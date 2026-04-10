"""
Sistema de Alertas Farmacéuticas
=================================
Autor: [Tu Nombre]
Descripción: Sistema de alertas basado en umbrales y predicciones ML
             para monitoreo de procesos farmacéuticos GMP.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import os

from config import (
    get_config, 
    AlertSeverity, 
    DataSource,
    SEVERITY_COLORS,
    WaterSystemConfig,
    TabletProductionConfig,
    EnvironmentalConfig
)


@dataclass
class Alert:
    """Representa una alerta del sistema"""
    id: str
    timestamp: datetime
    source: DataSource
    parameter: str
    value: float
    limit: float
    severity: AlertSeverity
    message: str
    zone: Optional[str] = None
    batch: Optional[str] = None
    is_ml_based: bool = False
    ml_score: Optional[float] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convierte la alerta a diccionario"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.value,
            'parameter': self.parameter,
            'value': self.value,
            'limit': self.limit,
            'severity': self.severity.value,
            'message': self.message,
            'zone': self.zone,
            'batch': self.batch,
            'is_ml_based': self.is_ml_based,
            'ml_score': self.ml_score,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolution_notes': self.resolution_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Crea una alerta desde un diccionario"""
        return cls(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=DataSource(data['source']),
            parameter=data['parameter'],
            value=data['value'],
            limit=data['limit'],
            severity=AlertSeverity(data['severity']),
            message=data['message'],
            zone=data.get('zone'),
            batch=data.get('batch'),
            is_ml_based=data.get('is_ml_based', False),
            ml_score=data.get('ml_score'),
            acknowledged=data.get('acknowledged', False),
            acknowledged_by=data.get('acknowledged_by'),
            acknowledged_at=datetime.fromisoformat(data['acknowledged_at']) if data.get('acknowledged_at') else None,
            resolution_notes=data.get('resolution_notes')
        )


@dataclass
class AlertRule:
    """Regla de alerta para un parámetro"""
    parameter: str
    source: DataSource
    limit_type: str  # 'upper', 'lower', 'range'
    limit_value: float  # Para upper/lower
    limit_range: Optional[Tuple[float, float]] = None  # Para range
    critical_multiplier: float = 1.0
    major_multiplier: float = 0.9
    minor_multiplier: float = 0.8
    unit: str = ""
    description: str = ""


