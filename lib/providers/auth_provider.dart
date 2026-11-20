import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/profile.dart';
import '../services/supabase_service.dart';

class AuthProvider extends ChangeNotifier {
  final SupabaseService _service = SupabaseService.instance;

  Profile? _profile;
  bool _isLoading = false;
  String? _errorMessage;

  Profile? get profile => _profile;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  bool get isAuthenticated => _service.currentUser != null;
  bool get hasChosenLanguage =>
      _profile?.preferredLanguage != null &&
      _profile!.preferredLanguage!.isNotEmpty;

  Future<void> checkSession() async {
    _setLoading(true);
    _errorMessage = null;

    try {
      if (!_service.isInitialized) {
        await _service.initialize();
      }

      final user = _service.currentUser;
      if (user != null) {
        _profile = await _service.getProfile(user.id);
      } else {
        _profile = null;
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> signUp({
    required String email,
    required String password,
    required String username,
  }) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      if (!_service.isInitialized) {
        await _service.initialize();
      }
      if (!_service.isInitialized) {
        _errorMessage = 'Supabase is not configured. Please supply SUPABASE_URL and SUPABASE_ANON_KEY.';
        _setLoading(false);
        return false;
      }

      final response = await _service.signUp(
        email: email,
        password: password,
        username: username,
      );

      final user = response.user;
      if (user != null) {
        _profile = await _service.getProfile(user.id);
        _setLoading(false);
        return true;
      }
      _errorMessage = 'Sign up failed. Please check your details.';
      _setLoading(false);
      return false;
    } on AuthException catch (e) {
      _errorMessage = e.message;
      _setLoading(false);
      return false;
    } catch (e) {
      _errorMessage = e.toString();
      _setLoading(false);
      return false;
    }
  }

  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      if (!_service.isInitialized) {
        await _service.initialize();
      }
      if (!_service.isInitialized) {
        _errorMessage = 'Supabase is not configured. Please supply SUPABASE_URL and SUPABASE_ANON_KEY.';
        _setLoading(false);
        return false;
      }

      final response = await _service.signIn(
        email: email,
        password: password,
      );

      final user = response.user;
      if (user != null) {
        _profile = await _service.getProfile(user.id);
        _setLoading(false);
        return true;
      }
      _errorMessage = 'Invalid email or password.';
      _setLoading(false);
      return false;
    } on AuthException catch (e) {
      _errorMessage = e.message;
      _setLoading(false);
      return false;
    } catch (e) {
      _errorMessage = e.toString();
      _setLoading(false);
      return false;
    }
  }

  Future<bool> setPreferredLanguage(String languageCode) async {
    final user = _service.currentUser;
    if (user == null) {
      _errorMessage = 'No active user session. Please log in first.';
      notifyListeners();
      return false;
    }

    _setLoading(true);
    _errorMessage = null;

    try {
      await _service.updatePreferredLanguage(user.id, languageCode);
      _profile = await _service.getProfile(user.id);
      _setLoading(false);
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _setLoading(false);
      return false;
    }
  }

  Future<bool> updateDisplayName(String displayName) async {
    final user = _service.currentUser;
    if (user == null) return false;

    _setLoading(true);
    _errorMessage = null;

    try {
      await _service.updateDisplayName(user.id, displayName);
      if (_profile != null) {
        _profile = _profile!.copyWith(displayName: displayName.trim());
      }
      _setLoading(false);
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _setLoading(false);
      return false;
    }
  }

  Future<void> logout() async {
    _setLoading(true);
    try {
      await _service.signOut();
      _profile = null;
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
