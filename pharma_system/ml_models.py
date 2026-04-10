"""
Módulo de Machine Learning para Detección de Anomalías
=======================================================
Autor: [Tu Nombre]
Descripción: Implementación de múltiples algoritmos de ML para
             detección de anomalías en procesos farmacéuticos.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import warnings
import pickle
import os

# Scikit-learn
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report,
    roc_auc_score, average_precision_score
)
from sklearn.decomposition import PCA

# Para el autoencoder
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    warnings.warn("TensorFlow no disponible. Autoencoder deshabilitado.")

from config import get_config, MLConfig

warnings.filterwarnings('ignore')


@dataclass
class AnomalyDetectionResult:
    """Resultado de detección de anomalías"""
    model_name: str
    predictions: np.ndarray
    scores: np.ndarray
    threshold: float
    anomaly_count: int
    anomaly_percentage: float
    training_time: float
    inference_time: float
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModelEnsembleResult:
    """Resultado del ensemble de modelos"""
    individual_results: Dict[str, AnomalyDetectionResult]
    ensemble_predictions: np.ndarray
    ensemble_scores: np.ndarray
    voting_weights: Dict[str, float]
    consensus_threshold: float


class DataPreprocessor:
    """
    Preprocesador de datos para modelos de ML.
    
    Funcionalidades:
    - Normalización y escalado
    - Manejo de valores faltantes
    - Selección de features
    - Reducción de dimensionalidad
    """
    
    def __init__(self, scaling_method: str = 'standard'):
        """
        Inicializa el preprocesador.
        
        Args:
            scaling_method: Método de escalado ('standard', 'minmax', 'robust')
        """
        self.scaling_method = scaling_method
        self.scaler = None
        self.feature_columns = None
        self.pca = None
        
    def fit_transform(
        self, 
        df: pd.DataFrame,
        feature_columns: Optional[List[str]] = None,
        exclude_columns: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Ajusta el preprocesador y transforma los datos.
        
        Args:
            df: DataFrame con los datos
            feature_columns: Columnas a usar como features
            exclude_columns: Columnas a excluir
            
        Returns:
            Array numpy con datos preprocesados
        """
        if feature_columns is None:
            # Seleccionar columnas numéricas
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if exclude_columns is None:
            exclude_columns = ['is_anomaly', 'weight_in_spec', 'hardness_in_spec',
                              'dissolution_pass', 'temp_in_spec', 'humidity_in_spec',
                              'pressure_compliant']
        
        self.feature_columns = [c for c in feature_columns if c not in exclude_columns]
        
        # Extraer datos
        X = df[self.feature_columns].copy()
        
        # Manejar valores faltantes
        X = X.fillna(X.median())
        
        # Escalado
        if self.scaling_method == 'standard':
            self.scaler = StandardScaler()
        elif self.scaling_method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            from sklearn.preprocessing import RobustScaler
            self.scaler = RobustScaler()
        
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transforma nuevos datos usando el preprocesador ajustado.
        
        Args:
            df: DataFrame con nuevos datos
            
        Returns:
            Array numpy con datos preprocesados
        """
        if self.scaler is None:
            raise ValueError("El preprocesador no ha sido ajustado. Llama a fit_transform primero.")
        
        X = df[self.feature_columns].copy()
        X = X.fillna(X.median())
        
        return self.scaler.transform(X)
    
    def apply_pca(
        self, 
        X: np.ndarray, 
        n_components: Union[int, float] = 0.95
    ) -> np.ndarray:
        """
        Aplica PCA para reducción de dimensionalidad.
        
        Args:
            X: Datos a transformar
            n_components: Número de componentes o varianza a preservar
            
        Returns:
            Datos transformados
        """
        self.pca = PCA(n_components=n_components)
        X_pca = self.pca.fit_transform(X)
        
        print(f"PCA: {X.shape[1]} dimensiones -> {X_pca.shape[1]} componentes")
        print(f"Varianza explicada: {self.pca.explained_variance_ratio_.sum():.2%}")
        
        return X_pca


class IsolationForestDetector:
    """
    Detector de anomalías basado en Isolation Forest.
    
    Ventajas:
    - Eficiente con grandes datasets
    - No requiere datos etiquetados
    - Robusto ante múltiples tipos de anomalías
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector.
        
        Args:
            config: Configuración del modelo
        """
        default_config = get_config().ml_config.isolation_forest
        self.config = config or default_config
        self.model = None
        self.threshold = None
        
    def fit(self, X: np.ndarray) -> 'IsolationForestDetector':
        """
        Entrena el modelo.
        
        Args:
            X: Datos de entrenamiento
            
        Returns:
            Self para encadenamiento
        """
        self.model = IsolationForest(**self.config)
        self.model.fit(X)
        
        # Calcular threshold basado en scores
        scores = -self.model.score_samples(X)
        self.threshold = np.percentile(scores, (1 - self.config['contamination']) * 100)
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predice anomalías.
        
        Args:
            X: Datos a evaluar
            
        Returns:
            Tupla con (predicciones, scores)
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado.")
        
        # Obtener predicciones (-1 = anomalía, 1 = normal)
        predictions = self.model.predict(X)
        # Convertir a 1 = anomalía, 0 = normal
        predictions = (predictions == -1).astype(int)
        
        # Scores de anomalía (más alto = más anómalo)
        scores = -self.model.score_samples(X)
        
        return predictions, scores


class LOFDetector:
    """
    Detector de anomalías basado en Local Outlier Factor.
    
    Ventajas:
    - Detecta anomalías locales
    - Considera la densidad del vecindario
    - Bueno para clusters de diferentes densidades
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector.
        
        Args:
            config: Configuración del modelo
        """
        default_config = get_config().ml_config.lof
        self.config = config or default_config
        self.model = None
        self.threshold = None
        
    def fit(self, X: np.ndarray) -> 'LOFDetector':
        """
        Entrena el modelo.
        
        Args:
            X: Datos de entrenamiento
            
        Returns:
            Self para encadenamiento
        """
        self.model = LocalOutlierFactor(**self.config)
        self.model.fit(X)
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predice anomalías.
        
        Args:
            X: Datos a evaluar
            
        Returns:
            Tupla con (predicciones, scores)
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado.")
        
        predictions = self.model.predict(X)
        predictions = (predictions == -1).astype(int)
        
        scores = -self.model.score_samples(X)
        
        return predictions, scores


class OneClassSVMDetector:
    """
    Detector de anomalías basado en One-Class SVM.
    
    Ventajas:
    - Bueno con datos de alta dimensionalidad
    - Kernel trick para patrones no lineales
    - Robusto matemáticamente
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector.
        
        Args:
            config: Configuración del modelo
        """
        default_config = get_config().ml_config.ocsvm
        self.config = config or default_config
        self.model = None
        
    def fit(self, X: np.ndarray) -> 'OneClassSVMDetector':
        """
        Entrena el modelo.
        
        Args:
            X: Datos de entrenamiento
            
        Returns:
            Self para encadenamiento
        """
        self.model = OneClassSVM(**self.config)
        self.model.fit(X)
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predice anomalías.
        
        Args:
            X: Datos a evaluar
            
        Returns:
            Tupla con (predicciones, scores)
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado.")
        
        predictions = self.model.predict(X)
        predictions = (predictions == -1).astype(int)
        
        scores = -self.model.decision_function(X)
        
        return predictions, scores


class AutoencoderDetector:
    """
    Detector de anomalías basado en Autoencoder.
    
    Ventajas:
    - Aprende representaciones no lineales
    - Detecta anomalías por error de reconstrucción
    - Puede capturar patrones complejos
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector.
        
        Args:
            config: Configuración del modelo
        """
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow es requerido para AutoencoderDetector")
        
        default_config = get_config().ml_config.autoencoder
        self.config = config or default_config
        self.model = None
        self.threshold = None
        self.history = None
        
    def _build_model(self, input_dim: int) -> Model:
        """
        Construye la arquitectura del autoencoder.
        
        Args:
            input_dim: Dimensión de entrada
            
        Returns:
            Modelo Keras
        """
        encoding_dim = self.config['encoding_dim']
        hidden_layers = self.config['hidden_layers']
        activation = self.config['activation']
        
        # Encoder
        inputs = keras.Input(shape=(input_dim,))
        x = inputs
        
        for units in hidden_layers:
            x = layers.Dense(units, activation=activation)(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(0.1)(x)
        
        # Capa de codificación (bottleneck)
        encoded = layers.Dense(encoding_dim, activation=activation, name='encoding')(x)
        
        # Decoder
        x = encoded
        for units in reversed(hidden_layers):
            x = layers.Dense(units, activation=activation)(x)
            x = layers.BatchNormalization()(x)
        
        # Salida
        outputs = layers.Dense(input_dim, activation='linear')(x)
        
        model = Model(inputs, outputs, name='autoencoder')
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse'
        )
        
        return model
    
    def fit(self, X: np.ndarray) -> 'AutoencoderDetector':
        """
        Entrena el autoencoder.
        
        Args:
            X: Datos de entrenamiento
            
        Returns:
            Self para encadenamiento
        """
        self.model = self._build_model(X.shape[1])
        
        # Callbacks
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Entrenar
        self.history = self.model.fit(
            X, X,
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            validation_split=self.config['validation_split'],
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Calcular threshold basado en errores de reconstrucción
        reconstructions = self.model.predict(X, verbose=0)
        mse = np.mean(np.power(X - reconstructions, 2), axis=1)
        self.threshold = np.percentile(mse, 95)
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predice anomalías basado en error de reconstrucción.
        
        Args:
            X: Datos a evaluar
            
        Returns:
            Tupla con (predicciones, scores)
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado.")
        
        reconstructions = self.model.predict(X, verbose=0)
        scores = np.mean(np.power(X - reconstructions, 2), axis=1)
        
        predictions = (scores > self.threshold).astype(int)
        
        return predictions, scores


class AnomalyDetectionEnsemble:
    """
    Ensemble de múltiples detectores de anomalías.
    
    Combina las predicciones de varios modelos para
    obtener resultados más robustos y confiables.
    """
    
    def __init__(
        self,
        models: Optional[List[str]] = None,
        voting_method: str = 'soft',
        consensus_threshold: float = 0.5
    ):
        """
        Inicializa el ensemble.
        
        Args:
            models: Lista de modelos a usar
            voting_method: Método de votación ('soft', 'hard', 'weighted')
            consensus_threshold: Umbral para votación suave
        """
        available_models = ['isolation_forest', 'lof', 'ocsvm']
        if TF_AVAILABLE:
            available_models.append('autoencoder')
        
        self.model_names = models or available_models
        self.voting_method = voting_method
        self.consensus_threshold = consensus_threshold
        
        self.preprocessor = DataPreprocessor()
        self.detectors = {}
        self.results = {}
        self.weights = {}
        
    def _initialize_detectors(self):
        """Inicializa los detectores seleccionados."""
        config = get_config().ml_config
        
        detector_classes = {
            'isolation_forest': IsolationForestDetector,
            'lof': LOFDetector,
            'ocsvm': OneClassSVMDetector
        }
        
        if TF_AVAILABLE:
            detector_classes['autoencoder'] = AutoencoderDetector
        
        for name in self.model_names:
            if name in detector_classes:
                self.detectors[name] = detector_classes[name]()
                self.weights[name] = 1.0  # Peso inicial igual
    
    def fit(
        self, 
        df: pd.DataFrame,
        feature_columns: Optional[List[str]] = None
    ) -> 'AnomalyDetectionEnsemble':
        """
        Entrena todos los modelos del ensemble.
        
        Args:
            df: DataFrame con los datos
            feature_columns: Columnas a usar
            
        Returns:
            Self para encadenamiento
        """
        print("Preprocesando datos...")
        X = self.preprocessor.fit_transform(df, feature_columns)
        
        print(f"Datos preprocesados: {X.shape}")
        
        self._initialize_detectors()
        
        print(f"\nEntrenando {len(self.detectors)} modelos:")
        for name, detector in self.detectors.items():
            start_time = datetime.now()
            print(f"  - {name}...", end=" ")
            
            try:
                detector.fit(X)
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"OK ({elapsed:.2f}s)")
            except Exception as e:
                print(f"ERROR: {e}")
                del self.detectors[name]
        
        return self
    
    def predict(
        self, 
        df: pd.DataFrame,
        return_details: bool = True
    ) -> Union[np.ndarray, ModelEnsembleResult]:
        """
        Genera predicciones del ensemble.
        
        Args:
            df: DataFrame con los datos
            return_details: Si retornar detalles completos
            
        Returns:
            Predicciones o resultado detallado
        """
        X = self.preprocessor.transform(df)
        n_samples = X.shape[0]
        
        all_predictions = np.zeros((n_samples, len(self.detectors)))
        all_scores = np.zeros((n_samples, len(self.detectors)))
        individual_results = {}
        
        print("\nGenerando predicciones:")
        for i, (name, detector) in enumerate(self.detectors.items()):
            start_time = datetime.now()
            
            predictions, scores = detector.predict(X)
            inference_time = (datetime.now() - start_time).total_seconds()
            
            all_predictions[:, i] = predictions
            all_scores[:, i] = scores
            
            # Normalizar scores a [0, 1]
            scores_normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
            
            result = AnomalyDetectionResult(
                model_name=name,
                predictions=predictions,
                scores=scores_normalized,
                threshold=detector.threshold if hasattr(detector, 'threshold') else 0.5,
                anomaly_count=int(predictions.sum()),
                anomaly_percentage=float(predictions.mean() * 100),
                training_time=0,
                inference_time=inference_time
            )
            
            individual_results[name] = result
            print(f"  - {name}: {result.anomaly_count} anomalías ({result.anomaly_percentage:.1f}%)")
        
        # Combinar predicciones
        if self.voting_method == 'hard':
            # Votación mayoritaria
            ensemble_predictions = (all_predictions.mean(axis=1) >= 0.5).astype(int)
            ensemble_scores = all_predictions.mean(axis=1)
            
        elif self.voting_method == 'soft':
            # Promedio de scores normalizados
            normalized_scores = np.zeros_like(all_scores)
            for i in range(all_scores.shape[1]):
                col = all_scores[:, i]
                normalized_scores[:, i] = (col - col.min()) / (col.max() - col.min() + 1e-10)
            
            ensemble_scores = normalized_scores.mean(axis=1)
            ensemble_predictions = (ensemble_scores >= self.consensus_threshold).astype(int)
            
        else:  # weighted
            # Votación ponderada
            weights = np.array([self.weights[name] for name in self.detectors.keys()])
            weights = weights / weights.sum()
            
            ensemble_scores = (all_predictions * weights).sum(axis=1)
            ensemble_predictions = (ensemble_scores >= self.consensus_threshold).astype(int)
        
        print(f"\nEnsemble: {ensemble_predictions.sum()} anomalías ({ensemble_predictions.mean()*100:.1f}%)")
        
        if return_details:
            return ModelEnsembleResult(
                individual_results=individual_results,
                ensemble_predictions=ensemble_predictions,
                ensemble_scores=ensemble_scores,
                voting_weights=self.weights,
                consensus_threshold=self.consensus_threshold
            )
        
        return ensemble_predictions
    
    def evaluate(
        self, 
        y_true: np.ndarray,
        result: ModelEnsembleResult
    ) -> Dict[str, Any]:
        """
        Evalúa el rendimiento del ensemble contra etiquetas reales.
        
        Args:
            y_true: Etiquetas reales
            result: Resultado del ensemble
            
        Returns:
            Diccionario con métricas
        """
        metrics = {
            'individual': {},
            'ensemble': {}
        }
        
        # Métricas individuales
        for name, res in result.individual_results.items():
            pred = res.predictions
            metrics['individual'][name] = {
                'precision': precision_score(y_true, pred, zero_division=0),
                'recall': recall_score(y_true, pred, zero_division=0),
                'f1': f1_score(y_true, pred, zero_division=0),
                'anomaly_count': int(pred.sum())
            }
            
            if len(np.unique(y_true)) > 1:
                try:
                    metrics['individual'][name]['roc_auc'] = roc_auc_score(y_true, res.scores)
                    metrics['individual'][name]['pr_auc'] = average_precision_score(y_true, res.scores)
                except:
                    pass
        
        # Métricas del ensemble
        ensemble_pred = result.ensemble_predictions
        metrics['ensemble'] = {
            'precision': precision_score(y_true, ensemble_pred, zero_division=0),
            'recall': recall_score(y_true, ensemble_pred, zero_division=0),
            'f1': f1_score(y_true, ensemble_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, ensemble_pred).tolist(),
            'classification_report': classification_report(y_true, ensemble_pred, output_dict=True)
        }
        
        if len(np.unique(y_true)) > 1:
            try:
                metrics['ensemble']['roc_auc'] = roc_auc_score(y_true, result.ensemble_scores)
                metrics['ensemble']['pr_auc'] = average_precision_score(y_true, result.ensemble_scores)
            except:
                pass
        
        return metrics
    
    def save(self, filepath: str):
        """Guarda el ensemble entrenado."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        state = {
            'preprocessor': self.preprocessor,
            'detectors': {k: v for k, v in self.detectors.items() if k != 'autoencoder'},
            'weights': self.weights,
            'model_names': self.model_names,
            'voting_method': self.voting_method,
            'consensus_threshold': self.consensus_threshold
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
        
        # Guardar autoencoder por separado si existe
        if 'autoencoder' in self.detectors and TF_AVAILABLE:
            ae_path = filepath.replace('.pkl', '_autoencoder.h5')
            self.detectors['autoencoder'].model.save(ae_path)
        
        print(f"Modelo guardado en: {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'AnomalyDetectionEnsemble':
        """Carga un ensemble guardado."""
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        
        instance = cls(
            models=state['model_names'],
            voting_method=state['voting_method'],
            consensus_threshold=state['consensus_threshold']
        )
        
        instance.preprocessor = state['preprocessor']
        instance.detectors = state['detectors']
        instance.weights = state['weights']
        
        # Cargar autoencoder si existe
        ae_path = filepath.replace('.pkl', '_autoencoder.h5')
        if os.path.exists(ae_path) and TF_AVAILABLE:
            ae_detector = AutoencoderDetector()
            ae_detector.model = keras.models.load_model(ae_path)
            instance.detectors['autoencoder'] = ae_detector
        
        print(f"Modelo cargado desde: {filepath}")
        return instance


# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    from data_generator import DataGenerator
    
    print("=" * 60)
    print("DETECCIÓN DE ANOMALÍAS CON MACHINE LEARNING")
    print("=" * 60)
    
    # Generar datos
    print("\nGenerando datos de prueba...")
    generator = DataGenerator()
    data = generator.generate_all_data(days=7)
    
    # Usar datos de agua como ejemplo
    water_df = data['water']
    y_true = water_df['is_anomaly'].values
    
    print(f"Total de registros: {len(water_df):,}")
    print(f"Anomalías conocidas: {y_true.sum()} ({y_true.mean()*100:.1f}%)")
    
    # Crear y entrenar ensemble
    print("\n" + "-" * 40)
    print("ENTRENAMIENTO DEL ENSEMBLE")
    print("-" * 40)
    
    ensemble = AnomalyDetectionEnsemble(
        models=['isolation_forest', 'lof', 'ocsvm'],
        voting_method='soft',
        consensus_threshold=0.4
    )
    
    ensemble.fit(water_df)
    
    # Predicciones
    print("\n" + "-" * 40)
    print("PREDICCIONES")
    print("-" * 40)
    
    result = ensemble.predict(water_df)
    
    # Evaluación
    print("\n" + "-" * 40)
    print("EVALUACIÓN")
    print("-" * 40)
    
    metrics = ensemble.evaluate(y_true, result)
    
    print("\nMétricas del Ensemble:")
    for metric, value in metrics['ensemble'].items():
        if metric not in ['confusion_matrix', 'classification_report']:
            print(f"  {metric}: {value:.4f}")
    
    print("\nMétricas por modelo:")
    for model_name, model_metrics in metrics['individual'].items():
        print(f"\n  {model_name}:")
        for metric, value in model_metrics.items():
            if isinstance(value, float):
                print(f"    {metric}: {value:.4f}")
    
    print("\n" + "=" * 60)
    print("Detección completada")
    print("=" * 60)
