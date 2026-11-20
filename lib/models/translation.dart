class Translation {
  final String id;
  final String messageId;
  final String targetLanguage;
  final String detectedLanguage;
  final String? transcript;
  final String translatedText;
  final DateTime? createdAt;

  Translation({
    required this.id,
    required this.messageId,
    required this.targetLanguage,
    required this.detectedLanguage,
    this.transcript,
    required this.translatedText,
    this.createdAt,
  });

  factory Translation.fromMap(Map<String, dynamic> map) {
    return Translation(
      id: map['id']?.toString() ?? '',
      messageId: map['message_id']?.toString() ?? '',
      targetLanguage: map['target_language']?.toString() ?? '',
      detectedLanguage: map['detected_language']?.toString() ?? '',
      transcript: map['transcript']?.toString(),
      translatedText: map['translated_text']?.toString() ?? '',
      createdAt: map['created_at'] != null
          ? DateTime.tryParse(map['created_at'].toString())
          : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'message_id': messageId,
      'target_language': targetLanguage,
      'detected_language': detectedLanguage,
      'transcript': transcript,
      'translated_text': translatedText,
    };
  }
}
