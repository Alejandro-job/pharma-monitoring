"""
Generador de Datos Sintéticos para Sistema Farmacéutico
========================================================
Autor: [Tu Nombre]
Descripción: Genera datos sintéticos realistas para tres fuentes:
             - Sistema de agua purificada
             - Producción de tabletas
             - Monitoreo ambiental
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List
from scipy import stats
from dataclasses import dataclass

from config import (
    SystemConfig, 
    WaterSystemConfig,
    TabletProductionConfig,
    EnvironmentalConfig,
    DataSource,
    get_config
)


class DataGenerator:
    """
    Generador de datos sintéticos para simulación farmacéutica.
    
    Implementa patrones realistas incluyendo:
    - Variación diurna y estacional
    - Correlaciones entre variables
    - Anomalías inyectadas de forma controlada
    - Drift gradual de procesos
    """
    
    def __init__(self, config: Optional[SystemConfig] = None):
        """
        Inicializa el generador de datos.
        
        Args:
            config: Configuración del sistema. Si es None, usa configuración por defecto.
        """
        self.config = config or get_config()
        np.random.seed(self.config.random_seed)
        
    def _generate_timestamps(
        self, 
        days: int, 
        freq: str = "1min"
    ) -> pd.DatetimeIndex:
        """
        Genera índice temporal para los datos.
        
        Args:
            days: Número de días a simular
            freq: Frecuencia de muestreo
            
        Returns:
            DatetimeIndex con las marcas temporales
        """
        start = datetime.now() - timedelta(days=days)
        periods = int(pd.Timedelta(days=days) / pd.Timedelta(freq))
        return pd.date_range(start=start, periods=periods, freq=freq)
    
    def _add_temporal_patterns(
        self, 
        base_values: np.ndarray,
        timestamps: pd.DatetimeIndex,
        daily_amplitude: float = 0.1,
        weekly_amplitude: float = 0.05
    ) -> np.ndarray:
        """
        Añade patrones temporales realistas a los datos.
        
        Args:
            base_values: Valores base generados
            timestamps: Índice temporal
            daily_amplitude: Amplitud de variación diaria
            weekly_amplitude: Amplitud de variación semanal
            
        Returns:
            Valores con patrones temporales aplicados
        """
        hours = timestamps.hour.values
        days = timestamps.dayofweek.values
        
        # Patrón diurno (sinusoidal)
        daily_pattern = daily_amplitude * np.sin(2 * np.pi * hours / 24)
        
        # Patrón semanal (menor actividad en fines de semana)
        weekly_pattern = weekly_amplitude * np.where(days >= 5, -0.5, 0.1)
        
        # Aplicar patrones
        mean_value = np.mean(base_values)
        return base_values + mean_value * (daily_pattern + weekly_pattern)
    
    def _inject_anomalies(
        self,
        data: np.ndarray,
        anomaly_rate: float,
        anomaly_magnitude: float = 3.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Inyecta anomalías controladas en los datos.
        
        Args:
            data: Datos originales
            anomaly_rate: Proporción de anomalías a inyectar
            anomaly_magnitude: Magnitud de las anomalías (en desviaciones estándar)
            
        Returns:
            Tupla con (datos con anomalías, máscara de anomalías)
        """
        n = len(data)
        anomaly_mask = np.random.random(n) < anomaly_rate
        anomaly_indices = np.where(anomaly_mask)[0]
        
        data_with_anomalies = data.copy()
        std = np.std(data)
        
        for idx in anomaly_indices:
            # Diferentes tipos de anomalías
            anomaly_type = np.random.choice(['spike', 'drift', 'shift'])
            
            if anomaly_type == 'spike':
                # Pico repentino
                direction = np.random.choice([-1, 1])
                data_with_anomalies[idx] += direction * anomaly_magnitude * std
                
            elif anomaly_type == 'drift':
                # Drift gradual
                drift_length = min(10, n - idx)
                drift = np.linspace(0, anomaly_magnitude * std, drift_length)
                end_idx = min(idx + drift_length, n)
                data_with_anomalies[idx:end_idx] += drift[:end_idx-idx]
                
            else:  # shift
                # Cambio de nivel
                shift_length = min(5, n - idx)
                end_idx = min(idx + shift_length, n)
                data_with_anomalies[idx:end_idx] += anomaly_magnitude * std * 0.5
        
        return data_with_anomalies, anomaly_mask
    
    def generate_water_data(
        self,
        days: Optional[int] = None,
        include_anomalies: bool = True
    ) -> pd.DataFrame:
        """
        Genera datos del sistema de agua purificada.
        
        Parámetros monitoreados:
        - Conductividad (μS/cm)
        - TOC - Carbono Orgánico Total (ppb)
        - pH
        - Temperatura (°C)
        - Endotoxinas (EU/mL)
        - Conteo microbiano (CFU/mL)
        
        Args:
            days: Número de días a simular
            include_anomalies: Si se deben incluir anomalías
            
        Returns:
            DataFrame con datos del sistema de agua
        """
        days = days or self.config.simulation_days
        cfg = self.config.water_config
        timestamps = self._generate_timestamps(days)
        n = len(timestamps)
        
        # Generar datos base
        data = {
            'timestamp': timestamps,
            'source': DataSource.WATER.value
        }
        
        # Conductividad
        conductivity = np.random.normal(cfg.conductivity_mean, cfg.conductivity_std, n)
        conductivity = np.clip(conductivity, 0.1, None)
        conductivity = self._add_temporal_patterns(conductivity, timestamps, 0.08, 0.03)
        
        # TOC
        toc = np.random.normal(cfg.toc_mean, cfg.toc_std, n)
        toc = np.clip(toc, 50, None)
        toc = self._add_temporal_patterns(toc, timestamps, 0.1, 0.05)
        
        # pH (correlacionado negativamente con conductividad)
        ph_noise = np.random.normal(0, cfg.ph_std * 0.5, n)
        ph = cfg.ph_mean - 0.3 * (conductivity - cfg.conductivity_mean) / cfg.conductivity_std + ph_noise
        ph = np.clip(ph, 5.5, 8.5)
        
        # Temperatura
        temperature = np.random.normal(cfg.temperature_mean, cfg.temperature_std, n)
        temperature = self._add_temporal_patterns(temperature, timestamps, 0.15, 0.08)
        
        # Endotoxinas (distribución log-normal)
        endotoxin = np.random.lognormal(
            np.log(cfg.endotoxin_mean), 
            cfg.endotoxin_std / cfg.endotoxin_mean, 
            n
        )
        endotoxin = np.clip(endotoxin, 0.001, None)
        
        # Conteo microbiano (distribución Poisson)
        bioburden = np.random.poisson(cfg.bioburden_mean, n).astype(float)
        
        # Inyectar anomalías si es necesario
        anomaly_masks = {}
        if include_anomalies:
            conductivity, anomaly_masks['conductivity'] = self._inject_anomalies(
                conductivity, self.config.anomaly_rate
            )
            toc, anomaly_masks['toc'] = self._inject_anomalies(
                toc, self.config.anomaly_rate
            )
            ph, anomaly_masks['ph'] = self._inject_anomalies(
                ph, self.config.anomaly_rate * 0.5
            )
        
        # Construir DataFrame
        data['conductivity_uS_cm'] = np.round(conductivity, 3)
        data['toc_ppb'] = np.round(toc, 1)
        data['ph'] = np.round(ph, 2)
        data['temperature_C'] = np.round(temperature, 1)
        data['endotoxin_EU_mL'] = np.round(endotoxin, 4)
        data['bioburden_CFU_mL'] = bioburden.astype(int)
        
        # Añadir columna de anomalía conocida
        if include_anomalies:
            combined_mask = np.zeros(n, dtype=bool)
            for mask in anomaly_masks.values():
                combined_mask |= mask
            data['is_anomaly'] = combined_mask
        else:
            data['is_anomaly'] = False
        
        df = pd.DataFrame(data)
        
        # Añadir métricas derivadas
        df['conductivity_pct_limit'] = (df['conductivity_uS_cm'] / cfg.conductivity_limit) * 100
        df['toc_pct_limit'] = (df['toc_ppb'] / cfg.toc_limit) * 100
        
        return df
    
    def generate_tablet_data(
        self,
        days: Optional[int] = None,
        include_anomalies: bool = True
    ) -> pd.DataFrame:
        """
        Genera datos de producción de tabletas.
        
        Parámetros monitoreados:
        - Peso (mg)
        - Dureza (N)
        - Friabilidad (%)
        - Tiempo de desintegración (min)
        - Disolución (%)
        - Uniformidad de contenido (%)
        - Espesor (mm)
        
        Args:
            days: Número de días a simular
            include_anomalies: Si se deben incluir anomalías
            
        Returns:
            DataFrame con datos de producción
        """
        days = days or self.config.simulation_days
        cfg = self.config.tablet_config
        
        # Frecuencia de muestreo para producción (cada 15 minutos)
        timestamps = self._generate_timestamps(days, freq="15min")
        n = len(timestamps)
        
        data = {
            'timestamp': timestamps,
            'source': DataSource.TABLETS.value
        }
        
        # Peso de tableta
        weight = np.random.normal(cfg.weight_target, cfg.weight_std, n)
        weight = self._add_temporal_patterns(weight, timestamps, 0.005, 0.002)
        
        # Dureza (correlacionada con el peso)
        hardness_noise = np.random.normal(0, cfg.hardness_std * 0.7, n)
        hardness = cfg.hardness_mean + 2 * (weight - cfg.weight_target) + hardness_noise
        hardness = np.clip(hardness, 50, 150)
        
        # Friabilidad (inversamente correlacionada con dureza)
        friability_noise = np.random.normal(0, cfg.friability_std * 0.5, n)
        friability = cfg.friability_mean - 0.002 * (hardness - cfg.hardness_mean) + friability_noise
        friability = np.clip(friability, 0.05, None)
        
        # Desintegración
        disintegration = np.random.normal(cfg.disintegration_mean, cfg.disintegration_std, n)
        disintegration = np.clip(disintegration, 1, None)
        
        # Disolución
        dissolution = np.random.normal(cfg.dissolution_mean, cfg.dissolution_std, n)
        dissolution = np.clip(dissolution, 0, 100)
        
        # Uniformidad de contenido
        content_uniformity = np.random.normal(
            cfg.content_uniformity_mean, 
            cfg.content_uniformity_std, 
            n
        )
        
        # Espesor
        thickness = np.random.normal(cfg.thickness_mean, cfg.thickness_std, n)
        thickness = np.clip(thickness, 4.0, 7.0)
        
        # Número de lote (cambia cada 8 horas)
        batch_numbers = []
        current_batch = 1
        for i, ts in enumerate(timestamps):
            if i > 0 and i % 32 == 0:  # 32 * 15min = 8 horas
                current_batch += 1
            batch_numbers.append(f"LOT-{ts.strftime('%Y%m%d')}-{current_batch:03d}")
        
        # Inyectar anomalías
        anomaly_masks = {}
        if include_anomalies:
            weight, anomaly_masks['weight'] = self._inject_anomalies(
                weight, self.config.anomaly_rate, 2.5
            )
            hardness, anomaly_masks['hardness'] = self._inject_anomalies(
                hardness, self.config.anomaly_rate, 2.0
            )
            dissolution, anomaly_masks['dissolution'] = self._inject_anomalies(
                dissolution, self.config.anomaly_rate * 0.5, -2.0
            )
        
        # Construir DataFrame
        data['batch_number'] = batch_numbers
        data['weight_mg'] = np.round(weight, 2)
        data['hardness_N'] = np.round(hardness, 1)
        data['friability_pct'] = np.round(friability, 3)
        data['disintegration_min'] = np.round(disintegration, 1)
        data['dissolution_pct'] = np.round(dissolution, 1)
        data['content_uniformity_pct'] = np.round(content_uniformity, 2)
        data['thickness_mm'] = np.round(thickness, 2)
        
        if include_anomalies:
            combined_mask = np.zeros(n, dtype=bool)
            for mask in anomaly_masks.values():
                combined_mask |= mask
            data['is_anomaly'] = combined_mask
        else:
            data['is_anomaly'] = False
        
        df = pd.DataFrame(data)
        
        # Métricas de calidad
        weight_lower = cfg.weight_target * (1 - cfg.weight_tolerance)
        weight_upper = cfg.weight_target * (1 + cfg.weight_tolerance)
        df['weight_in_spec'] = (df['weight_mg'] >= weight_lower) & (df['weight_mg'] <= weight_upper)
        df['hardness_in_spec'] = (df['hardness_N'] >= cfg.hardness_limits[0]) & (df['hardness_N'] <= cfg.hardness_limits[1])
        df['dissolution_pass'] = df['dissolution_pct'] >= cfg.dissolution_limit
        
        return df
    
    def generate_environmental_data(
        self,
        days: Optional[int] = None,
        include_anomalies: bool = True
    ) -> pd.DataFrame:
        """
        Genera datos de monitoreo ambiental.
        
        Parámetros monitoreados:
        - Partículas ≥0.5μm (partículas/m³)
        - Partículas ≥5.0μm (partículas/m³)
        - Temperatura (°C)
        - Humedad relativa (%)
        - Presión diferencial (Pa)
        - Conteo microbiano del aire (CFU/m³)
        
        Args:
            days: Número de días a simular
            include_anomalies: Si se deben incluir anomalías
            
        Returns:
            DataFrame con datos ambientales
        """
        days = days or self.config.simulation_days
        cfg = self.config.environmental_config
        
        # Frecuencia de muestreo (cada 5 minutos para ambiente)
        timestamps = self._generate_timestamps(days, freq="5min")
        n = len(timestamps)
        
        data = {
            'timestamp': timestamps,
            'source': DataSource.ENVIRONMENT.value
        }
        
        # Zonas de monitoreo
        zones = ['Zone_A', 'Zone_B', 'Zone_C', 'Clean_Corridor']
        zone_assignment = np.random.choice(zones, n)
        
        # Partículas 0.5μm
        particles_05 = np.random.lognormal(
            np.log(cfg.particles_05_mean),
            0.3,
            n
        )
        particles_05 = self._add_temporal_patterns(particles_05, timestamps, 0.2, 0.1)
        
        # Partículas 5.0μm (correlacionadas con 0.5μm)
        particles_5 = particles_05 * 0.01 + np.random.lognormal(
            np.log(cfg.particles_5_mean),
            0.4,
            n
        )
        
        # Temperatura
        temperature = np.random.normal(cfg.temperature_mean, cfg.temperature_std, n)
        temperature = self._add_temporal_patterns(temperature, timestamps, 0.1, 0.05)
        
        # Humedad (correlacionada inversamente con temperatura)
        humidity_noise = np.random.normal(0, cfg.humidity_std * 0.5, n)
        humidity = cfg.humidity_mean - 2 * (temperature - cfg.temperature_mean) + humidity_noise
        humidity = np.clip(humidity, 20, 70)
        
        # Presión diferencial
        pressure_diff = np.random.normal(cfg.pressure_diff_mean, cfg.pressure_diff_std, n)
        pressure_diff = np.clip(pressure_diff, 5, 30)
        
        # Conteo microbiano del aire (distribución Poisson)
        air_bioburden = np.random.poisson(cfg.air_bioburden_mean, n).astype(float)
        
        # Inyectar anomalías
        anomaly_masks = {}
        if include_anomalies:
            particles_05, anomaly_masks['particles_05'] = self._inject_anomalies(
                particles_05, self.config.anomaly_rate, 4.0
            )
            temperature, anomaly_masks['temperature'] = self._inject_anomalies(
                temperature, self.config.anomaly_rate * 0.5, 2.5
            )
            pressure_diff, anomaly_masks['pressure'] = self._inject_anomalies(
                pressure_diff, self.config.anomaly_rate, -2.0
            )
        
        # Construir DataFrame
        data['zone'] = zone_assignment
        data['particles_05um_per_m3'] = np.round(particles_05, 0).astype(int)
        data['particles_5um_per_m3'] = np.round(particles_5, 0).astype(int)
        data['temperature_C'] = np.round(temperature, 1)
        data['humidity_pct'] = np.round(humidity, 1)
        data['pressure_diff_Pa'] = np.round(pressure_diff, 1)
        data['air_bioburden_CFU_m3'] = air_bioburden.astype(int)
        
        if include_anomalies:
            combined_mask = np.zeros(n, dtype=bool)
            for mask in anomaly_masks.values():
                combined_mask |= mask
            data['is_anomaly'] = combined_mask
        else:
            data['is_anomaly'] = False
        
        df = pd.DataFrame(data)
        
        # Clasificación ISO
        iso7_limit = cfg.particles_05_limits['ISO_7']
        iso8_limit = cfg.particles_05_limits['ISO_8']
        df['iso_classification'] = np.where(
            df['particles_05um_per_m3'] <= iso7_limit, 'ISO_7',
            np.where(df['particles_05um_per_m3'] <= iso8_limit, 'ISO_8', 'Out_of_Spec')
        )
        
        # Conformidad de condiciones
        df['temp_in_spec'] = (df['temperature_C'] >= cfg.temperature_limits[0]) & \
                             (df['temperature_C'] <= cfg.temperature_limits[1])
        df['humidity_in_spec'] = (df['humidity_pct'] >= cfg.humidity_limits[0]) & \
                                 (df['humidity_pct'] <= cfg.humidity_limits[1])
        df['pressure_compliant'] = df['pressure_diff_Pa'] >= cfg.pressure_diff_min
        
        return df
    
    def generate_all_data(
        self,
        days: Optional[int] = None,
        include_anomalies: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Genera datos de todas las fuentes.
        
        Args:
            days: Número de días a simular
            include_anomalies: Si se deben incluir anomalías
            
        Returns:
            Diccionario con DataFrames de cada fuente
        """
        return {
            'water': self.generate_water_data(days, include_anomalies),
            'tablets': self.generate_tablet_data(days, include_anomalies),
            'environment': self.generate_environmental_data(days, include_anomalies)
        }
    
    def export_to_csv(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: str = "data"
    ) -> List[str]:
        """
        Exporta los datos a archivos CSV.
        
        Args:
            data: Diccionario con los DataFrames
            output_dir: Directorio de salida
            
        Returns:
            Lista de rutas de archivos creados
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        files_created = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, df in data.items():
            filepath = os.path.join(output_dir, f"{name}_data_{timestamp}.csv")
            df.to_csv(filepath, index=False)
            files_created.append(filepath)
            print(f"Exportado: {filepath} ({len(df)} registros)")
        
        return files_created


# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR DE DATOS FARMACÉUTICOS")
    print("=" * 60)
    
    # Inicializar generador
    generator = DataGenerator()
    
    # Generar todos los datos
    print("\nGenerando datos sintéticos...")
    data = generator.generate_all_data(days=30)
    
    # Mostrar resumen
    for source, df in data.items():
        print(f"\n{source.upper()}:")
        print(f"  - Registros: {len(df):,}")
        print(f"  - Columnas: {list(df.columns)}")
        print(f"  - Anomalías: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
        print(f"  - Rango temporal: {df['timestamp'].min()} a {df['timestamp'].max()}")
    
    # Exportar datos
    print("\nExportando datos...")
    files = generator.export_to_csv(data)
    
    print("\n" + "=" * 60)
    print("Generación completada exitosamente")
    print("=" * 60)
