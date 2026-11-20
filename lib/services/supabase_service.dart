import 'dart:typed_data';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../core/constants.dart';
import '../models/profile.dart';
import '../models/friendship.dart';
import '../models/message.dart';
import '../models/translation.dart';

class SupabaseService {
  static final SupabaseService instance = SupabaseService._internal();
  SupabaseService._internal();

  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  SupabaseClient get client => Supabase.instance.client;
  User? get currentUser => _isInitialized ? client.auth.currentUser : null;
  Session? get currentSession => _isInitialized ? client.auth.currentSession : null;

  Future<void> initialize({bool? autoRefreshToken}) async {
    if (_isInitialized) return;
    if (!AppConfig.isConfigured) {
      _isInitialized = false;
      return;
    }
    try {
      await Supabase.initialize(
        url: AppConfig.supabaseUrl,
        // ignore: deprecated_member_use
        anonKey: AppConfig.supabaseAnonKey,
        authOptions: FlutterAuthClientOptions(
          autoRefreshToken: autoRefreshToken ?? true,
        ),
      );
      _isInitialized = true;
    } catch (_) {
      // If placeholder or offline, keep _isInitialized false
      _isInitialized = false;
    }
  }

  // --- Auth & Profiles ---

  Future<AuthResponse> signUp({
    required String email,
    required String password,
    required String username,
  }) async {
    final cleanUsername = username.trim().toLowerCase();

    // Sign up the auth user
    final response = await client.auth.signUp(
      email: email.trim(),
      password: password,
      data: {'username': cleanUsername},
    );

    final user = response.user;
    if (user != null) {
      if (response.session == null) {
        try {
          await client.auth.signInWithPassword(
            email: email.trim(),
            password: password,
          );
        } catch (_) {}
      }

      // Create initial profile row (also backed up by database trigger)
      try {
        await client.from('profiles').upsert({
          'id': user.id,
          'username': cleanUsername,
          'display_name': username.trim(),
          'preferred_language': null,
        });
      } catch (_) {}
    }

    return response;
  }

  Future<AuthResponse> signIn({
    required String email,
    required String password,
  }) async {
    return await client.auth.signInWithPassword(
      email: email.trim(),
      password: password,
    );
  }

  Future<void> signOut() async {
    await client.auth.signOut();
  }

  Future<Profile?> getProfile(String userId) async {
    final response = await client
        .from('profiles')
        .select()
        .eq('id', userId)
        .maybeSingle();

    if (response == null) return null;
    return Profile.fromMap(response);
  }

  Future<Profile?> searchProfileByUsername(String username) async {
    final clean = username.trim().toLowerCase();
    final response = await client
        .from('profiles')
        .select()
        .eq('username', clean)
        .maybeSingle();

    if (response == null) return null;
    return Profile.fromMap(response);
  }

  Future<void> updatePreferredLanguage(String userId, String languageCode) async {
    final existing = await getProfile(userId);
    if (existing != null) {
      await client.from('profiles').update({
        'preferred_language': languageCode,
      }).eq('id', userId);
    } else {
      final emailPrefix = currentUser?.email?.split('@').first ?? 'user';
      await client.from('profiles').upsert({
        'id': userId,
        'username': emailPrefix.toLowerCase(),
        'display_name': emailPrefix,
        'preferred_language': languageCode,
      });
    }
  }

  Future<void> updateDisplayName(String userId, String displayName) async {
    await client.from('profiles').update({
      'display_name': displayName.trim(),
    }).eq('id', userId);
  }

  // --- Friendships ---

  Future<Friendship> sendFriendRequest(String addresseeId) async {
    final myId = currentUser!.id;
    final response = await client.from('friendships').insert({
      'requester_id': myId,
      'addressee_id': addresseeId,
      'status': 'pending',
    }).select().single();

    return Friendship.fromMap(response);
  }

  Future<void> updateFriendshipStatus(String friendshipId, String status) async {
    await client.from('friendships').update({'status': status}).eq('id', friendshipId);
  }

  Future<List<Friendship>> getFriendships() async {
    final myId = currentUser?.id;
    if (myId == null) return [];

    final response = await client
        .from('friendships')
        .select()
        .or('requester_id.eq.$myId,addressee_id.eq.$myId')
        .order('created_at', ascending: false);

    final List<Friendship> list = [];
    for (final item in response) {
      final friendship = Friendship.fromMap(item);
      final otherId = friendship.requesterId == myId
          ? friendship.addresseeId
          : friendship.requesterId;
      final otherProf = await getProfile(otherId);
      list.add(Friendship.fromMap(item, otherProfile: otherProf));
    }
    return list;
  }