class AlertEngine:
    """
    Motor de alertas para el sistema de monitoreo farmacéutico.
    
    Funcionalidades:
    - Evaluación de umbrales estáticos
    - Integración con predicciones ML
    - Gestión de severidad
    - Agregación y deduplicación
    - Notificaciones
    """
    
    def __init__(self):
        """Inicializa el motor de alertas"""
        self.config = get_config()
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        self.rules = self._initialize_rules()
        self.alert_history = defaultdict(list)
        
    def _initialize_rules(self) -> Dict[str, AlertRule]:
        """Inicializa las reglas de alerta basadas en la configuración"""
        rules = {}
        
        # Reglas para sistema de agua
        water_cfg = self.config.water_config
        
        rules['water_conductivity'] = AlertRule(
            parameter='conductivity_uS_cm',
            source=DataSource.WATER,
            limit_type='upper',
            limit_value=water_cfg.conductivity_limit,
            unit='μS/cm',
            description='Conductividad del agua purificada (USP <645>)'
        )
        
        rules['water_toc'] = AlertRule(
            parameter='toc_ppb',
            source=DataSource.WATER,
            limit_type='upper',
            limit_value=water_cfg.toc_limit,
            unit='ppb',
            description='Carbono Orgánico Total (USP <643>)'
        )
        
        rules['water_ph'] = AlertRule(
            parameter='ph',
            source=DataSource.WATER,
            limit_type='range',
            limit_value=0,
            limit_range=water_cfg.ph_limits,
            unit='',
            description='pH del agua (USP <791>)'
        )
        
        rules['water_endotoxin'] = AlertRule(
            parameter='endotoxin_EU_mL',
            source=DataSource.WATER,
            limit_type='upper',
            limit_value=water_cfg.endotoxin_limit,
            unit='EU/mL',
            description='Endotoxinas (USP <85>)'
        )
        
        rules['water_bioburden'] = AlertRule(
            parameter='bioburden_CFU_mL',
            source=DataSource.WATER,
            limit_type='upper',
            limit_value=water_cfg.bioburden_limit,
            unit='CFU/mL',
            description='Conteo microbiano'
        )
        
        # Reglas para producción de tabletas
        tablet_cfg = self.config.tablet_config
        
        rules['tablet_weight'] = AlertRule(
            parameter='weight_mg',
            source=DataSource.TABLETS,
            limit_type='range',
            limit_value=0,
            limit_range=(
                tablet_cfg.weight_target * (1 - tablet_cfg.weight_tolerance),
                tablet_cfg.weight_target * (1 + tablet_cfg.weight_tolerance)
            ),
            unit='mg',
            description='Peso de tableta (USP <905>)'
        )
        
        rules['tablet_hardness'] = AlertRule(
            parameter='hardness_N',
            source=DataSource.TABLETS,
            limit_type='range',
            limit_value=0,
            limit_range=tablet_cfg.hardness_limits,
            unit='N',
            description='Dureza de tableta (USP <1217>)'
        )
        
        rules['tablet_friability'] = AlertRule(
            parameter='friability_pct',
            source=DataSource.TABLETS,
            limit_type='upper',
            limit_value=tablet_cfg.friability_limit,
            unit='%',
            description='Friabilidad (USP <1216>)'
        )
        
        rules['tablet_disintegration'] = AlertRule(
            parameter='disintegration_min',
            source=DataSource.TABLETS,
            limit_type='upper',
            limit_value=tablet_cfg.disintegration_limit,
            unit='min',
            description='Tiempo de desintegración (USP <701>)'
        )
        
        rules['tablet_dissolution'] = AlertRule(
            parameter='dissolution_pct',
            source=DataSource.TABLETS,
            limit_type='lower',
            limit_value=tablet_cfg.dissolution_limit,
            unit='%',
            description='Disolución Q (USP <711>)'
        )
        
        # Reglas para monitoreo ambiental
        env_cfg = self.config.environmental_config
        
        rules['env_particles_05'] = AlertRule(
            parameter='particles_05um_per_m3',
            source=DataSource.ENVIRONMENT,
            limit_type='upper',
            limit_value=env_cfg.particles_05_limits['ISO_7'],
            unit='partículas/m³',
            description='Partículas ≥0.5μm (ISO 14644-1)'
        )
        
        rules['env_temperature'] = AlertRule(
            parameter='temperature_C',
            source=DataSource.ENVIRONMENT,
            limit_type='range',
            limit_value=0,
            limit_range=env_cfg.temperature_limits,
            unit='°C',
            description='Temperatura ambiental (GMP)'
        )
        
        rules['env_humidity'] = AlertRule(
            parameter='humidity_pct',
            source=DataSource.ENVIRONMENT,
            limit_type='range',
            limit_value=0,
            limit_range=env_cfg.humidity_limits,
            unit='%',
            description='Humedad relativa (GMP)'
        )
        
        rules['env_pressure'] = AlertRule(
            parameter='pressure_diff_Pa',
            source=DataSource.ENVIRONMENT,
            limit_type='lower',
            limit_value=env_cfg.pressure_diff_min,
            unit='Pa',
            description='Presión diferencial mínima'
        )
        
        return rules
    
    def _generate_alert_id(self) -> str:
        """Genera un ID único para la alerta"""
        self.alert_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ALT-{timestamp}-{self.alert_counter:04d}"
    
    def _determine_severity(
        self,
        value: float,
        rule: AlertRule
    ) -> Optional[AlertSeverity]:
        """
        Determina la severidad de una alerta basada en el valor y la regla.
        
        Returns:
            Severidad de la alerta o None si está dentro de límites
        """
        if rule.limit_type == 'upper':
            limit = rule.limit_value
            
            if value >= limit * rule.critical_multiplier:
                return AlertSeverity.CRITICAL
            elif value >= limit * rule.major_multiplier:
                return AlertSeverity.MAJOR
            elif value >= limit * rule.minor_multiplier:
                return AlertSeverity.MINOR
                
        elif rule.limit_type == 'lower':
            limit = rule.limit_value
            
            if value <= limit * (2 - rule.critical_multiplier):
                return AlertSeverity.CRITICAL
            elif value <= limit * (2 - rule.major_multiplier):
                return AlertSeverity.MAJOR
            elif value <= limit * (2 - rule.minor_multiplier):
                return AlertSeverity.MINOR
                
        elif rule.limit_type == 'range':
            lower, upper = rule.limit_range
            range_size = upper - lower
            
            # Calcular desviación del rango
            if value < lower:
                deviation = (lower - value) / range_size
            elif value > upper:
                deviation = (value - upper) / range_size
            else:
                return None
            
            if deviation >= 0.2:
                return AlertSeverity.CRITICAL
            elif deviation >= 0.1:
                return AlertSeverity.MAJOR
            else:
                return AlertSeverity.MINOR
        
        return None
    
    def _create_alert_message(
        self,
        rule: AlertRule,
        value: float,
        severity: AlertSeverity
    ) -> str:
        """Genera el mensaje de la alerta"""
        severity_text = {
            AlertSeverity.CRITICAL: "CRÍTICO",
            AlertSeverity.MAJOR: "MAYOR",
            AlertSeverity.MINOR: "MENOR",
            AlertSeverity.INFO: "INFO"
        }
        
        if rule.limit_type == 'upper':
            return (f"[{severity_text[severity]}] {rule.description}: "
                   f"Valor {value:.3f} {rule.unit} excede límite de {rule.limit_value} {rule.unit}")
        elif rule.limit_type == 'lower':
            return (f"[{severity_text[severity]}] {rule.description}: "
                   f"Valor {value:.3f} {rule.unit} por debajo del mínimo {rule.limit_value} {rule.unit}")
        else:  # range
            lower, upper = rule.limit_range
            return (f"[{severity_text[severity]}] {rule.description}: "
                   f"Valor {value:.3f} {rule.unit} fuera del rango [{lower}, {upper}] {rule.unit}")
    
    def evaluate_threshold(
        self,
        df: pd.DataFrame,
        source: DataSource
    ) -> List[Alert]:
        """
        Evalúa umbrales estáticos y genera alertas.
        
        Args:
            df: DataFrame con los datos
            source: Fuente de datos
            
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        # Filtrar reglas por fuente
        source_rules = {k: v for k, v in self.rules.items() if v.source == source}
        
        for rule_name, rule in source_rules.items():
            if rule.parameter not in df.columns:
                continue
            
            for idx, row in df.iterrows():
                value = row[rule.parameter]
                timestamp = row.get('timestamp', datetime.now())
                
                if pd.isna(value):
                    continue
                
                severity = self._determine_severity(value, rule)
                
                if severity is not None:
                    # Determinar límite para mostrar
                    if rule.limit_type == 'upper':
                        limit = rule.limit_value
                    elif rule.limit_type == 'lower':
                        limit = rule.limit_value
                    else:
                        lower, upper = rule.limit_range
                        limit = lower if value < lower else upper
                    
                    alert = Alert(
                        id=self._generate_alert_id(),
                        timestamp=timestamp if isinstance(timestamp, datetime) else pd.to_datetime(timestamp),
                        source=source,
                        parameter=rule.parameter,
                        value=value,
                        limit=limit,
                        severity=severity,
                        message=self._create_alert_message(rule, value, severity),
                        zone=row.get('zone'),
                        batch=row.get('batch_number'),
                        is_ml_based=False
                    )
                    alerts.append(alert)
        
        # Agregar al historial
        self.alerts.extend(alerts)
        
        return alerts
    
    def evaluate_ml_predictions(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        scores: np.ndarray,
        source: DataSource
    ) -> List[Alert]:
        """
        Genera alertas basadas en predicciones de ML.
        
        Args:
            df: DataFrame con los datos
            predictions: Predicciones binarias (1=anomalía)
            scores: Scores de anomalía
            source: Fuente de datos
            
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        anomaly_indices = np.where(predictions == 1)[0]
        
        for idx in anomaly_indices:
            row = df.iloc[idx]
            score = scores[idx]
            timestamp = row.get('timestamp', datetime.now())
            
            # Determinar severidad basada en score
            if score >= 0.9:
                severity = AlertSeverity.CRITICAL
            elif score >= 0.7:
                severity = AlertSeverity.MAJOR
            else:
                severity = AlertSeverity.MINOR
            
            # Identificar parámetros fuera de rango
            anomalous_params = []
            for col in df.select_dtypes(include=[np.number]).columns:
                if col in ['is_anomaly']:
                    continue
                val = row[col]
                mean = df[col].mean()
                std = df[col].std()
                z_score = abs((val - mean) / std) if std > 0 else 0
                if z_score > 2:
                    anomalous_params.append(f"{col}={val:.2f}")
            
            params_str = ", ".join(anomalous_params[:3])  # Mostrar máximo 3
            
            alert = Alert(
                id=self._generate_alert_id(),
                timestamp=timestamp if isinstance(timestamp, datetime) else pd.to_datetime(timestamp),
                source=source,
                parameter="ML_ANOMALY",
                value=score,
                limit=0.5,
                severity=severity,
                message=f"[ML] Anomalía detectada (score: {score:.2f}). Parámetros: {params_str}",
                zone=row.get('zone'),
                batch=row.get('batch_number'),
                is_ml_based=True,
                ml_score=score
            )
            alerts.append(alert)
        
        self.alerts.extend(alerts)
        
        return alerts
    
    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        source: Optional[DataSource] = None,
        acknowledged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Alert]:
        """
        Obtiene alertas filtradas.
        
        Args:
            severity: Filtrar por severidad
            source: Filtrar por fuente
            acknowledged: Filtrar por estado de reconocimiento
            start_time: Tiempo de inicio
            end_time: Tiempo de fin
            limit: Número máximo de alertas
            
        Returns:
            Lista de alertas filtradas
        """
        filtered = self.alerts
        
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        if source:
            filtered = [a for a in filtered if a.source == source]
        
        if acknowledged is not None:
            filtered = [a for a in filtered if a.acknowledged == acknowledged]
        
        if start_time:
            filtered = [a for a in filtered if a.timestamp >= start_time]
        
        if end_time:
            filtered = [a for a in filtered if a.timestamp <= end_time]
        
        # Ordenar por timestamp descendente
        filtered = sorted(filtered, key=lambda x: x.timestamp, reverse=True)
        
        return filtered[:limit]
    
    def acknowledge_alert(
        self,
        alert_id: str,
        user: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Reconoce una alerta.
        
        Args:
            alert_id: ID de la alerta
            user: Usuario que reconoce
            notes: Notas de resolución
            
        Returns:
            True si se reconoció correctamente
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                alert.resolution_notes = notes
                return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Genera un resumen de alertas.
        
        Returns:
            Diccionario con el resumen
        """
        summary = {
            'total': len(self.alerts),
            'by_severity': {
                'critical': len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]),
                'major': len([a for a in self.alerts if a.severity == AlertSeverity.MAJOR]),
                'minor': len([a for a in self.alerts if a.severity == AlertSeverity.MINOR]),
                'info': len([a for a in self.alerts if a.severity == AlertSeverity.INFO])
            },
            'by_source': {
                'water': len([a for a in self.alerts if a.source == DataSource.WATER]),
                'tablets': len([a for a in self.alerts if a.source == DataSource.TABLETS]),
                'environment': len([a for a in self.alerts if a.source == DataSource.ENVIRONMENT])
            },
            'acknowledged': len([a for a in self.alerts if a.acknowledged]),
            'unacknowledged': len([a for a in self.alerts if not a.acknowledged]),
            'ml_based': len([a for a in self.alerts if a.is_ml_based]),
            'threshold_based': len([a for a in self.alerts if not a.is_ml_based])
        }
        
        # Alertas recientes (últimas 24 horas)
        cutoff = datetime.now() - timedelta(hours=24)
        recent = [a for a in self.alerts if a.timestamp >= cutoff]
        summary['last_24h'] = len(recent)
        summary['last_24h_critical'] = len([a for a in recent if a.severity == AlertSeverity.CRITICAL])
        
        return summary
    
    def export_alerts(
        self,
        filepath: str,
        format: str = 'json'
    ):
        """
        Exporta alertas a archivo.
        
        Args:
            filepath: Ruta del archivo
            format: Formato ('json', 'csv')
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        if format == 'json':
            data = [a.to_dict() for a in self.alerts]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            df = pd.DataFrame([a.to_dict() for a in self.alerts])
            df.to_csv(filepath, index=False)
        
        print(f"Alertas exportadas a: {filepath}")
    
    def clear_old_alerts(self, days: int = 90):
        """
        Elimina alertas antiguas.
        
        Args:
            days: Días de retención
        """
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff]
        removed = original_count - len(self.alerts)
        print(f"Eliminadas {removed} alertas antiguas (>{days} días)")


