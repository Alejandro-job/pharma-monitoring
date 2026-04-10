"""
Configuración del Sistema de Monitoreo Farmacéutico Industrial
==============================================================
Autor: [Tu Nombre]
Descripción: Parámetros de configuración para simulación de datos,
             umbrales de alerta y configuración de modelos ML.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum
import numpy as np

# =============================================================================
# ENUMERACIONES
# =============================================================================

class AlertSeverity(Enum):
    """Niveles de severidad de alertas según normativas FDA/GMP"""
    CRITICAL = "critical"  # Requiere acción inmediata, detener producción
    MAJOR = "major"        # Requiere investigación en 24h
    MINOR = "minor"        # Requiere revisión en 72h
    INFO = "info"          # Informativo, sin acción requerida


class DataSource(Enum):
    """Fuentes de datos del sistema farmacéutico"""
    WATER = "water_system"
    TABLETS = "tablet_production"
    ENVIRONMENT = "environmental_monitoring"


# =============================================================================
# CONFIGURACIÓN DE SIMULACIÓN DE DATOS
# =============================================================================

@dataclass
class WaterSystemConfig:
    """Configuración para sistema de agua purificada (USP/WFI)"""
    
    # Conductividad (μS/cm) - USP <645>
    conductivity_mean: float = 0.8
    conductivity_std: float = 0.15
    conductivity_limit: float = 1.3  # Límite USP Stage 1
    
    # TOC - Carbono Orgánico Total (ppb) - USP <643>
    toc_mean: float = 250.0
    toc_std: float = 50.0
    toc_limit: float = 500.0  # Límite USP
    
    # pH - USP <791>
    ph_mean: float = 6.8
    ph_std: float = 0.3
    ph_limits: Tuple[float, float] = (5.0, 7.0)
    
    # Temperatura (°C)
    temperature_mean: float = 22.0
    temperature_std: float = 1.5
    temperature_limits: Tuple[float, float] = (15.0, 25.0)
    
    # Endotoxinas (EU/mL) - USP <85>
    endotoxin_mean: float = 0.05
    endotoxin_std: float = 0.02
    endotoxin_limit: float = 0.25  # Límite WFI
    
    # Conteo microbiano (CFU/mL)
    bioburden_mean: float = 5.0
    bioburden_std: float = 3.0
    bioburden_limit: float = 100.0  # Límite PW


@dataclass
class TabletProductionConfig:
    """Configuración para producción de tabletas según farmacopea"""
    
    # Peso de tableta (mg) - USP <905>
    weight_target: float = 500.0
    weight_std: float = 5.0
    weight_tolerance: float = 0.05  # ±5%
    
    # Dureza (N) - USP <1217>
    hardness_mean: float = 100.0
    hardness_std: float = 8.0
    hardness_limits: Tuple[float, float] = (70.0, 130.0)
    
    # Friabilidad (%) - USP <1216>
    friability_mean: float = 0.3
    friability_std: float = 0.1
    friability_limit: float = 1.0  # Máximo 1%
    
    # Tiempo de desintegración (minutos) - USP <701>
    disintegration_mean: float = 8.0
    disintegration_std: float = 2.0
    disintegration_limit: float = 30.0  # Máximo 30 min
    
    # Disolución (%) - USP <711>
    dissolution_mean: float = 92.0
    dissolution_std: float = 4.0
    dissolution_limit: float = 80.0  # Mínimo Q=80%
    
    # Uniformidad de contenido (%) - USP <905>
    content_uniformity_mean: float = 100.0
    content_uniformity_std: float = 2.5
    content_uniformity_limits: Tuple[float, float] = (85.0, 115.0)
    
    # Espesor (mm)
    thickness_mean: float = 5.5
    thickness_std: float = 0.15
    thickness_tolerance: float = 0.05  # ±5%


@dataclass
class EnvironmentalConfig:
    """Configuración para monitoreo ambiental (salas limpias ISO)"""
    
    # Partículas ≥0.5μm (partículas/m³) - ISO 14644-1
    particles_05_mean: float = 2500.0
    particles_05_std: float = 800.0
    particles_05_limits: Dict[str, float] = field(default_factory=lambda: {
        "ISO_7": 352000,
        "ISO_8": 3520000
    })
    
    # Partículas ≥5.0μm (partículas/m³)
    particles_5_mean: float = 15.0
    particles_5_std: float = 8.0
    particles_5_limits: Dict[str, float] = field(default_factory=lambda: {
        "ISO_7": 2930,
        "ISO_8": 29300
    })
    
    # Temperatura (°C) - GMP
    temperature_mean: float = 21.0
    temperature_std: float = 1.0
    temperature_limits: Tuple[float, float] = (18.0, 25.0)
    
    # Humedad Relativa (%)
    humidity_mean: float = 45.0
    humidity_std: float = 5.0
    humidity_limits: Tuple[float, float] = (30.0, 60.0)
    
    # Presión diferencial (Pa)
    pressure_diff_mean: float = 15.0
    pressure_diff_std: float = 3.0
    pressure_diff_min: float = 10.0  # Mínimo requerido
    
    # Conteo microbiano del aire (CFU/m³)
    air_bioburden_mean: float = 5.0
    air_bioburden_std: float = 3.0
    air_bioburden_limits: Dict[str, float] = field(default_factory=lambda: {
        "Grade_C": 100,
        "Grade_D": 200
    })


# =============================================================================
# CONFIGURACIÓN DE MACHINE LEARNING
# =============================================================================

@dataclass
class MLConfig:
    """Configuración para modelos de Machine Learning"""
    
    # Isolation Forest
    isolation_forest: Dict = field(default_factory=lambda: {
        "n_estimators": 100,
        "contamination": 0.05,
        "max_samples": "auto",
        "random_state": 42,
        "n_jobs": -1
    })
    
    # Local Outlier Factor
    lof: Dict = field(default_factory=lambda: {
        "n_neighbors": 20,
        "contamination": 0.05,
        "novelty": True,
        "n_jobs": -1
    })
    
    # One-Class SVM
    ocsvm: Dict = field(default_factory=lambda: {
        "kernel": "rbf",
        "gamma": "scale",
        "nu": 0.05
    })
    
    # Autoencoder
    autoencoder: Dict = field(default_factory=lambda: {
        "encoding_dim": 8,
        "hidden_layers": [32, 16],
        "activation": "relu",
        "epochs": 100,
        "batch_size": 32,
        "validation_split": 0.2
    })
    
    # Umbral de anomalía
    anomaly_threshold: float = 0.05
    
    # Ventana para detección de tendencias
    trend_window: int = 24  # horas


# =============================================================================
# CONFIGURACIÓN DE ALERTAS
# =============================================================================

@dataclass
class AlertConfig:
    """Configuración del sistema de alertas"""
    
    # Umbrales para escalamiento
    critical_multiplier: float = 1.0   # >= 100% del límite
    major_multiplier: float = 0.9      # >= 90% del límite
    minor_multiplier: float = 0.8      # >= 80% del límite
    
    # Configuración de notificaciones
    email_enabled: bool = True
    sms_enabled: bool = False
    dashboard_enabled: bool = True
    
    # Tiempo de retención de alertas (días)
    retention_days: int = 90
    
    # Configuración de agregación
    aggregation_window: int = 5  # minutos
    min_occurrences: int = 3     # mínimo de ocurrencias para confirmar


# =============================================================================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# =============================================================================

@dataclass
class SystemConfig:
    """Configuración general del sistema de monitoreo"""
    
    # Información del sistema
    system_name: str = "PharmaMon Pro"
    version: str = "2.0.0"
    facility_name: str = "Planta Farmacéutica GMP"
    
    # Configuración de datos
    data_frequency: str = "1min"  # Frecuencia de muestreo
    data_retention_days: int = 365
    
    # Configuración de simulación
    simulation_days: int = 30
    anomaly_rate: float = 0.03  # 3% de datos anómalos
    
    # Semilla para reproducibilidad
    random_seed: int = 42
    
    # Rutas de archivos
    output_dir: str = "output"
    models_dir: str = "models"
    logs_dir: str = "logs"
    
    # Componentes
    water_config: WaterSystemConfig = field(default_factory=WaterSystemConfig)
    tablet_config: TabletProductionConfig = field(default_factory=TabletProductionConfig)
    environmental_config: EnvironmentalConfig = field(default_factory=EnvironmentalConfig)
    ml_config: MLConfig = field(default_factory=MLConfig)
    alert_config: AlertConfig = field(default_factory=AlertConfig)


# =============================================================================
# INSTANCIA GLOBAL DE CONFIGURACIÓN
# =============================================================================

def get_config() -> SystemConfig:
    """Obtiene la configuración del sistema"""
    np.random.seed(42)
    return SystemConfig()


# Constantes de colores para visualización
COLORS = {
    "primary": "#0066CC",
    "secondary": "#00A3E0",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    "dark": "#343A40",
    "light": "#F8F9FA",
    "water": "#00BCD4",
    "tablet": "#9C27B0",
    "environment": "#4CAF50"
}

# Mapeo de severidad a colores
SEVERITY_COLORS = {
    AlertSeverity.CRITICAL: "#DC3545",
    AlertSeverity.MAJOR: "#FD7E14",
    AlertSeverity.MINOR: "#FFC107",
    AlertSeverity.INFO: "#17A2B8"
}
