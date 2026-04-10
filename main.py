"""
================================================================================
PHARMA INDUSTRIAL MONITORING SYSTEM - MAIN EXECUTION
================================================================================
Script principal que orquesta todo el sistema de monitoreo farmacéutico.
Ejecuta la generación de datos, análisis, modelos ML y sistema de alertas.

Autor: [Tu Nombre]
Versión: 1.0.0
================================================================================
"""

import os
import sys
import json
import warnings
from datetime import datetime
from pathlib import Path

# Configurar warnings
warnings.filterwarnings('ignore')

# Importaciones del sistema
from config import (
    SystemConfig, WaterSystemConfig, TabletProductionConfig,
    EnvironmentalConfig, AlertConfig, MLConfig
)
from data_generator import (
    WaterSystemGenerator, TabletProductionGenerator,
    EnvironmentalGenerator, DataGenerationOrchestrator
)
from analysis import (
    WaterAnalyzer, TabletAnalyzer, EnvironmentalAnalyzer,
    CrossSystemAnalyzer, AnalysisOrchestrator
)
from ml_models import (
    AnomalyDetectionPipeline, WaterAnomalyDetector,
    TabletAnomalyDetector, EnvironmentalAnomalyDetector,
    EnsembleAnomalyDetector
)
from alerts import (
    AlertEngine, AlertNotifier, AlertDashboard,
    ComplianceMonitor
)


