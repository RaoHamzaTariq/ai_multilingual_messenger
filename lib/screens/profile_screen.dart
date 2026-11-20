import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/constants.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';
import 'login_screen.dart';

class ProfileScreen extends StatefulWidget {
  final bool isTab;
  const ProfileScreen({super.key, this.isTab = false});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _nameController = TextEditingController();
  String? _selectedLanguage;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final profile = context.read<AuthProvider>().profile;
    _nameController.text = profile?.displayName ?? '';
    _selectedLanguage = profile?.preferredLanguage ?? 'en';
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    final authProvider = context.read<AuthProvider>();
    setState(() => _isSaving = true);

    bool success = true;

    // Update display name if changed
    if (_nameController.text.trim().isNotEmpty &&
        _nameController.text.trim() != authProvider.profile?.displayName) {
      final nameSuccess = await authProvider.updateDisplayName(_nameController.text);
      if (!nameSuccess) success = false;
    }

    // Update preferred language if changed
    if (_selectedLanguage != null &&
        _selectedLanguage != authProvider.profile?.preferredLanguage) {
      final langSuccess = await authProvider.setPreferredLanguage(_selectedLanguage!);
      if (!langSuccess) success = false;
    }

    setState(() => _isSaving = false);
    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated successfully!')),
      );
    } else {
      final error = authProvider.errorMessage ?? 'Failed to update profile.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error), backgroundColor: Colors.red.shade700),
      );
    }
  }

  Future<void> _confirmLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to log out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Logout'),
          ),
        ],
      ),
    );

    if (confirm != true || !mounted) return;

    final authProvider = context.read<AuthProvider>();
    await authProvider.logout();

    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final profile = authProvider.profile;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: widget.isTab ? null : AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(20.0),
        children: [
          Center(
            child: CircleAvatar(
              radius: 44,
              backgroundColor: theme.colorScheme.primaryContainer,
              child: Text(
                (profile?.displayName.isNotEmpty == true
                        ? profile!.displayName[0]
                        : profile?.username.isNotEmpty == true
                            ? profile!.username[0]
                            : '?')
                    .toUpperCase(),
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Center(
            child: Text(
              '@${profile?.username ?? 'username'}',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(height: 28),
          Text(
            'Personal Details',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Display Name',
              prefixIcon: Icon(Icons.badge_outlined),
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: _selectedLanguage,
            decoration: const InputDecoration(
              labelText: 'Preferred Language',
              prefixIcon: Icon(Icons.language_rounded),
            ),
            items: AppConstants.supportedLanguages.map((lang) {
              return DropdownMenuItem<String>(
                value: lang['code'],
                child: Text('${lang['name']} (${lang['code']})'),
              );
            }).toList(),
            onChanged: (val) {
              setState(() {
                _selectedLanguage = val;
              });
            },
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            icon: const Icon(Icons.check),
            label: _isSaving
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Text('Save Changes'),
            onPressed: _isSaving ? null : _saveProfile,
          ),
          const SizedBox(height: 32),
          Text(
            'Preferences & Session',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 8),
          SwitchListTile(
            title: const Text('Dark Mode'),
            subtitle: const Text('Switch between light and dark themes'),
            secondary: Icon(
              themeProvider.isDarkMode ? Icons.dark_mode : Icons.light_mode,
            ),
            value: themeProvider.isDarkMode,
            onChanged: (val) => themeProvider.setDarkMode(val),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Logout', style: TextStyle(color: Colors.red)),
            onTap: _confirmLogout,
          ),
        ],
      ),
    );
  }
}
