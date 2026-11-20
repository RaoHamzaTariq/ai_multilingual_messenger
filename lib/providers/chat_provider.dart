import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/message.dart';
import '../models/profile.dart';
import '../services/supabase_service.dart';
import '../services/translation_service.dart';

class ChatProvider extends ChangeNotifier {
  Profile? _activeFriend;
  List<Message> _messages = [];
  bool _isLoading = false;
  String? _errorMessage;
  RealtimeChannel? _channel;

  Profile? get activeFriend => _activeFriend;
  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  String? get currentUserId => SupabaseService.instance.currentUser?.id;

  void clearActiveChat() {
    _activeFriend = null;
    if (_channel != null) {
      SupabaseService.instance.unsubscribe(_channel!);
      _channel = null;
    }
  }

  Future<void> initChat({
    required Profile friend,
    required String userLanguage,
  }) async {
    _activeFriend = friend;
    _messages = [];
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    // Clean up previous subscription if any
    if (_channel != null) {
      await SupabaseService.instance.unsubscribe(_channel!);
      _channel = null;
    }

    try {
      // 1. Fetch historical messages
      _messages = await SupabaseService.instance.getMessages(friend.id);

      // 2. Translate any received messages that need translation
      for (final msg in _messages) {
        if (msg.senderId != currentUserId) {
          if (msg.type == 'text' && msg.content != null) {
            _translateMessage(msg, userLanguage);
          } else if (msg.type == 'voice' && msg.mediaUrl != null) {
            _translateVoiceMessage(msg, userLanguage);
          }
        }
      }

      // 3. Mark incoming unread messages as read
      await SupabaseService.instance.markMessagesAsRead(friend.id);

      // 4. Subscribe to realtime new messages & updates
      _channel = SupabaseService.instance.subscribeToMessages(
        friend.id,
        (newMessage) {
          _handleIncomingMessage(newMessage, userLanguage);
        },
        onMessageUpdated: (updatedMessage) {
          _handleMessageUpdated(updatedMessage);
        },
      );
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _handleIncomingMessage(Message newMessage, String userLanguage) {
    // Avoid duplicate insertions
    final exists = _messages.any((m) => m.id == newMessage.id);
    if (exists) return;

    _messages.add(newMessage);
    notifyListeners();

    // If incoming message, mark as read and trigger translation
    if (newMessage.senderId != currentUserId) {
      SupabaseService.instance.markMessagesAsRead(newMessage.senderId);
      if (newMessage.type == 'text' && newMessage.content != null) {
        _translateMessage(newMessage, userLanguage);
      } else if (newMessage.type == 'voice' && newMessage.mediaUrl != null) {
        _translateVoiceMessage(newMessage, userLanguage);
      }
    }
  }

  void _handleMessageUpdated(Message updatedMessage) {
    final index = _messages.indexWhere((m) => m.id == updatedMessage.id);
    if (index != -1) {
      final old = _messages[index];
      updatedMessage.translation = old.translation;
      updatedMessage.showOriginal = old.showOriginal;
      updatedMessage.isTranslating = old.isTranslating;
      _messages[index] = updatedMessage;
      notifyListeners();
    }
  }

  Future<void> _translateVoiceMessage(Message message, String targetLanguage) async {
    if (message.mediaUrl == null || message.mediaUrl!.trim().isEmpty) return;

    message.isTranslating = true;
    notifyListeners();

    try {
      final translation = await TranslationService.instance.translateVoice(
        messageId: message.id,
        audioPath: message.mediaUrl!,
        targetLanguage: targetLanguage,
      );
      if (translation != null) {
        message.translation = translation;
      }
    } catch (_) {
      // Keep translation null; fallback to audio player
    } finally {
      message.isTranslating = false;
      notifyListeners();
    }
  }

  Future<void> _translateMessage(Message message, String targetLanguage) async {
    if (message.content == null || message.content!.trim().isEmpty) return;

    message.isTranslating = true;
    notifyListeners();

    try {
      final translation = await TranslationService.instance.translateText(
        messageId: message.id,
        text: message.content!,
        targetLanguage: targetLanguage,
      );
      message.translation = translation;
    } catch (_) {
      // Translation failure keeps translation null; falls back to message.content
    } finally {
      message.isTranslating = false;
      notifyListeners();
    }
  }

  Future<bool> sendTextMessage({
    required String content,
    required String userLanguage,
  }) async {
    final text = content.trim();
    if (text.isEmpty || _activeFriend == null) return false;

    try {
      final msg = await SupabaseService.instance.sendMessage(
        receiverId: _activeFriend!.id,
        type: 'text',
        content: text,
      );

      // If realtime hasn't added it yet, add locally
      if (!_messages.any((m) => m.id == msg.id)) {
        _messages.add(msg);
        notifyListeners();
      }
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> sendVoiceMessage({
    required Uint8List bytes,
    required int durationSeconds,
  }) async {
    if (_activeFriend == null) return false;

    try {
      final ext = kIsWeb ? 'webm' : 'm4a';
      final mimeType = kIsWeb ? 'audio/webm' : 'audio/m4a';
      final fileName =
          'voice_${DateTime.now().millisecondsSinceEpoch}.$ext';
      final path = '${_activeFriend!.id}/$fileName';

      await SupabaseService.instance.uploadMedia(
        bucket: 'chat-voice',
        path: path,
        bytes: bytes,
        contentType: mimeType,
      );

      final msg = await SupabaseService.instance.sendMessage(
        receiverId: _activeFriend!.id,
        type: 'voice',
        mediaUrl: path,
        durationSeconds: durationSeconds,
      );

      if (!_messages.any((m) => m.id == msg.id)) {
        _messages.add(msg);
        notifyListeners();
      }
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> sendImageMessage({
    required Uint8List bytes,
    required String fileName,
  }) async {
    if (_activeFriend == null) return false;

    try {
      final ext = fileName.split('.').last.toLowerCase();
      final mimeType = ext == 'png' ? 'image/png' : 'image/jpeg';
      final path =
          '${_activeFriend!.id}/${DateTime.now().millisecondsSinceEpoch}_$fileName';

      await SupabaseService.instance.uploadMedia(
        bucket: 'chat-images',
        path: path,
        bytes: bytes,
        contentType: mimeType,
      );

      final msg = await SupabaseService.instance.sendMessage(
        receiverId: _activeFriend!.id,
        type: 'image',
        mediaUrl: path,
      );

      if (!_messages.any((m) => m.id == msg.id)) {
        _messages.add(msg);
        notifyListeners();
      }
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  void toggleShowOriginal(String messageId) {
    final index = _messages.indexWhere((m) => m.id == messageId);
    if (index != -1) {
      _messages[index].showOriginal = !_messages[index].showOriginal;
      notifyListeners();
    }
  }

  void addMessageLocally(Message msg) {
    if (!_messages.any((m) => m.id == msg.id)) {
      _messages.add(msg);
      notifyListeners();
    }
  }

  Future<void> closeChat() async {
    if (_channel != null) {
      await SupabaseService.instance.unsubscribe(_channel!);
      _channel = null;
    }
    _activeFriend = null;
    _messages = [];
  }

  @override
  void dispose() {
    if (_channel != null) {
      SupabaseService.instance.unsubscribe(_channel!);
    }
    super.dispose();
  }
}
