import 'package:flutter/material.dart';

class ChatInputBar extends StatefulWidget {
  final Function(String text) onSendText;
  final VoidCallback? onPickImage;
  final VoidCallback? onRecordVoice;
  final bool isRecording;
  final int recordingSeconds;

  const ChatInputBar({
    super.key,
    required this.onSendText,
    this.onPickImage,
    this.onRecordVoice,
    this.isRecording = false,
    this.recordingSeconds = 0,
  });

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final _controller = TextEditingController();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      final has = _controller.text.trim().isNotEmpty;
      if (has != _hasText) {
        setState(() => _hasText = has);
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    widget.onSendText(text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // If recording voice note, show simple recording banner
    if (widget.isRecording) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        color: theme.colorScheme.errorContainer.withValues(alpha: 0.3),
        child: Row(
          children: [
            const Icon(Icons.fiber_manual_record, color: Colors.red, size: 20),
            const SizedBox(width: 8),
            Text(
              'Recording: ${widget.recordingSeconds}s / 60s',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.error,
              ),
            ),
            const Spacer(),
            TextButton(
              onPressed: widget.onRecordVoice,
              child: const Text('Stop & Send'),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          top: BorderSide(
            color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
            width: 0.5,
          ),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            // Image picker button
            IconButton(
              icon: const Icon(Icons.image_outlined),
              tooltip: 'Send Image (max 1 MB)',
              onPressed: widget.onPickImage,
            ),

            // Voice record button
            IconButton(
              icon: const Icon(Icons.mic_none_outlined),
              tooltip: 'Record Voice (max 60s)',
              onPressed: widget.onRecordVoice,
            ),

            // Text input field
            Expanded(
              child: TextField(
                controller: _controller,
                textCapitalization: TextCapitalization.sentences,
                decoration: InputDecoration(
                  hintText: 'Type a message...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24.0),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 10.0,
                  ),
                  isDense: true,
                ),
                maxLines: null,
                keyboardType: TextInputType.multiline,
                onSubmitted: (_) => _submit(),
              ),
            ),

            const SizedBox(width: 6),

            // Send button
            IconButton.filled(
              icon: const Icon(Icons.send_rounded, size: 18),
              onPressed: _hasText ? _submit : null,
            ),
          ],
        ),
      ),
    );
  }
}
