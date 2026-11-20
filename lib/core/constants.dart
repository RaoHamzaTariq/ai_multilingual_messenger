class AppConstants {
  static const int maxImageSizeBytes = 1024 * 1024; // 1 MB
  static const int maxVoiceDurationSeconds = 60; // 60 seconds

  // 10 supported languages from project requirements
  static const List<Map<String, String>> supportedLanguages = [
    {'code': 'en', 'name': 'English'},
    {'code': 'ur', 'name': 'Urdu'},
    {'code': 'ar', 'name': 'Arabic'},
    {'code': 'es', 'name': 'Spanish'},
    {'code': 'hi', 'name': 'Hindi'},
    {'code': 'fr', 'name': 'French'},
    {'code': 'de', 'name': 'German'},
    {'code': 'zh', 'name': 'Chinese'},
    {'code': 'tr', 'name': 'Turkish'},
    {'code': 'ru', 'name': 'Russian'},
  ];

  static String getLanguageName(String code) {
    final match = supportedLanguages.firstWhere(
      (lang) => lang['code'] == code,
      orElse: () => {'code': code, 'name': code},
    );
    return match['name'] ?? code;
  }
}

class AppConfig {
  static const String supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://xwvwlwbqzatkwycszkih.supabase.co',
  );
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3dndsd2JxemF0a3d5Y3N6a2loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI4MzY1ODMsImV4cCI6MjEwODQxMjU4M30.w5iElfjitutUxlockEwYZGxuq6nMqT4a33qKsuj9tgY',
  );
  static const String backendUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://localhost:8000',
  );

  static bool get isConfigured =>
      supabaseUrl.isNotEmpty &&
      supabaseAnonKey.isNotEmpty &&
      !supabaseUrl.contains('placeholder');
}

