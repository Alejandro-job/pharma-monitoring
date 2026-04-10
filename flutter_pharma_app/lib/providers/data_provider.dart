import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/sensor_data.dart';

class DataProvider extends ChangeNotifier {
  final Random _random = Random();
  Timer? _dataTimer;
  bool _isSimulating = false;
  
  // Data storage
  List<WaterSystemData> _waterData = [];
  List<TabletProductionData> _tabletData = [];
  List<EnvironmentData> _environmentData = [];
  List<ModelMetrics> _modelMetrics = [];
  
  // Getters
  List<WaterSystemData> get waterData => _waterData;
  List<TabletProductionData> get tabletData => _tabletData;
  List<EnvironmentData> get environmentData => _environmentData;
  List<ModelMetrics> get modelMetrics => _modelMetrics;
  bool get isSimulating => _isSimulating;
  
  // Latest readings
  WaterSystemData? get latestWaterData => 
      _waterData.isNotEmpty ? _waterData.last : null;
  TabletProductionData? get latestTabletData => 
      _tabletData.isNotEmpty ? _tabletData.last : null;
  EnvironmentData? get latestEnvironmentData => 
      _environmentData.isNotEmpty ? _environmentData.last : null;
  
  // Statistics
  Map<String, double> get waterStats => _calculateWaterStats();
  Map<String, double> get tabletStats => _calculateTabletStats();
  Map<String, double> get environmentStats => _calculateEnvironmentStats();
  
  DataProvider() {
    _initializeData();
    _initializeModelMetrics();
  }
  
  void _initializeData() {
    final now = DateTime.now();
    
    // Generate historical data (last 24 hours)
    for (int i = 1440; i >= 0; i--) {
      final timestamp = now.subtract(Duration(minutes: i));
      _waterData.add(_generateWaterData(timestamp));
      
      if (i % 5 == 0) { // Tablet data every 5 minutes
        _tabletData.add(_generateTabletData(timestamp));
      }
      
      if (i % 2 == 0) { // Environment data every 2 minutes
        _environmentData.add(_generateEnvironmentData(timestamp));
      }
    }
  }
  
  void _initializeModelMetrics() {
    _modelMetrics = [
      ModelMetrics(
        modelName: 'Isolation Forest',
        accuracy: 0.956,
        precision: 0.923,
        recall: 0.891,
        f1Score: 0.907,
        aucRoc: 0.967,
        trainedAt: DateTime.now().subtract(const Duration(hours: 2)),
        samplesUsed: 50000,
      ),
      ModelMetrics(
        modelName: 'Local Outlier Factor',
        accuracy: 0.942,
        precision: 0.915,
        recall: 0.878,
        f1Score: 0.896,
        aucRoc: 0.951,
        trainedAt: DateTime.now().subtract(const Duration(hours: 2)),
        samplesUsed: 50000,
      ),
      ModelMetrics(
        modelName: 'One-Class SVM',
        accuracy: 0.938,
        precision: 0.902,
        recall: 0.885,
        f1Score: 0.893,
        aucRoc: 0.945,
        trainedAt: DateTime.now().subtract(const Duration(hours: 2)),
        samplesUsed: 50000,
      ),
      ModelMetrics(
        modelName: 'Autoencoder',
        accuracy: 0.961,
        precision: 0.934,
        recall: 0.912,
        f1Score: 0.923,
        aucRoc: 0.972,
        trainedAt: DateTime.now().subtract(const Duration(hours: 2)),
        samplesUsed: 50000,
      ),
    ];
  }
  