class PharmaMonitoringSystem:
    """
    Sistema principal de monitoreo farmacéutico industrial.
    Integra todos los componentes del sistema.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el sistema de monitoreo.
        
        Args:
            output_dir: Directorio para guardar resultados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectorios
        self.data_dir = self.output_dir / "data"
        self.analysis_dir = self.output_dir / "analysis"
        self.models_dir = self.output_dir / "models"
        self.reports_dir = self.output_dir / "reports"
        self.alerts_dir = self.output_dir / "alerts"
        
        for dir_path in [self.data_dir, self.analysis_dir, 
                         self.models_dir, self.reports_dir, self.alerts_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Componentes del sistema
        self.data_orchestrator = None
        self.analysis_orchestrator = None
        self.ml_pipeline = None
        self.alert_engine = None
        self.compliance_monitor = None
        
        # Datos generados
        self.water_data = None
        self.tablet_data = None
        self.environmental_data = None
        
        # Resultados
        self.analysis_results = {}
        self.anomaly_results = {}
        self.alerts = []
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa todos los componentes del sistema."""
        print("=" * 70)
        print("PHARMA INDUSTRIAL MONITORING SYSTEM")
        print("=" * 70)
        print(f"\nInicializando sistema... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        
        # Generadores de datos
        self.data_orchestrator = DataGenerationOrchestrator(
            water_config=WaterSystemConfig(),
            tablet_config=TabletProductionConfig(),
            environmental_config=EnvironmentalConfig()
        )
        print("[OK] Generadores de datos inicializados")
        
        # Analizadores
        self.analysis_orchestrator = AnalysisOrchestrator()
        print("[OK] Analizadores estadísticos inicializados")
        
        # Pipeline de ML
        self.ml_pipeline = AnomalyDetectionPipeline(
            config=MLConfig(),
            output_dir=str(self.models_dir)
        )
        print("[OK] Pipeline de Machine Learning inicializado")
        
        # Motor de alertas
        self.alert_engine = AlertEngine(config=AlertConfig())
        print("[OK] Motor de alertas inicializado")
        
        # Monitor de cumplimiento
        self.compliance_monitor = ComplianceMonitor()
        print("[OK] Monitor de cumplimiento GMP inicializado")
        
        print("\n" + "-" * 70)
    
    def generate_data(self, days: int = 30, 
                      samples_per_day: int = 24,
                      anomaly_rate: float = 0.05) -> dict:
        """
        Genera datos sintéticos para todos los sistemas.
        
        Args:
            days: Número de días a simular
            samples_per_day: Muestras por día
            anomaly_rate: Tasa de anomalías a inyectar
            
        Returns:
            Diccionario con los DataFrames generados
        """
        print(f"\n[FASE 1] GENERACIÓN DE DATOS SINTÉTICOS")
        print("-" * 50)
        print(f"  - Período: {days} días")
        print(f"  - Muestras/día: {samples_per_day}")
        print(f"  - Tasa de anomalías: {anomaly_rate * 100:.1f}%")
        
        # Generar datos
        all_data = self.data_orchestrator.generate_all(
            days=days,
            samples_per_day=samples_per_day,
            anomaly_rate=anomaly_rate
        )
        
        self.water_data = all_data['water']
        self.tablet_data = all_data['tablet']
        self.environmental_data = all_data['environmental']
        
        # Guardar datos
        self.water_data.to_csv(self.data_dir / "water_system.csv", index=False)
        self.tablet_data.to_csv(self.data_dir / "tablet_production.csv", index=False)
        self.environmental_data.to_csv(self.data_dir / "environmental.csv", index=False)
        
        print(f"\n  [OK] Sistema de Agua: {len(self.water_data):,} registros")
        print(f"  [OK] Producción de Tabletas: {len(self.tablet_data):,} registros")
        print(f"  [OK] Monitoreo Ambiental: {len(self.environmental_data):,} registros")
        print(f"\n  Datos guardados en: {self.data_dir}")
        
        return all_data
    
    def run_analysis(self) -> dict:
        """
        Ejecuta análisis exploratorio completo.
        
        Returns:
            Diccionario con resultados del análisis
        """
        print(f"\n[FASE 2] ANÁLISIS EXPLORATORIO DE DATOS")
        print("-" * 50)
        
        if self.water_data is None:
            raise ValueError("Debe generar datos primero con generate_data()")
        
        # Análisis por sistema
        results = self.analysis_orchestrator.run_full_analysis(
            water_data=self.water_data,
            tablet_data=self.tablet_data,
            environmental_data=self.environmental_data,
            output_dir=str(self.analysis_dir)
        )
        
        self.analysis_results = results
        
        # Mostrar resumen
        print("\n  RESUMEN DEL ANÁLISIS:")
        print("  " + "-" * 40)
        
        for system_name, system_results in results.items():
            if 'statistics' in system_results:
                stats = system_results['statistics']
                print(f"\n  [{system_name.upper()}]")
                for var, var_stats in list(stats.items())[:3]:
                    print(f"    - {var}: μ={var_stats.get('mean', 0):.3f}, "
                          f"σ={var_stats.get('std', 0):.3f}")
        
        # Guardar resultados
        with open(self.analysis_dir / "analysis_summary.json", 'w') as f:
            # Convertir a serializable
            serializable_results = self._make_serializable(results)
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"\n  [OK] Análisis completado y guardado en: {self.analysis_dir}")
        
        return results
    
    def train_models(self) -> dict:
        """
        Entrena modelos de detección de anomalías.
        
        Returns:
            Diccionario con métricas de los modelos
        """
        print(f"\n[FASE 3] ENTRENAMIENTO DE MODELOS ML")
        print("-" * 50)
        
        if self.water_data is None:
            raise ValueError("Debe generar datos primero con generate_data()")
        
        # Preparar datos para cada sistema
        datasets = {
            'water': self.water_data,
            'tablet': self.tablet_data,
            'environmental': self.environmental_data
        }
        
        all_metrics = {}
        
        for system_name, data in datasets.items():
            print(f"\n  Entrenando modelos para: {system_name.upper()}")
            
            # Seleccionar columnas numéricas
            numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
            feature_cols = [c for c in numeric_cols if c not in 
                          ['is_anomaly', 'anomaly_type', 'batch_number']]
            
            if len(feature_cols) < 2:
                print(f"    [SKIP] Insuficientes características")
                continue
            
            # Entrenar pipeline
            metrics = self.ml_pipeline.train(
                data=data,
                feature_columns=feature_cols,
                system_name=system_name
            )
            
            all_metrics[system_name] = metrics
            
            # Mostrar métricas
            for model_name, model_metrics in metrics.items():
                if isinstance(model_metrics, dict) and 'f1_score' in model_metrics:
                    print(f"    - {model_name}: F1={model_metrics['f1_score']:.3f}, "
                          f"Precision={model_metrics['precision']:.3f}")
        
        self.anomaly_results['metrics'] = all_metrics
        
        # Guardar métricas
        with open(self.models_dir / "model_metrics.json", 'w') as f:
            json.dump(all_metrics, f, indent=2, default=str)
        
        print(f"\n  [OK] Modelos entrenados y guardados en: {self.models_dir}")
        
        return all_metrics
    
    def detect_anomalies(self) -> dict:
        """
        Ejecuta detección de anomalías en todos los sistemas.
        
        Returns:
            Diccionario con anomalías detectadas
        """
        print(f"\n[FASE 4] DETECCIÓN DE ANOMALÍAS")
        print("-" * 50)
        
        datasets = {
            'water': self.water_data,
            'tablet': self.tablet_data,
            'environmental': self.environmental_data
        }
        
        all_anomalies = {}
        
        for system_name, data in datasets.items():
            print(f"\n  Analizando: {system_name.upper()}")
            
            # Predecir anomalías
            predictions = self.ml_pipeline.predict(
                data=data,
                system_name=system_name
            )
            
            if predictions is not None:
                anomaly_count = (predictions == -1).sum()
                anomaly_pct = anomaly_count / len(predictions) * 100
                
                all_anomalies[system_name] = {
                    'total_samples': len(predictions),
                    'anomalies_detected': int(anomaly_count),
                    'anomaly_percentage': float(anomaly_pct),
                    'predictions': predictions.tolist()
                }
                
                print(f"    - Total muestras: {len(predictions):,}")
                print(f"    - Anomalías detectadas: {anomaly_count:,} ({anomaly_pct:.2f}%)")
        
        self.anomaly_results['detections'] = all_anomalies
        
        # Guardar resultados
        with open(self.models_dir / "anomaly_detections.json", 'w') as f:
            json.dump(all_anomalies, f, indent=2, default=str)
        
        print(f"\n  [OK] Detección completada")
        
        return all_anomalies
    
    def generate_alerts(self) -> list:
        """
        Genera alertas basadas en umbrales y predicciones ML.
        
        Returns:
            Lista de alertas generadas
        """
        print(f"\n[FASE 5] GENERACIÓN DE ALERTAS")
        print("-" * 50)
        
        all_alerts = []
        
        # Alertas basadas en umbrales
        datasets = {
            'water': (self.water_data, WaterSystemConfig()),
            'tablet': (self.tablet_data, TabletProductionConfig()),
            'environmental': (self.environmental_data, EnvironmentalConfig())
        }
        
        for system_name, (data, config) in datasets.items():
            alerts = self.alert_engine.evaluate_thresholds(
                data=data,
                config=config,
                system_name=system_name
            )
            all_alerts.extend(alerts)
        
        # Alertas basadas en ML
        if 'detections' in self.anomaly_results:
            ml_alerts = self.alert_engine.evaluate_ml_predictions(
                self.anomaly_results['detections']
            )
            all_alerts.extend(ml_alerts)
        
        self.alerts = all_alerts
        
        # Clasificar por severidad
        critical = sum(1 for a in all_alerts if a.get('severity') == 'CRITICAL')
        major = sum(1 for a in all_alerts if a.get('severity') == 'MAJOR')
        minor = sum(1 for a in all_alerts if a.get('severity') == 'MINOR')
        
        print(f"\n  RESUMEN DE ALERTAS:")
        print(f"    - CRÍTICAS: {critical}")
        print(f"    - MAYORES: {major}")
        print(f"    - MENORES: {minor}")
        print(f"    - TOTAL: {len(all_alerts)}")
        
        # Guardar alertas
        with open(self.alerts_dir / "alerts.json", 'w') as f:
            json.dump(all_alerts, f, indent=2, default=str)
        
        print(f"\n  [OK] Alertas guardadas en: {self.alerts_dir}")
        
        return all_alerts
    
    def check_compliance(self) -> dict:
        """
        Verifica cumplimiento GMP/FDA.
        
        Returns:
            Informe de cumplimiento
        """
        print(f"\n[FASE 6] VERIFICACIÓN DE CUMPLIMIENTO GMP")
        print("-" * 50)
        
        compliance_report = self.compliance_monitor.evaluate(
            water_data=self.water_data,
            tablet_data=self.tablet_data,
            environmental_data=self.environmental_data,
            alerts=self.alerts
        )
        
        # Mostrar resumen
        print(f"\n  ESTADO DE CUMPLIMIENTO:")
        print(f"    - Puntuación general: {compliance_report.get('overall_score', 0):.1f}%")
        print(f"    - Estado: {compliance_report.get('status', 'UNKNOWN')}")
        
        if 'violations' in compliance_report:
            print(f"    - Violaciones: {len(compliance_report['violations'])}")
        
        # Guardar informe
        with open(self.reports_dir / "compliance_report.json", 'w') as f:
            json.dump(compliance_report, f, indent=2, default=str)
        
        return compliance_report
    
    def generate_reports(self) -> dict:
        """
        Genera informes ejecutivos y técnicos.
        
        Returns:
            Rutas a los informes generados
        """
        print(f"\n[FASE 7] GENERACIÓN DE INFORMES")
        print("-" * 50)
        
        report_paths = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Informe ejecutivo
        executive_report = self._generate_executive_report()
        exec_path = self.reports_dir / f"executive_report_{timestamp}.json"
        with open(exec_path, 'w') as f:
            json.dump(executive_report, f, indent=2, default=str)
        report_paths['executive'] = str(exec_path)
        print(f"  [OK] Informe ejecutivo: {exec_path.name}")
        
        # Informe técnico
        technical_report = self._generate_technical_report()
        tech_path = self.reports_dir / f"technical_report_{timestamp}.json"
        with open(tech_path, 'w') as f:
            json.dump(technical_report, f, indent=2, default=str)
        report_paths['technical'] = str(tech_path)
        print(f"  [OK] Informe técnico: {tech_path.name}")
        
        # Informe de calidad
        quality_report = self._generate_quality_report()
        qual_path = self.reports_dir / f"quality_report_{timestamp}.json"
        with open(qual_path, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        report_paths['quality'] = str(qual_path)
        print(f"  [OK] Informe de calidad: {qual_path.name}")
        
        return report_paths
    
    def _generate_executive_report(self) -> dict:
        """Genera informe ejecutivo."""
        return {
            'report_type': 'EXECUTIVE SUMMARY',
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': self.water_data['timestamp'].min() if self.water_data is not None else None,
                'end': self.water_data['timestamp'].max() if self.water_data is not None else None
            },
            'key_metrics': {
                'total_samples_analyzed': sum([
                    len(self.water_data) if self.water_data is not None else 0,
                    len(self.tablet_data) if self.tablet_data is not None else 0,
                    len(self.environmental_data) if self.environmental_data is not None else 0
                ]),
                'anomalies_detected': self.anomaly_results.get('detections', {}),
                'alerts_generated': len(self.alerts),
                'critical_alerts': sum(1 for a in self.alerts if a.get('severity') == 'CRITICAL')
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_technical_report(self) -> dict:
        """Genera informe técnico."""
        return {
            'report_type': 'TECHNICAL ANALYSIS',
            'generated_at': datetime.now().isoformat(),
            'data_statistics': self.analysis_results,
            'ml_model_performance': self.anomaly_results.get('metrics', {}),
            'anomaly_analysis': self.anomaly_results.get('detections', {}),
            'system_configurations': {
                'water': vars(WaterSystemConfig()),
                'tablet': vars(TabletProductionConfig()),
                'environmental': vars(EnvironmentalConfig())
            }
        }
    
    def _generate_quality_report(self) -> dict:
        """Genera informe de calidad."""
        return {
            'report_type': 'QUALITY ASSURANCE',
            'generated_at': datetime.now().isoformat(),
            'compliance_status': 'EVALUATED',
            'quality_metrics': {
                'cpk_values': self._calculate_cpk_values(),
                'ooe_events': self._count_ooe_events(),
                'oos_events': self._count_oos_events()
            },
            'alerts_by_system': self._categorize_alerts_by_system(),
            'trending_issues': self._identify_trends()
        }
    
    def _generate_recommendations(self) -> list:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Basado en alertas críticas
        critical_alerts = [a for a in self.alerts if a.get('severity') == 'CRITICAL']
        if critical_alerts:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Process Control',
                'recommendation': 'Investigar inmediatamente las alertas críticas detectadas',
                'count': len(critical_alerts)
            })
        
        # Basado en anomalías
        for system, data in self.anomaly_results.get('detections', {}).items():
            if data.get('anomaly_percentage', 0) > 5:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'area': system.upper(),
                    'recommendation': f'Revisar calibración de sensores - tasa de anomalías elevada',
                    'anomaly_rate': f"{data['anomaly_percentage']:.2f}%"
                })
        
        return recommendations
    
    def _calculate_cpk_values(self) -> dict:
        """Calcula valores Cpk para variables críticas."""
        cpk_values = {}
        
        if self.tablet_data is not None:
            for col in ['weight_mg', 'hardness_n', 'thickness_mm']:
                if col in self.tablet_data.columns:
                    data = self.tablet_data[col].dropna()
                    if len(data) > 0:
                        mean = data.mean()
                        std = data.std()
                        # Simulamos límites de especificación
                        usl = mean + 3 * std
                        lsl = mean - 3 * std
                        if std > 0:
                            cpu = (usl - mean) / (3 * std)
                            cpl = (mean - lsl) / (3 * std)
                            cpk_values[col] = min(cpu, cpl)
        
        return cpk_values
    
    def _count_ooe_events(self) -> int:
        """Cuenta eventos fuera de expectativa (OOE)."""
        return sum(1 for a in self.alerts if 'OOE' in a.get('type', ''))
    
    def _count_oos_events(self) -> int:
        """Cuenta eventos fuera de especificación (OOS)."""
        return sum(1 for a in self.alerts if a.get('severity') in ['CRITICAL', 'MAJOR'])
    
    def _categorize_alerts_by_system(self) -> dict:
        """Categoriza alertas por sistema."""
        categories = {}
        for alert in self.alerts:
            system = alert.get('system', 'unknown')
            if system not in categories:
                categories[system] = []
            categories[system].append(alert)
        return {k: len(v) for k, v in categories.items()}
    
    def _identify_trends(self) -> list:
        """Identifica tendencias en los datos."""
        trends = []
        
        # Analizar tendencias temporales simples
        for system_name, data in [('water', self.water_data), 
                                   ('tablet', self.tablet_data),
                                   ('environmental', self.environmental_data)]:
            if data is not None and 'timestamp' in data.columns:
                numeric_cols = data.select_dtypes(include=['float64']).columns[:3]
                for col in numeric_cols:
                    # Calcular tendencia simple
                    first_half = data[col].iloc[:len(data)//2].mean()
                    second_half = data[col].iloc[len(data)//2:].mean()
                    
                    if first_half != 0:
                        change_pct = ((second_half - first_half) / first_half) * 100
                        if abs(change_pct) > 5:
                            trends.append({
                                'system': system_name,
                                'variable': col,
                                'trend': 'INCREASING' if change_pct > 0 else 'DECREASING',
                                'change_percentage': round(change_pct, 2)
                            })
        
        return trends
    
    def _make_serializable(self, obj):
        """Convierte objetos a formato serializable JSON."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return obj
    
    def run_full_pipeline(self, days: int = 30, 
                          samples_per_day: int = 24,
                          anomaly_rate: float = 0.05):
        """
        Ejecuta el pipeline completo del sistema.
        
        Args:
            days: Días a simular
            samples_per_day: Muestras por día
            anomaly_rate: Tasa de anomalías
        """
        start_time = datetime.now()
        
        print("\n" + "=" * 70)
        print("INICIANDO PIPELINE COMPLETO DE MONITOREO FARMACÉUTICO")
        print("=" * 70)
        print(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Fase 1: Generación de datos
            self.generate_data(days, samples_per_day, anomaly_rate)
            
            # Fase 2: Análisis exploratorio
            self.run_analysis()
            
            # Fase 3: Entrenamiento de modelos
            self.train_models()
            
            # Fase 4: Detección de anomalías
            self.detect_anomalies()
            
            # Fase 5: Generación de alertas
            self.generate_alerts()
            
            # Fase 6: Verificación de cumplimiento
            self.check_compliance()
            
            # Fase 7: Generación de informes
            report_paths = self.generate_reports()
            
            # Resumen final
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 70)
            print("PIPELINE COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            print(f"Duración total: {duration:.2f} segundos")
            print(f"Directorio de salida: {self.output_dir}")
            print("\nArchivos generados:")
            print(f"  - Datos: {self.data_dir}")
            print(f"  - Análisis: {self.analysis_dir}")
            print(f"  - Modelos: {self.models_dir}")
            print(f"  - Alertas: {self.alerts_dir}")
            print(f"  - Informes: {self.reports_dir}")
            print("=" * 70)
            
            return {
                'status': 'SUCCESS',
                'duration_seconds': duration,
                'output_directory': str(self.output_dir),
                'report_paths': report_paths
            }
            
        except Exception as e:
            print(f"\n[ERROR] Pipeline fallido: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'FAILED',
                'error': str(e)
            }


def main():
    """Función principal de ejecución."""
    print("\n" + "=" * 70)
    print("  PHARMA INDUSTRIAL MONITORING SYSTEM v1.0")
    print("  Sistema de Monitoreo Farmacéutico Industrial")
    print("=" * 70)
    
    # Crear sistema
    system = PharmaMonitoringSystem(output_dir="pharma_output")
    
    # Ejecutar pipeline completo
    result = system.run_full_pipeline(
        days=30,
        samples_per_day=24,
        anomaly_rate=0.05
    )
    
    if result['status'] == 'SUCCESS':
        print("\n[SUCCESS] Sistema ejecutado correctamente.")
        print("Para visualizar el dashboard, ejecute:")
        print("  streamlit run dashboard.py")
    else:
        print(f"\n[FAILED] Error en la ejecución: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    main()
