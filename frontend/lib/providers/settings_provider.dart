import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SettingsProvider extends ChangeNotifier {
  final SharedPreferences prefs;
  final FlutterSecureStorage secureStorage;
  bool _isDarkMode = false;

  SettingsProvider(this.prefs, this.secureStorage) {
    _loadSettings();
  }

  bool get isDarkMode => _isDarkMode;

  void _loadSettings() {
    _isDarkMode = prefs.getBool('dark_mode') ?? false;
  }

  void toggleTheme() {
    _isDarkMode = !_isDarkMode;
    prefs.setBool('dark_mode', _isDarkMode);
    notifyListeners();
  }
}
