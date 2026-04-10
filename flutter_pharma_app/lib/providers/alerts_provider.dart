import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/sensor_data.dart';

class AlertsProvider extends ChangeNotifier {
  final Random _random = Random();
  Timer? _alertTimer;
  
  List<SystemAlert> _alerts = [];
  bool _isMonitoring = false;
  
  List<SystemAlert> get alerts => _alerts;
  List<SystemAlert> get activeAlerts => 
      _alerts.where((a) => !a.isAcknowledged).toList();
  List<SystemAlert> get criticalAlerts => 
      _alerts.where((a) => a.severity == AlertSeverity.critical && !a.isAcknowledged).toList();
  bool get isMonitoring => _isMonitoring;
  
  int get totalAlerts => _alerts.length;
  int get unacknowledgedCount => activeAlerts.length;
  int get criticalCount => criticalAlerts.length;
  
  AlertsProvider() {
    _generateInitialAlerts();
  }
  
  void _generateInitialAlerts() {
    final now = DateTime.now();
    
    // Generate some historical alerts
    _alerts = [
      SystemAlert(
        id: 'ALT-001',
        timestamp: now.subtract(const Duration(hours: 3, minutes: 45)),
        severity: AlertSeverity.major,
        source: 'Sistema de Agua',
        parameter: 'Conductividad',
        message: 'Conductividad excede límite USP',
        currentValue: 1.45,
        limitValue: 1.3,
        isAcknowledged: true,
        acknowledgedAt: now.subtract(const Duration(hours: 3, minutes: 30)),
        acknowledgedBy: 'Operador A',
      ),
      SystemAlert(
        id: 'ALT-002',
        timestamp: now.subtract(const Duration(hours: 2, minutes: 15)),
        severity: AlertSeverity.minor,
        source: 'Ambiente',
        parameter: 'Humedad',
        message: 'Humedad relativa cercana al límite superior',
        currentValue: 63.5,
        limitValue: 65.0,
        isAcknowledged: true,
        acknowledgedAt: now.subtract(const Duration(hours: 2)),
        acknowledgedBy: 'Supervisor B',
      ),
      SystemAlert(
        id: 'ALT-003',
        timestamp: now.subtract(const Duration(hours: 1, minutes: 30)),
        severity: AlertSeverity.critical,
        source: 'Producción Tabletas',
        parameter: 'Peso',
        message: 'Peso de tableta fuera de especificación',
        currentValue: 468.5,
        limitValue: 475.0,
        isAcknowledged: false,
      ),
      SystemAlert(
        id: 'ALT-004',
        timestamp: now.subtract(const Duration(minutes: 45)),
        severity: AlertSeverity.major,
        source: 'ML Predicción',
        parameter: 'Anomalía Detectada',
        message: 'Modelo detecta patrón anómalo en datos de agua',
        currentValue: 0.89,
        limitValue: 0.70,
        isAcknowledged: false,
      ),
      SystemAlert(
        id: 'ALT-005',
        timestamp: now.subtract(const Duration(minutes: 15)),
        severity: AlertSeverity.minor,
        source: 'Ambiente',
        parameter: 'Partículas 0.5µm',
        message: 'Incremento en conteo de partículas',
        currentValue: 42000,
        limitValue: 35200,
        isAcknowledged: false,
      ),
    ];
  }
  
  void startMonitoring() {
    if (_isMonitoring) return;
    
    _isMonitoring = true;
    _alertTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      _checkForNewAlerts();
    });
    notifyListeners();
  }
  
  void stopMonitoring() {
    _alertTimer?.cancel();
    _isMonitoring = false;
    notifyListeners();
  }
  
  void _checkForNewAlerts() {
    // Randomly generate new alerts (simulation)
    if (_random.nextDouble() < 0.3) {
      final alertTypes = [
        {
          'source': 'Sistema de Agua',
          'parameter': 'TOC',
          'severity': AlertSeverity.major,
          'message': 'TOC excede límite de alerta',
          'current': 520.0,
          'limit': 500.0,
        },
        {
          'source': 'Producción Tabletas',
          'parameter': 'Dureza',
          'severity': AlertSeverity.minor,
          'message': 'Dureza de tableta cercana al límite',
          'current': 78.5,
          'limit': 80.0,
        },
        {
          'source': 'Ambiente',
          'parameter': 'Temperatura',
          'severity': AlertSeverity.major,
          'message': 'Temperatura fuera de rango',
          'current': 26.2,
          'limit': 25.0,
        },
        {
          'source': 'ML Predicción',
          'parameter': 'Score Anomalía',
          'severity': AlertSeverity.critical,
          'message': 'Alta probabilidad de anomalía detectada',
          'current': 0.92,
          'limit': 0.70,
        },
        {
          'source': 'Sistema de Agua',
          'parameter': 'pH',
          'severity': AlertSeverity.critical,
          'message': 'pH fuera de especificación USP',
          'current': 4.8,
          'limit': 5.0,
        },
      ];
      
      final alertType = alertTypes[_random.nextInt(alertTypes.length)];
      final newId = 'ALT-${(_alerts.length + 1).toString().padLeft(3, '0')}';
      
      _alerts.insert(0, SystemAlert(
        id: newId,
        timestamp: DateTime.now(),
        severity: alertType['severity'] as AlertSeverity,
        source: alertType['source'] as String,
        parameter: alertType['parameter'] as String,
        message: alertType['message'] as String,
        currentValue: alertType['current'] as double,
        limitValue: alertType['limit'] as double,
      ));
      
      notifyListeners();
    }
  }
  
  void acknowledgeAlert(String alertId, String acknowledgedBy) {
    final index = _alerts.indexWhere((a) => a.id == alertId);
    if (index != -1) {
      _alerts[index] = _alerts[index].copyWith(
        isAcknowledged: true,
        acknowledgedAt: DateTime.now(),
        acknowledgedBy: acknowledgedBy,
      );
      notifyListeners();
    }
  }
  
  void acknowledgeAllAlerts(String acknowledgedBy) {
    _alerts = _alerts.map((alert) {
      if (!alert.isAcknowledged) {
        return alert.copyWith(
          isAcknowledged: true,
          acknowledgedAt: DateTime.now(),
          acknowledgedBy: acknowledgedBy,
        );
      }
      return alert;
    }).toList();
    notifyListeners();
  }
  
  void clearAcknowledgedAlerts() {
    _alerts.removeWhere((a) => a.isAcknowledged);
    notifyListeners();
  }
  
  Map<String, int> get alertsBySource {
    final Map<String, int> counts = {};
    for (final alert in activeAlerts) {
      counts[alert.source] = (counts[alert.source] ?? 0) + 1;
    }
    return counts;
  }
  
  Map<AlertSeverity, int> get alertsBySeverity {
    final Map<AlertSeverity, int> counts = {};
    for (final alert in activeAlerts) {
      counts[alert.severity] = (counts[alert.severity] ?? 0) + 1;
    }
    return counts;
  }
  
  @override
  void dispose() {
    _alertTimer?.cancel();
    super.dispose();
  }
}