  // Start real-time simulation
  void startSimulation() {
    if (_isSimulating) return;
    
    _isSimulating = true;
    _dataTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      _addNewReading();
    });
    notifyListeners();
  }
  
  // Stop simulation
  void stopSimulation() {
    _dataTimer?.cancel();
    _isSimulating = false;
    notifyListeners();
  }
  
  void _addNewReading() {
    final now = DateTime.now();
    
    _waterData.add(_generateWaterData(now));
    if (_waterData.length > 2000) {
      _waterData.removeAt(0);
    }
    
    if (_random.nextDouble() < 0.33) {
      _tabletData.add(_generateTabletData(now));
      if (_tabletData.length > 500) {
        _tabletData.removeAt(0);
      }
    }
    
    _environmentData.add(_generateEnvironmentData(now));
    if (_environmentData.length > 1000) {
      _environmentData.removeAt(0);
    }
    
    notifyListeners();
  }
  
  WaterSystemData _generateWaterData(DateTime timestamp) {
    // Simulate realistic water system data with occasional anomalies
    final isAnomaly = _random.nextDouble() < 0.02;
    
    double conductivity = 0.8 + _random.nextDouble() * 0.3;
    double toc = 250 + _random.nextDouble() * 150;
    double ph = 6.0 + _random.nextDouble() * 0.8;
    double temperature = 22 + _random.nextDouble() * 3;
    double flowRate = 45 + _random.nextDouble() * 10;
    
    if (isAnomaly) {
      switch (_random.nextInt(3)) {
        case 0:
          conductivity *= 1.5 + _random.nextDouble();
          break;
        case 1:
          toc *= 1.8 + _random.nextDouble();
          break;
        case 2:
          ph = _random.nextBool() ? 4.5 : 7.8;
          break;
      }
    }
    
    return WaterSystemData(
      timestamp: timestamp,
      conductivity: conductivity,
      toc: toc,
      ph: ph,
      temperature: temperature,
      flowRate: flowRate,
      isAnomaly: isAnomaly,
      anomalyScore: isAnomaly ? 0.7 + _random.nextDouble() * 0.3 : _random.nextDouble() * 0.3,
    );
  }
  
  TabletProductionData _generateTabletData(DateTime timestamp) {
    final isAnomaly = _random.nextDouble() < 0.03;
    final batchId = 'BATCH-${timestamp.year}${timestamp.month.toString().padLeft(2, '0')}${timestamp.day.toString().padLeft(2, '0')}-${_random.nextInt(999).toString().padLeft(3, '0')}';
    
    double weight = 498 + _random.nextDouble() * 4;
    double hardness = 55 + _random.nextDouble() * 15;
    double thickness = 4.8 + _random.nextDouble() * 0.4;
    double friability = 0.3 + _random.nextDouble() * 0.4;
    double dissolutionTime = 12 + _random.nextDouble() * 6;
    double contentUniformity = 98 + _random.nextDouble() * 3;
    
    if (isAnomaly) {
      switch (_random.nextInt(3)) {
        case 0:
          weight = _random.nextBool() ? 470 : 535;
          break;
        case 1:
          hardness = _random.nextBool() ? 30 : 95;
          break;
        case 2:
          friability = 1.5 + _random.nextDouble();
          break;
      }
    }
    
    return TabletProductionData(
      timestamp: timestamp,
      batchId: batchId,
      weight: weight,
      hardness: hardness,
      thickness: thickness,
      friability: friability,
      dissolutionTime: dissolutionTime,
      contentUniformity: contentUniformity,
      isAnomaly: isAnomaly,
      anomalyScore: isAnomaly ? 0.75 + _random.nextDouble() * 0.25 : _random.nextDouble() * 0.25,
    );
  }
  
  EnvironmentData _generateEnvironmentData(DateTime timestamp) {
    final isAnomaly = _random.nextDouble() < 0.015;
    final rooms = ['PROD-A', 'PROD-B', 'PACK-1', 'QC-LAB'];
    final classes = ['ISO 7', 'ISO 8'];
    
    double temperature = 21 + _random.nextDouble() * 3;
    double humidity = 42 + _random.nextDouble() * 13;
    double pressure = 12 + _random.nextDouble() * 6;
    int particles05 = 15000 + _random.nextInt(20000);
    int particles50 = 50 + _random.nextInt(200);
    
    if (isAnomaly) {
      switch (_random.nextInt(3)) {
        case 0:
          temperature = _random.nextBool() ? 16 : 28;
          break;
        case 1:
          humidity = _random.nextBool() ? 25 : 72;
          break;
        case 2:
          particles05 *= 3;
          particles50 *= 3;
          break;
      }
    }
    
    return EnvironmentData(
      timestamp: timestamp,
      roomId: rooms[_random.nextInt(rooms.length)],
      temperature: temperature,
      humidity: humidity,
      differentialPressure: pressure,
      particleCount05: particles05,
      particleCount50: particles50,
      cleanroomClass: classes[_random.nextInt(classes.length)],
      isAnomaly: isAnomaly,
      anomalyScore: isAnomaly ? 0.8 + _random.nextDouble() * 0.2 : _random.nextDouble() * 0.2,
    );
  }
  
  Map<String, double> _calculateWaterStats() {
    if (_waterData.isEmpty) return {};
    
    final recent = _waterData.length > 100 
        ? _waterData.sublist(_waterData.length - 100) 
        : _waterData;
    
    return {
      'conductivity_avg': recent.map((d) => d.conductivity).reduce((a, b) => a + b) / recent.length,
      'toc_avg': recent.map((d) => d.toc).reduce((a, b) => a + b) / recent.length,
      'ph_avg': recent.map((d) => d.ph).reduce((a, b) => a + b) / recent.length,
      'anomaly_rate': recent.where((d) => d.isAnomaly).length / recent.length * 100,
      'compliance_rate': recent.where((d) => d.allInSpec).length / recent.length * 100,
    };
  }
  
  Map<String, double> _calculateTabletStats() {
    if (_tabletData.isEmpty) return {};
    
    final recent = _tabletData.length > 50 
        ? _tabletData.sublist(_tabletData.length - 50) 
        : _tabletData;
    
    return {
      'weight_avg': recent.map((d) => d.weight).reduce((a, b) => a + b) / recent.length,
      'hardness_avg': recent.map((d) => d.hardness).reduce((a, b) => a + b) / recent.length,
      'friability_avg': recent.map((d) => d.friability).reduce((a, b) => a + b) / recent.length,
      'anomaly_rate': recent.where((d) => d.isAnomaly).length / recent.length * 100,
      'yield_rate': recent.where((d) => d.weightInSpec && d.hardnessInSpec && d.friabilityInSpec).length / recent.length * 100,
    };
  }
  
  Map<String, double> _calculateEnvironmentStats() {
    if (_environmentData.isEmpty) return {};
    
    final recent = _environmentData.length > 100 
        ? _environmentData.sublist(_environmentData.length - 100) 
        : _environmentData;
    
    return {
      'temperature_avg': recent.map((d) => d.temperature).reduce((a, b) => a + b) / recent.length,
      'humidity_avg': recent.map((d) => d.humidity).reduce((a, b) => a + b) / recent.length,
      'pressure_avg': recent.map((d) => d.differentialPressure).reduce((a, b) => a + b) / recent.length,
      'anomaly_rate': recent.where((d) => d.isAnomaly).length / recent.length * 100,
      'compliance_rate': recent.where((d) => d.temperatureInSpec && d.humidityInSpec && d.pressureInSpec).length / recent.length * 100,
    };
  }
  
  @override
  void dispose() {
    _dataTimer?.cancel();
    super.dispose();
  }
}
