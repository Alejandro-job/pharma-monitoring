import 'package:equatable/equatable.dart';

// Modelo base para datos de sensores
class SensorReading extends Equatable {
  final DateTime timestamp;
  final double value;
  final String unit;
  final bool isAnomaly;
  final double? anomalyScore;

  const SensorReading({
    required this.timestamp,
    required this.value,
    required this.unit,
    this.isAnomaly = false,
    this.anomalyScore,
  });

  @override
  List<Object?> get props => [timestamp, value, unit, isAnomaly, anomalyScore];

  factory SensorReading.fromJson(Map<String, dynamic> json) {
    return SensorReading(
      timestamp: DateTime.parse(json['timestamp']),
      value: (json['value'] as num).toDouble(),
      unit: json['unit'] ?? '',
      isAnomaly: json['is_anomaly'] ?? false,
      anomalyScore: json['anomaly_score']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp.toIso8601String(),
    'value': value,
    'unit': unit,
    'is_anomaly': isAnomaly,
    'anomaly_score': anomalyScore,
  };
}

// Datos del sistema de agua
class WaterSystemData extends Equatable {
  final DateTime timestamp;
  final double conductivity;
  final double toc;
  final double ph;
  final double temperature;
  final double flowRate;
  final bool isAnomaly;
  final double? anomalyScore;

  const WaterSystemData({
    required this.timestamp,
    required this.conductivity,
    required this.toc,
    required this.ph,
    required this.temperature,
    required this.flowRate,
    this.isAnomaly = false,
    this.anomalyScore,
  });

  @override
  List<Object?> get props => [
    timestamp, conductivity, toc, ph, temperature, flowRate, isAnomaly
  ];

  factory WaterSystemData.fromJson(Map<String, dynamic> json) {
    return WaterSystemData(
      timestamp: DateTime.parse(json['timestamp']),
      conductivity: (json['conductivity'] as num).toDouble(),
      toc: (json['toc'] as num).toDouble(),
      ph: (json['ph'] as num).toDouble(),
      temperature: (json['temperature'] as num).toDouble(),
      flowRate: (json['flow_rate'] as num).toDouble(),
      isAnomaly: json['is_anomaly'] ?? false,
      anomalyScore: json['anomaly_score']?.toDouble(),
    );
  }

  // Límites USP para agua purificada
  static const double conductivityMax = 1.3; // µS/cm
  static const double tocMax = 500; // ppb
  static const double phMin = 5.0;
  static const double phMax = 7.0;
  
  bool get conductivityInSpec => conductivity <= conductivityMax;
  bool get tocInSpec => toc <= tocMax;
  bool get phInSpec => ph >= phMin && ph <= phMax;
  bool get allInSpec => conductivityInSpec && tocInSpec && phInSpec;
}

// Datos de producción de tabletas
class TabletProductionData extends Equatable {
  final DateTime timestamp;
  final String batchId;
  final double weight;
  final double hardness;
  final double thickness;
  final double friability;
  final double dissolutionTime;
  final double contentUniformity;
  final bool isAnomaly;
  final double? anomalyScore;

  const TabletProductionData({
    required this.timestamp,
    required this.batchId,
    required this.weight,
    required this.hardness,
    required this.thickness,
    required this.friability,
    required this.dissolutionTime,
    required this.contentUniformity,
    this.isAnomaly = false,
    this.anomalyScore,
  });

  @override
  List<Object?> get props => [
    timestamp, batchId, weight, hardness, thickness, 
    friability, dissolutionTime, contentUniformity, isAnomaly
  ];

  factory TabletProductionData.fromJson(Map<String, dynamic> json) {
    return TabletProductionData(
      timestamp: DateTime.parse(json['timestamp']),
      batchId: json['batch_id'] ?? '',
      weight: (json['weight'] as num).toDouble(),
      hardness: (json['hardness'] as num).toDouble(),
      thickness: (json['thickness'] as num).toDouble(),
      friability: (json['friability'] as num).toDouble(),
      dissolutionTime: (json['dissolution_time'] as num).toDouble(),
      contentUniformity: (json['content_uniformity'] as num).toDouble(),
      isAnomaly: json['is_anomaly'] ?? false,
      anomalyScore: json['anomaly_score']?.toDouble(),
    );
  }

  // Especificaciones de tabletas
  static const double weightTarget = 500; // mg
  static const double weightTolerance = 0.05; // 5%
  static const double hardnessMin = 40; // N
  static const double hardnessMax = 80; // N
  static const double friabilityMax = 1.0; // %
  
  bool get weightInSpec {
    final min = weightTarget * (1 - weightTolerance);
    final max = weightTarget * (1 + weightTolerance);
    return weight >= min && weight <= max;
  }
  bool get hardnessInSpec => hardness >= hardnessMin && hardness <= hardnessMax;
  bool get friabilityInSpec => friability <= friabilityMax;
}

// Datos ambientales
class EnvironmentData extends Equatable {
  final DateTime timestamp;
  final String roomId;
  final double temperature;
  final double humidity;
  final double differentialPressure;
  final int particleCount05;
  final int particleCount50;
  final String cleanroomClass;
  final bool isAnomaly;
  final double? anomalyScore;

