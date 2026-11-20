import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import '../models/message.dart';
import '../services/supabase_service.dart';

class VoiceMessageBubble extends StatefulWidget {
  final Message message;
  final bool isMe;

  const VoiceMessageBubble({
    super.key,
    required this.message,
    required this.isMe,
  });

  @override
  State<VoiceMessageBubble> createState() => _VoiceMessageBubbleState();
}

class _VoiceMessageBubbleState extends State<VoiceMessageBubble> {
  final AudioPlayer _player = AudioPlayer();
  bool _isPlaying = false;
  bool _isLoading = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  @override
  void initState() {
    super.initState();
    _duration = Duration(seconds: widget.message.durationSeconds ?? 0);

    _player.onPlayerStateChanged.listen((state) {
      if (!mounted) return;
      setState(() {
        _isPlaying = state == PlayerState.playing;
        if (state == PlayerState.completed) {
          _position = Duration.zero;
        }
      });
    });

    _player.onPositionChanged.listen((pos) {
      if (!mounted) return;
      setState(() => _position = pos);
    });

    _player.onDurationChanged.listen((d) {
      if (!mounted) return;
      if (d.inSeconds > 0) {
        setState(() => _duration = d);
      }
    });
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  Future<void> _togglePlay() async {
    if (_isPlaying) {
      await _player.pause();
      return;
    }

    if (widget.message.mediaUrl == null) return;

    setState(() => _isLoading = true);
    try {
      final audioUrl = await SupabaseService.instance.getMediaUrl(
        'chat-voice',
        widget.message.mediaUrl!,
      );
      await _player.stop();
      await _player.play(UrlSource(audioUrl));
    } catch (_) {
      // Audio playback error handled gracefully
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final textColor = widget.isMe
        ? Theme.of(context).colorScheme.onPrimary
        : Theme.of(context).colorScheme.onSurfaceVariant;

    final maxSec = _duration.inSeconds > 0
        ? _duration.inSeconds
        : (widget.message.durationSeconds ?? 0);
    final curSec = _position.inSeconds;
    final progress = maxSec > 0 ? (curSec / maxSec).clamp(0.0, 1.0) : 0.0;

    return Column(
      crossAxisAlignment:
          widget.isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              iconSize: 28,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
              icon: _isLoading
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: textColor,
                      ),
                    )
                  : Icon(
                      _isPlaying
                          ? Icons.pause_circle_filled
                          : Icons.play_circle_filled,
                      color: textColor,
                    ),
              onPressed: _isLoading ? null : _togglePlay,
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 130,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: textColor.withValues(alpha: 0.2),
                    valueColor: AlwaysStoppedAnimation<Color>(textColor),
                    minHeight: 4,
                    borderRadius: BorderRadius.circular(2),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _formatDuration(curSec),
                        style: TextStyle(
                          fontSize: 10,
                          color: textColor.withValues(alpha: 0.8),
                        ),
                      ),
                      Text(
                        _formatDuration(maxSec),
                        style: TextStyle(
                          fontSize: 10,
                          color: textColor.withValues(alpha: 0.8),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),

        // Translating transcript indicator
        if (widget.message.isTranslating)
          Padding(
            padding: const EdgeInsets.only(top: 6.0),
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
                  'Transcribing & translating...',
                  style: TextStyle(
                    fontSize: 11,
                    fontStyle: FontStyle.italic,
                    color: textColor.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ),
          ),

        // Phase 3 Voice Transcript & Translation
        if (widget.message.translation?.transcript != null &&
            widget.message.translation!.transcript!.isNotEmpty) ...[
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: textColor.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  (widget.message.translation!.translatedText.isNotEmpty &&
                          !widget.message.showOriginal)
                      ? widget.message.translation!.translatedText
                      : widget.message.translation!.transcript!,
                  style: TextStyle(
                    fontSize: 13,
                    color: textColor,
                  ),
                ),
                if (widget.message.translation!.translatedText.isNotEmpty &&
                    widget.message.translation!.translatedText !=
                        widget.message.translation!.transcript) ...[
                  const SizedBox(height: 4),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(
                          color: textColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          widget.message.showOriginal
                              ? 'Original'
                              : 'Translated',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: textColor,
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      InkWell(
                        onTap: () {
                          setState(() {
                            widget.message.showOriginal =
                                !widget.message.showOriginal;
                          });
                        },
                        child: Text(
                          widget.message.showOriginal
                              ? 'Show translated'
                              : 'Show original',
                          style: TextStyle(
                            fontSize: 10,
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
            ),
          ),
        ],
      ],
    );
  }

  String _formatDuration(int totalSeconds) {
    final m = totalSeconds ~/ 60;
    final s = totalSeconds % 60;
    return '$m:${s.toString().padLeft(2, '0')}';
  }
}
