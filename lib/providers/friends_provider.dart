import 'package:flutter/foundation.dart';
import '../models/friendship.dart';
import '../models/profile.dart';
import '../services/supabase_service.dart';

class FriendsProvider extends ChangeNotifier {
  List<Friendship> _friendships = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<Friendship> get friendships => _friendships;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  String? get currentUserId => SupabaseService.instance.currentUser?.id;

  // Accepted friends: profiles of other users in accepted friendships
  List<Profile> get acceptedFriends {
    final myId = currentUserId;
    if (myId == null) return [];
    return _friendships
        .where((f) => f.status == 'accepted' && f.otherProfile != null)
        .map((f) => f.otherProfile!)
        .toList();
  }

  // Pending incoming requests (sent to current user)
  List<Friendship> get pendingRequests {
    final myId = currentUserId;
    if (myId == null) return [];
    return _friendships
        .where((f) => f.status == 'pending' && f.addresseeId == myId)
        .toList();
  }

  // Pending outgoing requests (sent by current user)
  List<Friendship> get sentRequests {
    final myId = currentUserId;
    if (myId == null) return [];
    return _friendships
        .where((f) => f.status == 'pending' && f.requesterId == myId)
        .toList();
  }

  Future<void> loadFriendships() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _friendships = await SupabaseService.instance.getFriendships();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> sendRequest(String username) async {
    final clean = username.trim().toLowerCase();
    if (clean.isEmpty) {
      _errorMessage = 'Please enter a username';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final myId = currentUserId;
      if (myId == null) throw Exception('Not logged in');

      final targetProfile =
          await SupabaseService.instance.searchProfileByUsername(clean);
      if (targetProfile == null) {
        throw Exception('User "@$clean" not found');
      }

      if (targetProfile.id == myId) {
        throw Exception('You cannot add yourself as a friend');
      }

      final alreadyExists = _friendships.any((f) =>
          (f.requesterId == targetProfile.id || f.addresseeId == targetProfile.id) &&
          f.status != 'rejected');
      if (alreadyExists) {
        throw Exception('A friend request with @$clean is already active or accepted');
      }

      await SupabaseService.instance.sendFriendRequest(targetProfile.id);
      await loadFriendships();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> acceptRequest(String friendshipId) async {
    try {
      await SupabaseService.instance.updateFriendshipStatus(friendshipId, 'accepted');
      await loadFriendships();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> rejectRequest(String friendshipId) async {
    try {
      await SupabaseService.instance.updateFriendshipStatus(friendshipId, 'rejected');
      await loadFriendships();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}
