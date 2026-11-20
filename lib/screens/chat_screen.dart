import 'dart:async';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../core/constants.dart';
import '../models/profile.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../services/audio_service.dart';
import '../widgets/chat_input_bar.dart';
import '../widgets/message_bubble.dart';
import 'search_screen.dart';

class ChatScreen extends StatefulWidget {
  final Profile friend;

  const ChatScreen({
    super.key,
    required this.friend,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _scrollController = ScrollController();
  bool _isRecording = false;
  int _recordingSeconds = 0;
  int _previousMessageCount = 0;
  Timer? _recordTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final myLang = context.read<AuthProvider>().profile?.preferredLanguage ?? 'en';
      context.read<ChatProvider>().initChat(
            friend: widget.friend,
            userLanguage: myLang,
          );
    });
  }

  @override
  void dispose() {
    _recordTimer?.cancel();
    _scrollController.dispose();
    context.read<ChatProvider>().clearActiveChat();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      });
    }
  }

  void _scrollToMessage(String id) {
    final messages = context.read<ChatProvider>().messages;
    final index = messages.indexWhere((m) => m.id == id);
    if (index != -1 && _scrollController.hasClients) {
      final total = messages.length;
      if (total > 0) {
        final target = (index / total) * _scrollController.position.maxScrollExtent;
        _scrollController.animateTo(
          target.clamp(0.0, _scrollController.position.maxScrollExtent),
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeInOut,
        );
      }
    }
  }

  Future<void> _toggleVoiceRecording() async {
    if (_isRecording) {
      await _stopAndSendVoice();
    } else {
      try {
        final hasPerm = await AudioService.instance.hasPermission();
        if (!hasPerm) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Microphone permission is required to record voice notes.')),
          );
          return;
        }

        final started = await AudioService.instance.startRecording();
        if (!started) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Could not start recording audio.')),
          );
          return;
        }

        setState(() {
          _isRecording = true;
          _recordingSeconds = 0;
        });

        _recordTimer?.cancel();
        _recordTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
          if (!mounted) {
            timer.cancel();
            return;
          }
          setState(() {
            _recordingSeconds++;
          });

          // Auto-stop at 60 seconds limit
          if (_recordingSeconds >= AppConstants.maxVoiceDurationSeconds) {
            timer.cancel();
            _stopAndSendVoice();
          }
        });
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Recording error: $e')),
        );
      }
    }
  }

  Future<void> _stopAndSendVoice() async {
    _recordTimer?.cancel();
    final duration = _recordingSeconds;

    setState(() {
      _isRecording = false;
      _recordingSeconds = 0;
    });

    final bytes = await AudioService.instance.stopRecordingAndGetBytes();
    if (bytes == null || duration <= 0) return;

    try {
      if (!mounted) return;
      final ok = await context.read<ChatProvider>().sendVoiceMessage(
            bytes: bytes,
            durationSeconds: duration,
          );
      if (ok) {
        _scrollToBottom();
      } else {
        if (!mounted) return;
        final error = context.read<ChatProvider>().errorMessage ??
            'Failed to send voice note.';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error)),
        );
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to send voice note.')),
      );
    }
  }

  Future<void> _pickAndSendImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null || !mounted) return;

    final bytes = await picked.readAsBytes();
    if (!mounted) return;

    if (bytes.lengthInBytes > AppConstants.maxImageSizeBytes) {
      final sizeMb = (bytes.lengthInBytes / (1024 * 1024)).toStringAsFixed(2);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Image exceeds the 1 MB limit ($sizeMb MB). Please choose a smaller image.',
          ),
          backgroundColor: Colors.red.shade700,
        ),
      );
      return;
    }

    final chatProvider = context.read<ChatProvider>();
    final ok = await chatProvider.sendImageMessage(
      bytes: bytes,
      fileName: picked.name,
    );

    if (ok) {
      _scrollToBottom();
    } else {
      if (!mounted) return;
      final error = chatProvider.errorMessage ?? 'Failed to upload image.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error), backgroundColor: Colors.red.shade700),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatProvider = context.watch<ChatProvider>();
    final authProvider = context.watch<AuthProvider>();
    final myId = authProvider.profile?.id ?? '';
    final myLang = authProvider.profile?.preferredLanguage ?? 'en';

    final messages = chatProvider.messages;
    final friendName = widget.friend.displayName.isNotEmpty
        ? widget.friend.displayName
        : widget.friend.username;
    final friendLang = widget.friend.preferredLanguage != null
        ? AppConstants.getLanguageName(widget.friend.preferredLanguage!)
        : 'Unknown';

    // Auto-scroll on new messages
    if (messages.length > _previousMessageCount) {
      _previousMessageCount = messages.length;
      _scrollToBottom();
    }

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Text(
                friendName[0].toUpperCase(),
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontSize: 14,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    friendName,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    'Speaks: $friendLang',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 11),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: 'Search messages',
            onPressed: () async {
              final selectedId = await Navigator.of(context).push<String>(
                MaterialPageRoute(
                  builder: (_) => SearchScreen(
                    messages: messages,
                    myId: myId,
                    friend: widget.friend,
                  ),
                ),
              );
              if (selectedId != null && mounted) {
                _scrollToMessage(selectedId);
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: chatProvider.isLoading && messages.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : messages.isEmpty
                    ? Center(
                        child: Text(
                          'Say hello to $friendName!\nMessages will automatically be translated.',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Theme.of(context).colorScheme.onSurfaceVariant,
                              ),
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        itemCount: messages.length,
                        itemBuilder: (context, index) {
                          final message = messages[index];
                          return MessageBubble(
                            message: message,
                            isMe: message.senderId == myId,
                            onToggleOriginal: () {
                              chatProvider.toggleShowOriginal(message.id);
                            },
                          );
                        },
                      ),
          ),
          ChatInputBar(
            onPickImage: _pickAndSendImage,
            onRecordVoice: _toggleVoiceRecording,
            isRecording: _isRecording,
            recordingSeconds: _recordingSeconds,
            onSendText: (text) async {
              final ok = await chatProvider.sendTextMessage(
                content: text,
                userLanguage: myLang,
              );
              if (ok) {
                _scrollToBottom();
              }
            },
          ),
        ],
      ),
    );
  }
}
