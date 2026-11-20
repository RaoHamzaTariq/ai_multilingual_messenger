import 'translation.dart';

class Message {
  final String id;
  final String senderId;
  final String receiverId;
  final String type; // 'text', 'image', 'voice'
  final String? content;
  final String? mediaUrl;
  final int? durationSeconds;
  final DateTime? createdAt;
  final bool isRead;

  // Local helper state for UI display
  Translation? translation;
  bool showOriginal;
  bool isTranslating;

  Message({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.type,
    this.content,
    this.mediaUrl,
    this.durationSeconds,
    this.createdAt,
    this.isRead = false,
    this.translation,
    this.showOriginal = false,
    this.isTranslating = false,
  });

  factory Message.fromMap(Map<String, dynamic> map) {
    return Message(
      id: map['id'] as String,
      senderId: map['sender_id'] as String,
      receiverId: map['receiver_id'] as String,
      type: map['type'] as String? ?? 'text',
      content: map['content'] as String?,
      mediaUrl: map['media_url'] as String?,
      durationSeconds: map['duration_seconds'] as int?,
      createdAt: map['created_at'] != null
          ? DateTime.tryParse(map['created_at'].toString())
          : null,
      isRead: (map['is_read'] as bool?) ?? false,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'type': type,
      'content': content,
      'media_url': mediaUrl,
      'duration_seconds': durationSeconds,
      'is_read': isRead,
    };
  }
}
