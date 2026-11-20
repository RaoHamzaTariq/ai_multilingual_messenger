import 'dart:async';
import 'package:flutter/material.dart';
import '../models/message.dart';
import '../models/profile.dart';

class NotificationBanner {
  static OverlayEntry? _currentEntry;
  static Timer? _dismissTimer;

  static void show(
    BuildContext context, {
    required Profile friend,
    required Message message,
    required VoidCallback onTap,
  }) {
    dismiss();

    final overlay = Overlay.maybeOf(context);
    if (overlay == null) return;

    final entry = OverlayEntry(
      builder: (context) => _BannerWidget(
        friend: friend,
        message: message,
        onTap: () {
          dismiss();
          onTap();
        },
        onDismiss: dismiss,
      ),
    );

    _currentEntry = entry;
    overlay.insert(entry);

    // Auto-dismiss after 3.5 seconds
    _dismissTimer = Timer(const Duration(milliseconds: 3500), () {
      dismiss();
    });
  }

  static void dismiss() {
    _dismissTimer?.cancel();
    _dismissTimer = null;
    _currentEntry?.remove();
    _currentEntry = null;
  }
}

class _BannerWidget extends StatefulWidget {
  final Profile friend;
  final Message message;
  final VoidCallback onTap;
  final VoidCallback onDismiss;

  const _BannerWidget({
    required this.friend,
    required this.message,
    required this.onTap,
    required this.onDismiss,
  });

  @override
  State<_BannerWidget> createState() => _BannerWidgetState();
}

class _BannerWidgetState extends State<_BannerWidget>
    with SingleTickerProviderStateMixin {
  late final AnimationController _animController;
  late final Animation<Offset> _slideAnimation;
  late final Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -0.6),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOutCubic,
    ));

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeIn),
    );

    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final friendName = widget.friend.displayName.isNotEmpty
        ? widget.friend.displayName
        : widget.friend.username;

    String preview = '';
    IconData icon = Icons.message_outlined;

    if (widget.message.type == 'text') {
      preview = widget.message.content ?? '';
      icon = Icons.chat_bubble_outline;
    } else if (widget.message.type == 'image') {
      preview = 'Photo attachment';
      icon = Icons.image_outlined;
    } else if (widget.message.type == 'voice') {
      preview = 'Voice note (${widget.message.durationSeconds ?? 0}s)';
      icon = Icons.mic_outlined;
    }

    final topPadding = MediaQuery.of(context).padding.top;

    return Positioned(
      top: topPadding + 10,
      left: 16,
      right: 16,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Material(
            elevation: 8,
            borderRadius: BorderRadius.circular(16),
            color: theme.colorScheme.surfaceContainerHighest,
            shadowColor: Colors.black.withValues(alpha: 0.25),
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: widget.onTap,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: theme.colorScheme.primary.withValues(alpha: 0.2),
                    width: 1,
                  ),
                ),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: theme.colorScheme.primary,
                      child: Text(
                        friendName.isNotEmpty ? friendName[0].toUpperCase() : '?',
                        style: TextStyle(
                          color: theme.colorScheme.onPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Row(
                            children: [
                              Text(
                                friendName,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(width: 6),
                              Icon(icon, size: 14, color: theme.colorScheme.primary),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            preview,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontSize: 13,
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      color: theme.colorScheme.onSurfaceVariant,
                      onPressed: widget.onDismiss,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
