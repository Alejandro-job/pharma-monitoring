import 'package:flutter/foundation.dart';

class SettingsProvider extends ChangeNotifier {
  bool _isDarkMode = true;
  bool _notificationsEnabled = true;
  bool _soundEnabled = true;
  String _refreshRate = '3s';
  String _language = 'es';
  String _dateFormat = 'dd/MM/yyyy';
  
  // Getters
  bool get isDarkMode => _isDarkMode;
  bool get notificationsEnabled => _notificationsEnabled;
  bool get soundEnabled => _soundEnabled;
  String get refreshRate => _refreshRate;
  String get language => _language;
  String get dateFormat => _dateFormat;
  
  // Setters
  void setDarkMode(bool value) {
    _isDarkMode = value;
    notifyListeners();
  }
  
  void setNotificationsEnabled(bool value) {
    _notificationsEnabled = value;
    notifyListeners();
  }
  
  void setSoundEnabled(bool value) {
    _soundEnabled = value;
    notifyListeners();
  }
  
  void setRefreshRate(String value) {
    _refreshRate = value;
    notifyListeners();
  }
  
  void setLanguage(String value) {
    _language = value;
    notifyListeners();
  }
  
  void setDateFormat(String value) {
    _dateFormat = value;
    notifyListeners();
  }
}
