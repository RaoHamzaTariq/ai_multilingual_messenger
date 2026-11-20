class Profile {
  final String id;
  final String username;
  final String displayName;
  final String? preferredLanguage;
  final DateTime? createdAt;

  Profile({
    required this.id,
    required this.username,
    required this.displayName,
    this.preferredLanguage,
    this.createdAt,
  });

  factory Profile.fromMap(Map<String, dynamic> map) {
    return Profile(
      id: map['id'] as String,
      username: map['username'] as String? ?? '',
      displayName: map['display_name'] as String? ?? '',
      preferredLanguage: map['preferred_language'] as String?,
      createdAt: map['created_at'] != null ? DateTime.tryParse(map['created_at'].toString()) : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'username': username.toLowerCase(),
      'display_name': displayName,
      'preferred_language': preferredLanguage,
    };
  }

  Profile copyWith({
    String? username,
    String? displayName,
    String? preferredLanguage,
  }) {
    return Profile(
      id: id,
      username: username ?? this.username,
      displayName: displayName ?? this.displayName,
      preferredLanguage: preferredLanguage ?? this.preferredLanguage,
      createdAt: createdAt,
    );
  }
}