  // --- Messages ---

  Future<List<Message>> getMessages(String otherUserId) async {
    final myId = currentUser?.id;
    if (myId == null) return [];

    final response = await client
        .from('messages')
        .select()
        .or('and(sender_id.eq.$myId,receiver_id.eq.$otherUserId),and(sender_id.eq.$otherUserId,receiver_id.eq.$myId)')
        .order('created_at', ascending: true);

    return (response as List).map((m) => Message.fromMap(m)).toList();
  }

  Future<Message> sendMessage({
    required String receiverId,
    required String type,
    String? content,
    String? mediaUrl,
    int? durationSeconds,
  }) async {
    final myId = currentUser!.id;
    final response = await client.from('messages').insert({
      'sender_id': myId,
      'receiver_id': receiverId,
      'type': type,
      'content': content,
      'media_url': mediaUrl,
      'duration_seconds': durationSeconds,
    }).select().single();

    return Message.fromMap(response);
  }

  RealtimeChannel subscribeToMessages(
    String otherUserId,
    void Function(Message message) onMessage, {
    void Function(Message message)? onMessageUpdated,
  }) {
    final myId = currentUser?.id ?? '';
    final channel = client.channel('chat:$myId:$otherUserId');

    channel.onPostgresChanges(
      event: PostgresChangeEvent.all,
      schema: 'public',
      table: 'messages',
      callback: (payload) {
        final record = payload.newRecord;
        if (record.isNotEmpty) {
          final sender = record['sender_id'];
          final receiver = record['receiver_id'];
          if ((sender == myId && receiver == otherUserId) ||
              (sender == otherUserId && receiver == myId)) {
            final msg = Message.fromMap(record);
            if (payload.eventType == PostgresChangeEvent.insert) {
              onMessage(msg);
            } else if (payload.eventType == PostgresChangeEvent.update) {
              onMessageUpdated?.(msg);
            }
          }
        }
      },
    ).subscribe();

    return channel;
  }

  Future<void> markMessagesAsRead(String otherUserId) async {
    final myId = currentUser?.id;
    if (myId == null) return;

    try {
      await client
          .from('messages')
          .update({'is_read': true})
          .eq('sender_id', otherUserId)
          .eq('receiver_id', myId)
          .eq('is_read', false);
    } catch (_) {
      // Graceful fallback if is_read is not yet populated
    }
  }

  RealtimeChannel subscribeToAllUserMessages(
    void Function(Message message) onIncomingMessage,
  ) {
    final myId = currentUser?.id ?? '';
    final channel = client.channel('user-incoming-messages-global:$myId');

    channel.onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'messages',
      callback: (payload) {
        final newRecord = payload.newRecord;
        if (newRecord.isNotEmpty) {
          final receiver = newRecord['receiver_id'];
          if (receiver == myId) {
            onIncomingMessage(Message.fromMap(newRecord));
          }
        }
      },
    ).subscribe();

    return channel;
  }

  Future<void> unsubscribe(RealtimeChannel channel) async {
    await client.removeChannel(channel);
  }

  // --- Storage ---

  Future<String> uploadMedia({
    required String bucket,
    required String path,
    required Uint8List bytes,
    required String contentType,
  }) async {
    await client.storage.from(bucket).uploadBinary(
          path,
          bytes,
          fileOptions: FileOptions(contentType: contentType, upsert: true),
        );
    return path;
  }

  Future<String> getMediaUrl(String bucket, String path) async {
    try {
      final signedUrl =
          await client.storage.from(bucket).createSignedUrl(path, 60 * 60);
      return signedUrl;
    } catch (_) {
      return client.storage.from(bucket).getPublicUrl(path);
    }
  }

  // --- Translations cache check ---

  Future<Translation?> getCachedTranslation(
    String messageId,
    String targetLanguage,
  ) async {
    final response = await client
        .from('translations')
        .select()
        .eq('message_id', messageId)
        .eq('target_language', targetLanguage)
        .maybeSingle();

    if (response == null) return null;
    return Translation.fromMap(response);
  }
}
