import 'package:flutter/material.dart';
import '../models/message.dart';
import '../models/profile.dart';

class SearchScreen extends StatefulWidget {
  final List<Message> messages;
  final String myId;
  final Profile friend;

  const SearchScreen({
    super.key,
    required this.messages,
    required this.myId,
    required this.friend,
  });

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  List<Message> _filteredMessages = [];
  String _query = '';

  @override
  void initState() {
    super.initState();
    _filteredMessages = widget.messages;
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    setState(() {
      _query = query.trim().toLowerCase();
      if (_query.isEmpty) {
        _filteredMessages = widget.messages;
      } else {
        _filteredMessages = widget.messages.where((msg) {
          // Check text content
          if (msg.content?.toLowerCase().contains(_query) == true) {
            return true;
          }
          // Check translated text
          if (msg.translation?.translatedText.toLowerCase().contains(_query) == true) {
            return true;
          }
          // Check voice transcript
          if (msg.translation?.transcript?.toLowerCase().contains(_query) == true) {
            return true;
          }
          // Check image type query
          if (msg.type == 'image' && 'image'.contains(_query)) {
            return true;
          }
          return false;
        }).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final friendName = widget.friend.displayName.isNotEmpty
        ? widget.friend.displayName
        : widget.friend.username;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: TextField(
          controller: _searchController,
          autofocus: true,
          decoration: InputDecoration(
            hintText: 'Search in conversation...',
            border: InputBorder.none,
            hintStyle: TextStyle(color: theme.colorScheme.onSurfaceVariant),
          ),
          onChanged: _onSearchChanged,
        ),
        actions: [
          if (_query.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.clear),
              onPressed: () {
                _searchController.clear();
                _onSearchChanged('');
              },
            ),
        ],
      ),
      body: _filteredMessages.isEmpty
          ? Center(
              child: Text(
                _query.isEmpty
                    ? 'No messages in this chat.'
                    : 'No messages matching "$_query"',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            )
          : ListView.separated(
              itemCount: _filteredMessages.length,
              separatorBuilder: (context, index) => const Divider(height: 1, indent: 16, endIndent: 16),
              itemBuilder: (context, index) {
                final msg = _filteredMessages[index];
                final isMe = msg.senderId == widget.myId;
                final senderLabel = isMe ? 'You' : friendName;

                String displayPreview = '';
                IconData icon = Icons.chat_bubble_outline;

                if (msg.type == 'text') {
                  final translation = msg.translation?.translatedText;
                  if (translation != null && translation.isNotEmpty) {
                    displayPreview = translation;
                  } else {
                    displayPreview = msg.content ?? '';
                  }
                  icon = Icons.message_outlined;
                } else if (msg.type == 'image') {
                  displayPreview = 'Photo attachment';
                  icon = Icons.image_outlined;
                } else if (msg.type == 'voice') {
                  final transcript = msg.translation?.transcript ??
                      msg.translation?.translatedText;
                  if (transcript != null && transcript.isNotEmpty) {
                    displayPreview = 'Voice: "$transcript"';
                  } else {
                    displayPreview = 'Voice note (${msg.durationSeconds ?? 0}s)';
                  }
                  icon = Icons.mic_outlined;
                }

                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: isMe
                        ? theme.colorScheme.primaryContainer
                        : theme.colorScheme.surfaceContainerHighest,
                    child: Icon(icon, size: 20, color: isMe ? theme.colorScheme.primary : theme.colorScheme.onSurfaceVariant),
                  ),
                  title: Text(
                    senderLabel,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  subtitle: Text(
                    displayPreview,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 14),
                  ),
                  trailing: Text(
                    _formatTime(msg.createdAt),
                    style: TextStyle(
                      fontSize: 11,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  onTap: () {
                    Navigator.of(context).pop(msg.id);
                  },
                );
              },
            ),
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
