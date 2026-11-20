import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/constants.dart';
import '../models/friendship.dart';
import '../models/profile.dart';
import '../providers/friends_provider.dart';

class FriendsScreen extends StatefulWidget {
  final bool isTab;
  final void Function(Profile friend)? onOpenChat;

  const FriendsScreen({
    super.key,
    this.isTab = false,
    this.onOpenChat,
  });

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen> {
  final _usernameController = TextEditingController();
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<FriendsProvider>().loadFriendships();
    });
  }

  @override
  void dispose() {
    _usernameController.dispose();
    super.dispose();
  }

  Future<void> _handleSendRequest() async {
    final text = _usernameController.text.trim();
    if (text.isEmpty) return;

    setState(() => _isSending = true);
    final provider = context.read<FriendsProvider>();
    final success = await provider.sendRequest(text);
    setState(() => _isSending = false);

    if (!mounted) return;

    if (success) {
      _usernameController.clear();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Friend request sent to @$text!')),
      );
    } else {
      final error = provider.errorMessage ?? 'Could not send friend request.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error), backgroundColor: Colors.red.shade700),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<FriendsProvider>();
    final pending = provider.pendingRequests;
    final friends = provider.acceptedFriends;

    final body = RefreshIndicator(
      onRefresh: () => provider.loadFriendships(),
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // 1. Add friend by username
          Card(
            elevation: 0,
            color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 8.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _usernameController,
                      decoration: const InputDecoration(
                        hintText: 'Enter username to add...',
                        border: InputBorder.none,
                        isDense: true,
                        prefixText: '@',
                      ),
                      onSubmitted: (_) => _handleSendRequest(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _isSending ? null : _handleSendRequest,
                    child: _isSending
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Add'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // 2. Pending requests
          if (pending.isNotEmpty) ...[
            Text(
              'Friend Requests (${pending.length})',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            ...pending.map((req) => _buildPendingRequestItem(req)),
            const SizedBox(height: 20),
          ],

          // 3. Accepted friends
          Text(
            'Friends (${friends.length})',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),

          if (provider.isLoading && friends.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32.0),
                child: CircularProgressIndicator(),
              ),
            )
          else if (friends.isEmpty)
            Padding(
              padding: const EdgeInsets.all(32.0),
              child: Center(
                child: Text(
                  'No friends yet.\nAdd a friend by username above to get started.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ),
            )
          else
            ...friends.map((friend) => _buildFriendItem(friend)),
        ],
      ),
    );

    if (widget.isTab) {
      return body;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Friends')),
      body: body,
    );
  }

  Widget _buildPendingRequestItem(Friendship req) {
    final profile = req.otherProfile;
    final name = profile?.displayName.isNotEmpty == true
        ? profile!.displayName
        : profile?.username ?? 'User';
    final username = profile?.username ?? 'unknown';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 1,
      child: ListTile(
        leading: CircleAvatar(
          child: Text(name[0].toUpperCase()),
        ),
        title: Text(name),
        subtitle: Text('@$username'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.check_circle, color: Colors.green),
              tooltip: 'Accept',
              onPressed: () =>
                  context.read<FriendsProvider>().acceptRequest(req.id),
            ),
            IconButton(
              icon: const Icon(Icons.cancel, color: Colors.red),
              tooltip: 'Reject',
              onPressed: () =>
                  context.read<FriendsProvider>().rejectRequest(req.id),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFriendItem(Profile friend) {
    final langName = friend.preferredLanguage != null
        ? AppConstants.getLanguageName(friend.preferredLanguage!)
        : 'Unknown';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerLow,
      child: ListTile(
        leading: CircleAvatar(
          child: Text(
            (friend.displayName.isNotEmpty
                    ? friend.displayName[0]
                    : friend.username[0])
                .toUpperCase(),
          ),
        ),
        title: Text(
          friend.displayName.isNotEmpty ? friend.displayName : friend.username,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text('@${friend.username} • $langName'),
        trailing: const Icon(Icons.chat_bubble_outline, size: 20),
        onTap: () {
          if (widget.onOpenChat != null) {
            widget.onOpenChat!(friend);
          }
        },
      ),
    );
  }
}
