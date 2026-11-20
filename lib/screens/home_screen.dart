import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../core/constants.dart';
import '../models/profile.dart';
import '../providers/chat_provider.dart';
import '../providers/friends_provider.dart';
import '../services/supabase_service.dart';
import '../widgets/notification_banner.dart';
import 'chat_screen.dart';
import 'friends_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  RealtimeChannel? _globalChannel;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<FriendsProvider>().loadFriendships();
      _setupGlobalMessageSubscription();
    });
  }

  void _setupGlobalMessageSubscription() {
    _globalChannel = SupabaseService.instance.subscribeToAllUserMessages((message) async {
      if (!mounted) return;
      final activeFriend = context.read<ChatProvider>().activeFriend;
      // If currently chatting with this friend, don't show the in-app banner
      if (activeFriend?.id == message.senderId) return;

      // Find sender profile from existing friends list or fetch from database
      final friends = context.read<FriendsProvider>().acceptedFriends;
      Profile? sender = friends.cast<Profile?>().firstWhere(
            (f) => f?.id == message.senderId,
            orElse: () => null,
          );

      sender ??= await SupabaseService.instance.getProfile(message.senderId);

      if (sender != null && mounted) {
        NotificationBanner.show(
          context,
          friend: sender,
          message: message,
          onTap: () {
            _openChat(sender!);
          },
        );
      }
    });
  }

  @override
  void dispose() {
    if (_globalChannel != null) {
      SupabaseService.instance.unsubscribe(_globalChannel!);
      _globalChannel = null;
    }
    NotificationBanner.dismiss();
    super.dispose();
  }

  void _openChat(Profile friend) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ChatScreen(friend: friend),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final titles = ['Chats', 'Friends', 'Profile'];

    return Scaffold(
      appBar: AppBar(
        title: Text(titles[_currentIndex]),
        elevation: 0,
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          _buildChatsTab(),
          FriendsScreen(
            isTab: true,
            onOpenChat: _openChat,
          ),
          const ProfileScreen(isTab: true),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline),
            selectedIcon: Icon(Icons.chat_bubble),
            label: 'Chats',
          ),
          NavigationDestination(
            icon: Icon(Icons.people_outline),
            selectedIcon: Icon(Icons.people),
            label: 'Friends',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildChatsTab() {
    final friendsProvider = context.watch<FriendsProvider>();
    final friends = friendsProvider.acceptedFriends;

    if (friendsProvider.isLoading && friends.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (friends.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.chat_bubble_outline,
                size: 64,
                color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.5),
              ),
              const SizedBox(height: 16),
              Text(
                'No chats yet.',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Add a friend from the Friends tab to start chatting.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 20),
              FilledButton.tonalIcon(
                icon: const Icon(Icons.person_add_outlined),
                label: const Text('Find Friends'),
                onPressed: () {
                  setState(() => _currentIndex = 1);
                },
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => friendsProvider.loadFriendships(),
      child: ListView.separated(
        itemCount: friends.length,
        separatorBuilder: (context, index) => const Divider(height: 1, indent: 72),
        itemBuilder: (context, index) {
          final friend = friends[index];
          final langName = friend.preferredLanguage != null
              ? AppConstants.getLanguageName(friend.preferredLanguage!)
              : 'Unknown';

          return ListTile(
            leading: CircleAvatar(
              radius: 24,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Text(
                (friend.displayName.isNotEmpty
                        ? friend.displayName[0]
                        : friend.username[0])
                    .toUpperCase(),
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            title: Text(
              friend.displayName.isNotEmpty ? friend.displayName : friend.username,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text(
              'Language: $langName',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: const Icon(Icons.arrow_forward_ios, size: 14),
            onTap: () => _openChat(friend),
          );
        },
      ),
    );
  }
}
