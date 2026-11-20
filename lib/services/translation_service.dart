import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/translation.dart';
import 'supabase_service.dart';

class TranslationService {
  static final TranslationService instance = TranslationService._internal();
  TranslationService._internal();

  /// Translates text into [targetLanguage].
  /// Checks Supabase cache first. Falls back to original [text] on any error.
  Future<Translation> translateText({
    required String messageId,
    required String text,
    required String targetLanguage,
  }) async {
    final cleanText = text.trim();

    // 1. If text is empty, return immediate fallback
    if (cleanText.isEmpty) {
      return Translation(
        id: '',
        messageId: messageId,
        targetLanguage: targetLanguage,
        detectedLanguage: targetLanguage,
        translatedText: text,
      );
    }

    // 2. Check local/Supabase translations table cache
    try {
      final cached = await SupabaseService.instance.getCachedTranslation(
        messageId,
        targetLanguage,
      );
      if (cached != null) {
        return cached;
      }
    } catch (_) {
      // Ignore cache check errors, proceed to backend
    }

    // 3. Prepare token and request
    final token = SupabaseService.instance.currentSession?.accessToken;
    final backendUrl = AppConfig.backendUrl;

    if (token == null || backendUrl.isEmpty) {
      // Fallback to original text if not authenticated or backend not set
      return Translation(
        id: '',
        messageId: messageId,
        targetLanguage: targetLanguage,
        detectedLanguage: 'unknown',
        translatedText: text,
      );
    }

    // 4. Call FastAPI backend POST /translate/text
    try {
      final url = Uri.parse('$backendUrl/translate/text');
      final response = await http
          .post(
            url,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: jsonEncode({
              'message_id': messageId,
              'text': text,
              'target_language': targetLanguage,
            }),
          )
          .timeout(const Duration(seconds: 12));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return Translation(
          id: '',
          messageId: messageId,
          targetLanguage: targetLanguage,
          detectedLanguage: data['detected_language']?.toString() ?? 'unknown',
          translatedText: data['translated_text']?.toString() ?? text,
        );
      }
    } catch (_) {
      // On any AI/network failure, fall back to original text without blocking
    }

    // 5. Fallback to original text
    return Translation(
      id: '',
      messageId: messageId,
      targetLanguage: targetLanguage,
      detectedLanguage: 'unknown',
      translatedText: text,
    );
  }

  /// Transcribes and translates a voice message into [targetLanguage] via Gemini.
  /// Checks Supabase cache first. Returns null if translation fails.
  Future<Translation?> translateVoice({
    required String messageId,
    required String audioPath,
    required String targetLanguage,
  }) async {
    if (audioPath.trim().isEmpty) return null;

    // 1. Check local/Supabase cache first
    try {
      final cached = await SupabaseService.instance.getCachedTranslation(
        messageId,
        targetLanguage,
      );
      if (cached != null &&
          cached.transcript != null &&
          cached.transcript!.isNotEmpty) {
        return cached;
      }
    } catch (_) {}

    // 2. Token and backend URL check
    final token = SupabaseService.instance.currentSession?.accessToken;
    final backendUrl = AppConfig.backendUrl;
    if (token == null || backendUrl.isEmpty) return null;

    // 3. Call FastAPI backend POST /translate/voice
    try {
      final url = Uri.parse('$backendUrl/translate/voice');
      final response = await http
          .post(
            url,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: jsonEncode({
              'message_id': messageId,
              'audio_path': audioPath,
              'target_language': targetLanguage,
            }),
          )
          .timeout(const Duration(seconds: 35));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return Translation(
          id: '',
          messageId: messageId,
          targetLanguage: targetLanguage,
          detectedLanguage: data['detected_language']?.toString() ?? 'unknown',
          transcript: data['transcript']?.toString(),
          translatedText: data['translated_text']?.toString() ?? '',
        );
      }
    } catch (_) {
      // AI or network failure returns null; app falls back to audio player only
    }

    return null;
  }
}