  const EnvironmentData({
    required this.timestamp,
    required this.roomId,
    required this.temperature,
    required this.humidity,
    required this.differentialPressure,
    required this.particleCount05,
    required this.particleCount50,
    required this.cleanroomClass,
    this.isAnomaly = false,
    this.anomalyScore,
  });

  @override
  List<Object?> get props => [
    timestamp, roomId, temperature, humidity, differentialPressure,
    particleCount05, particleCount50, cleanroomClass, isAnomaly
  ];

  factory EnvironmentData.fromJson(Map<String, dynamic> json) {
    return EnvironmentData(
      timestamp: DateTime.parse(json['timestamp']),
      roomId: json['room_id'] ?? '',
      temperature: (json['temperature'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      differentialPressure: (json['differential_pressure'] as num).toDouble(),
      particleCount05: (json['particle_count_05'] as num).toInt(),
      particleCount50: (json['particle_count_50'] as num).toInt(),
      cleanroomClass: json['cleanroom_class'] ?? 'ISO 8',
      isAnomaly: json['is_anomaly'] ?? false,
      anomalyScore: json['anomaly_score']?.toDouble(),
    );
  }

  // Límites ISO para salas limpias
  static const double tempMin = 18.0;
  static const double tempMax = 25.0;
  static const double humidityMin = 30.0;
  static const double humidityMax = 65.0;
  static const double pressureMin = 10.0; // Pa
  
  bool get temperatureInSpec => temperature >= tempMin && temperature <= tempMax;
  bool get humidityInSpec => humidity >= humidityMin && humidity <= humidityMax;
  bool get pressureInSpec => differentialPressure >= pressureMin;
}

// Alerta del sistema
enum AlertSeverity { critical, major, minor, info }

class SystemAlert extends Equatable {
  final String id;
  final DateTime timestamp;
  final AlertSeverity severity;
  final String source;
  final String parameter;
  final String message;
  final double currentValue;
  final double limitValue;
  final bool isAcknowledged;
  final DateTime? acknowledgedAt;
  final String? acknowledgedBy;

  const SystemAlert({
    required this.id,
    required this.timestamp,
    required this.severity,
    required this.source,
    required this.parameter,
    required this.message,
    required this.currentValue,
    required this.limitValue,
    this.isAcknowledged = false,
    this.acknowledgedAt,
    this.acknowledgedBy,
  });

  @override
  List<Object?> get props => [id, timestamp, severity, source, parameter];

  factory SystemAlert.fromJson(Map<String, dynamic> json) {
    return SystemAlert(
      id: json['id'],
      timestamp: DateTime.parse(json['timestamp']),
      severity: AlertSeverity.values.firstWhere(
        (e) => e.name == json['severity'],
        orElse: () => AlertSeverity.info,
      ),
      source: json['source'],
      parameter: json['parameter'],
      message: json['message'],
      currentValue: (json['current_value'] as num).toDouble(),
      limitValue: (json['limit_value'] as num).toDouble(),
      isAcknowledged: json['is_acknowledged'] ?? false,
      acknowledgedAt: json['acknowledged_at'] != null 
          ? DateTime.parse(json['acknowledged_at']) 
          : null,
      acknowledgedBy: json['acknowledged_by'],
    );
  }

  SystemAlert copyWith({
    bool? isAcknowledged,
    DateTime? acknowledgedAt,
    String? acknowledgedBy,
  }) {
    return SystemAlert(
      id: id,
      timestamp: timestamp,
      severity: severity,
      source: source,
      parameter: parameter,
      message: message,
      currentValue: currentValue,
      limitValue: limitValue,
      isAcknowledged: isAcknowledged ?? this.isAcknowledged,
      acknowledgedAt: acknowledgedAt ?? this.acknowledgedAt,
      acknowledgedBy: acknowledgedBy ?? this.acknowledgedBy,
    );
  }
}

// Métricas del modelo ML
class ModelMetrics extends Equatable {
  final String modelName;
  final double accuracy;
  final double precision;
  final double recall;
  final double f1Score;
  final double aucRoc;
  final DateTime trainedAt;
  final int samplesUsed;

  const ModelMetrics({
    required this.modelName,
    required this.accuracy,
    required this.precision,
    required this.recall,
    required this.f1Score,
    required this.aucRoc,
    required this.trainedAt,
    required this.samplesUsed,
  });

  @override
  List<Object> get props => [modelName, accuracy, precision, recall, f1Score, aucRoc];

  factory ModelMetrics.fromJson(Map<String, dynamic> json) {
    return ModelMetrics(
      modelName: json['model_name'],
      accuracy: (json['accuracy'] as num).toDouble(),
      precision: (json['precision'] as num).toDouble(),
      recall: (json['recall'] as num).toDouble(),
      f1Score: (json['f1_score'] as num).toDouble(),
      aucRoc: (json['auc_roc'] as num).toDouble(),
      trainedAt: DateTime.parse(json['trained_at']),
      samplesUsed: json['samples_used'],
    );
  }
}
