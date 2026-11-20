import 'profile.dart';

class Friendship {
  final String id;
  final String requesterId;
  final String addresseeId;
  final String status; // 'pending', 'accepted', 'rejected'
  final DateTime? createdAt;
  final Profile? otherProfile; // Helper profile for UI

  Friendship({
    required this.id,
    required this.requesterId,
    required this.addresseeId,
    required this.status,
    this.createdAt,
    this.otherProfile,
  });

  factory Friendship.fromMap(Map<String, dynamic> map, {Profile? otherProfile}) {
    return Friendship(
      id: map['id'] as String,
      requesterId: map['requester_id'] as String,
      addresseeId: map['addressee_id'] as String,
      status: map['status'] as String? ?? 'pending',
      createdAt: map['created_at'] != null
          ? DateTime.tryParse(map['created_at'].toString())
          : null,
      otherProfile: otherProfile,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'requester_id': requesterId,
      'addressee_id': addresseeId,
      'status': status,
    };
  }
}