class AlertNotifier:
    """
    Sistema de notificaciones para alertas.
    
    Soporta múltiples canales:
    - Dashboard (en memoria)
    - Email (simulado)
    - SMS (simulado)
    """
    
    def __init__(self):
        """Inicializa el notificador"""
        self.config = get_config().alert_config
        self.notification_history = []
        
    def notify(
        self,
        alerts: List[Alert],
        channels: Optional[List[str]] = None
    ):
        """
        Envía notificaciones para una lista de alertas.
        
        Args:
            alerts: Lista de alertas
            channels: Canales a usar
        """
        if channels is None:
            channels = []
            if self.config.dashboard_enabled:
                channels.append('dashboard')
            if self.config.email_enabled:
                channels.append('email')
            if self.config.sms_enabled:
                channels.append('sms')
        
        for alert in alerts:
            for channel in channels:
                self._send_notification(alert, channel)
    
    def _send_notification(self, alert: Alert, channel: str):
        """Envía una notificación por un canal específico"""
        notification = {
            'alert_id': alert.id,
            'channel': channel,
            'timestamp': datetime.now().isoformat(),
            'severity': alert.severity.value,
            'message': alert.message
        }
        
        if channel == 'email':
            # Simulación de envío de email
            print(f"[EMAIL] Enviando alerta {alert.id} a administradores...")
            notification['status'] = 'sent'
            notification['recipients'] = ['admin@pharma.com', 'qa@pharma.com']
            
        elif channel == 'sms':
            # Solo alertas críticas por SMS
            if alert.severity == AlertSeverity.CRITICAL:
                print(f"[SMS] Enviando alerta crítica {alert.id}...")
                notification['status'] = 'sent'
            else:
                notification['status'] = 'skipped'
                
        else:  # dashboard
            notification['status'] = 'displayed'
        
        self.notification_history.append(notification)


# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    from data_generator import DataGenerator
    from ml_models import AnomalyDetectionEnsemble
    
    print("=" * 60)
    print("SISTEMA DE ALERTAS FARMACÉUTICAS")
    print("=" * 60)
    
    # Generar datos
    print("\nGenerando datos de prueba...")
    generator = DataGenerator()
    data = generator.generate_all_data(days=3)
    
    # Inicializar motor de alertas
    alert_engine = AlertEngine()
    notifier = AlertNotifier()
    
    # Evaluar umbrales estáticos
    print("\n" + "-" * 40)
    print("EVALUACIÓN DE UMBRALES")
    print("-" * 40)
    
    all_alerts = []
    
    for source_name, df in data.items():
        source = DataSource(df['source'].iloc[0])
        alerts = alert_engine.evaluate_threshold(df, source)
        all_alerts.extend(alerts)
        print(f"{source_name}: {len(alerts)} alertas generadas")
    
    # Entrenar modelo ML y evaluar
    print("\n" + "-" * 40)
    print("EVALUACIÓN CON ML")
    print("-" * 40)
    
    ensemble = AnomalyDetectionEnsemble(
        models=['isolation_forest', 'lof'],
        voting_method='soft'
    )
    
    water_df = data['water']
    ensemble.fit(water_df)
    result = ensemble.predict(water_df)
    
    ml_alerts = alert_engine.evaluate_ml_predictions(
        water_df,
        result.ensemble_predictions,
        result.ensemble_scores,
        DataSource.WATER
    )
    print(f"Alertas ML (agua): {len(ml_alerts)}")
    
    # Resumen
    print("\n" + "-" * 40)
    print("RESUMEN DE ALERTAS")
    print("-" * 40)
    
    summary = alert_engine.get_alert_summary()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    
    # Mostrar alertas críticas
    critical_alerts = alert_engine.get_alerts(severity=AlertSeverity.CRITICAL, limit=5)
    if critical_alerts:
        print("\n" + "-" * 40)
        print("ALERTAS CRÍTICAS (últimas 5)")
        print("-" * 40)
        for alert in critical_alerts:
            print(f"\n[{alert.id}] {alert.timestamp}")
            print(f"  {alert.message}")
    
    # Notificar alertas críticas
    notifier.notify(critical_alerts)
    
    # Exportar
    alert_engine.export_alerts("alerts_export.json")
    
    print("\n" + "=" * 60)
    print("Sistema de alertas completado")
    print("=" * 60)
