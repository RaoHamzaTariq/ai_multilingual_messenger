import 'package:flutter/material.dart';
import '../models/message.dart';
import '../services/supabase_service.dart';
import 'voice_message_bubble.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool isMe;
  final VoidCallback? onToggleOriginal;
  final VoidCallback? onTapImage;

  const MessageBubble({
    super.key,
    required this.message,
    required this.isMe,
    this.onToggleOriginal,
    this.onTapImage,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final bubbleBg = isMe
        ? colorScheme.primary
        : colorScheme.surfaceContainerHighest;
    final textColor = isMe
        ? colorScheme.onPrimary
        : colorScheme.onSurfaceVariant;

    final alignment = isMe ? Alignment.centerRight : Alignment.centerLeft;
    final borderRadius = BorderRadius.only(
      topLeft: const Radius.circular(16),
      topRight: const Radius.circular(16),
      bottomLeft: Radius.circular(isMe ? 16 : 4),
      bottomRight: Radius.circular(isMe ? 4 : 16),
    );

    return Align(
      alignment: alignment,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: bubbleBg,
          borderRadius: borderRadius,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          crossAxisAlignment:
              isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Message Body based on type
            if (message.type == 'text')
              _buildTextContent(context, textColor)
            else if (message.type == 'image')
              _buildImageContent(context)
            else if (message.type == 'voice')
              VoiceMessageBubble(message: message, isMe: isMe),

            const SizedBox(height: 4),

            // Time and status
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _formatTime(message.createdAt),
                  style: TextStyle(
                    fontSize: 10,
                    color: textColor.withValues(alpha: 0.7),
                  ),
                ),
                if (isMe) ...[
                  const SizedBox(width: 4),
                  Icon(
                    Icons.done_all,
                    size: 14,
                    color: message.isRead
                        ? const Color(0xFF4FC3F7)
                        : textColor.withValues(alpha: 0.5),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextContent(BuildContext context, Color textColor) {
    final translation = message.translation;
    final hasValidTranslation = !isMe &&
        translation != null &&
        translation.translatedText.isNotEmpty &&
        translation.translatedText != message.content;

    final displayText = (hasValidTranslation && !message.showOriginal)
        ? translation.translatedText
        : (message.content ?? '');

    return Column(
      crossAxisAlignment:
          isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: [
        // Translation loading indicator
        if (message.isTranslating)
          Padding(
            padding: const EdgeInsets.only(bottom: 4.0),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 10,
                  height: 10,
                  child: CircularProgressIndicator(
                    strokeWidth: 1.5,
                    color: textColor.withValues(alpha: 0.6),
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  'Translating...',
                  style: TextStyle(
                    fontSize: 11,
                    fontStyle: FontStyle.italic,
                    color: textColor.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ),
          ),

        // Main text
        Text(
          displayText,
          style: TextStyle(
            fontSize: 15,
            color: textColor,
          ),
        ),

        // "Translated" badge & "Show original" toggle
        if (hasValidTranslation) ...[
          const SizedBox(height: 6),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                decoration: BoxDecoration(
                  color: textColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  message.showOriginal ? 'Original' : 'Translated',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: textColor,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              InkWell(
                onTap: onToggleOriginal,
                child: Text(
                  message.showOriginal ? 'Show translated' : 'Show original',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    decoration: TextDecoration.underline,
                    color: textColor,
                  ),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildImageContent(BuildContext context) {
    if (message.mediaUrl == null || message.mediaUrl!.isEmpty) {
      return Container(
        width: 200,
        height: 150,
        color: Colors.black12,
        child: const Center(child: Icon(Icons.broken_image, size: 40)),
      );
    }

    return FutureBuilder<String>(
      future: SupabaseService.instance.getMediaUrl('chat-images', message.mediaUrl!),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return Container(
            width: 200,
            height: 150,
            color: Colors.black12,
            child: const Center(
              child: SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
          );
        }

        final imageUrl = snapshot.data!;
        return GestureDetector(
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => Scaffold(
                  backgroundColor: Colors.black,
                  appBar: AppBar(
                    backgroundColor: Colors.transparent,
                    foregroundColor: Colors.white,
                  ),
                  body: Center(
                    child: InteractiveViewer(
                      child: Image.network(
                        imageUrl,
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.network(
              imageUrl,
              width: 220,
              height: 180,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                width: 220,
                height: 180,
                color: Colors.black12,
                child: const Center(
                  child: Icon(Icons.broken_image, size: 40, color: Colors.grey),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  String _formatTime(DateTime? dt) {
    if (dt == null) return '';
    final local = dt.toLocal();
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
