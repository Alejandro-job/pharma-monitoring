"""
Módulo de Análisis Exploratorio de Datos (EDA)
===============================================
Autor: [Tu Nombre]
Descripción: Análisis estadístico completo y visualización
             de datos farmacéuticos industriales.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import normaltest, shapiro, kstest
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import warnings

from config import get_config, COLORS, DataSource

warnings.filterwarnings('ignore')

# Configuración de estilo para visualizaciones
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


@dataclass
class StatisticalSummary:
    """Resumen estadístico de una variable"""
    variable: str
    count: int
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    skewness: float
    kurtosis: float
    cv: float  # Coeficiente de variación
    is_normal: bool
    normality_pvalue: float


class PharmaceuticalAnalyzer:
    """
    Analizador de datos farmacéuticos.
    
    Proporciona:
    - Estadísticas descriptivas
    - Pruebas de normalidad
    - Análisis de correlación
    - Detección de outliers estadísticos
    - Análisis de tendencias
    - Análisis de capacidad de proceso (Cp, Cpk)
    """
    
    def __init__(self):
        """Inicializa el analizador"""
        self.config = get_config()
        
    def calculate_statistics(
        self, 
        df: pd.DataFrame, 
        numeric_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calcula estadísticas descriptivas completas.
        
        Args:
            df: DataFrame con los datos
            numeric_columns: Columnas numéricas a analizar
            
        Returns:
            DataFrame con estadísticas
        """
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            # Excluir columnas que no son mediciones
            exclude = ['is_anomaly', 'weight_in_spec', 'hardness_in_spec', 
                      'dissolution_pass', 'temp_in_spec', 'humidity_in_spec',
                      'pressure_compliant']
            numeric_columns = [c for c in numeric_columns if c not in exclude]
        
        summaries = []
        
        for col in numeric_columns:
            data = df[col].dropna()
            
            if len(data) < 3:
                continue
                
            # Prueba de normalidad
            if len(data) >= 20:
                if len(data) < 5000:
                    _, p_value = shapiro(data.sample(min(len(data), 5000)))
                else:
                    _, p_value = normaltest(data)
            else:
                p_value = 0.0
            
            summary = StatisticalSummary(
                variable=col,
                count=len(data),
                mean=data.mean(),
                std=data.std(),
                min=data.min(),
                q25=data.quantile(0.25),
                median=data.median(),
                q75=data.quantile(0.75),
                max=data.max(),
                skewness=stats.skew(data),
                kurtosis=stats.kurtosis(data),
                cv=(data.std() / data.mean() * 100) if data.mean() != 0 else 0,
                is_normal=p_value > 0.05,
                normality_pvalue=p_value
            )
            summaries.append(summary)
        
        # Convertir a DataFrame
        stats_df = pd.DataFrame([vars(s) for s in summaries])
        
        # Formatear números
        float_cols = ['mean', 'std', 'min', 'q25', 'median', 'q75', 'max', 
                      'skewness', 'kurtosis', 'cv', 'normality_pvalue']
        for col in float_cols:
            if col in stats_df.columns:
                stats_df[col] = stats_df[col].round(4)
        
        return stats_df
    
    def detect_outliers_iqr(
        self, 
        df: pd.DataFrame, 
        column: str, 
        k: float = 1.5
    ) -> pd.DataFrame:
        """
        Detecta outliers usando el método IQR.
        
        Args:
            df: DataFrame con los datos
            column: Columna a analizar
            k: Multiplicador del IQR (1.5 estándar, 3 para extremos)
            
        Returns:
            DataFrame con outliers identificados
        """
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].copy()
        outliers['outlier_type'] = np.where(
            outliers[column] < lower_bound, 'lower', 'upper'
        )
        outliers['deviation'] = np.where(
            outliers[column] < lower_bound,
            outliers[column] - lower_bound,
            outliers[column] - upper_bound
        )
        
        return outliers
    
    def detect_outliers_zscore(
        self, 
        df: pd.DataFrame, 
        column: str, 
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Detecta outliers usando Z-score.
        
        Args:
            df: DataFrame con los datos
            column: Columna a analizar
            threshold: Umbral de Z-score
            
        Returns:
            DataFrame con outliers identificados
        """
        mean = df[column].mean()
        std = df[column].std()
        
        df_copy = df.copy()
        df_copy['z_score'] = (df_copy[column] - mean) / std
        
        outliers = df_copy[abs(df_copy['z_score']) > threshold].copy()
        return outliers
    
    def calculate_process_capability(
        self,
        data: np.ndarray,
        lsl: Optional[float] = None,
        usl: Optional[float] = None,
        target: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calcula índices de capacidad de proceso.
        
        Args:
            data: Datos del proceso
            lsl: Límite de especificación inferior
            usl: Límite de especificación superior
            target: Valor objetivo
            
        Returns:
            Diccionario con Cp, Cpk, Pp, Ppk
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        results = {
            'mean': mean,
            'std': std,
            'n': len(data)
        }
        
        if usl is not None and lsl is not None:
            # Cp: Capacidad del proceso
            results['Cp'] = (usl - lsl) / (6 * std)
            
            # Cpk: Capacidad del proceso centrado
            cpu = (usl - mean) / (3 * std)
            cpl = (mean - lsl) / (3 * std)
            results['Cpk'] = min(cpu, cpl)
            results['Cpu'] = cpu
            results['Cpl'] = cpl
            
            # PPM fuera de especificación
            ppm_lower = stats.norm.cdf((lsl - mean) / std) * 1e6
            ppm_upper = (1 - stats.norm.cdf((usl - mean) / std)) * 1e6
            results['PPM_total'] = ppm_lower + ppm_upper
            
        elif usl is not None:
            results['Cpu'] = (usl - mean) / (3 * std)
            results['Cpk'] = results['Cpu']
            
        elif lsl is not None:
            results['Cpl'] = (mean - lsl) / (3 * std)
            results['Cpk'] = results['Cpl']
        
        # Evaluación
        if 'Cpk' in results:
            if results['Cpk'] >= 1.33:
                results['capability_rating'] = 'Excelente'
            elif results['Cpk'] >= 1.0:
                results['capability_rating'] = 'Capaz'
            elif results['Cpk'] >= 0.67:
                results['capability_rating'] = 'Marginal'
            else:
                results['capability_rating'] = 'Incapaz'
        
        return results
    
    def analyze_trends(
        self,
        df: pd.DataFrame,
        column: str,
        window: int = 24,
        timestamp_col: str = 'timestamp'
    ) -> pd.DataFrame:
        """
        Analiza tendencias en los datos.
        
        Args:
            df: DataFrame con los datos
            column: Columna a analizar
            window: Tamaño de ventana para media móvil
            timestamp_col: Nombre de columna temporal
            
        Returns:
            DataFrame con análisis de tendencias
        """
        df_sorted = df.sort_values(timestamp_col).copy()
        
        # Media móvil
        df_sorted['rolling_mean'] = df_sorted[column].rolling(window=window).mean()
        df_sorted['rolling_std'] = df_sorted[column].rolling(window=window).std()
        
        # Límites de control (±3σ)
        overall_mean = df_sorted[column].mean()
        overall_std = df_sorted[column].std()
        df_sorted['ucl'] = overall_mean + 3 * overall_std
        df_sorted['lcl'] = overall_mean - 3 * overall_std
        df_sorted['center_line'] = overall_mean
        
        # Detectar puntos fuera de control
        df_sorted['out_of_control'] = (
            (df_sorted[column] > df_sorted['ucl']) | 
            (df_sorted[column] < df_sorted['lcl'])
        )
        
        # Tendencia (regresión lineal)
        if len(df_sorted) > 2:
            x = np.arange(len(df_sorted))
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x, df_sorted[column].values
            )
            df_sorted['trend_line'] = intercept + slope * x
            df_sorted['trend_slope'] = slope
            df_sorted['trend_r_squared'] = r_value ** 2
        
        return df_sorted
    
    def correlation_analysis(
        self,
        df: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None,
        method: str = 'pearson'
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Análisis de correlación entre variables.
        
        Args:
            df: DataFrame con los datos
            numeric_columns: Columnas a incluir
            method: Método de correlación ('pearson', 'spearman', 'kendall')
            
        Returns:
            Tupla con (matriz de correlación, p-values)
        """
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            exclude = ['is_anomaly', 'weight_in_spec', 'hardness_in_spec', 
                      'dissolution_pass', 'temp_in_spec', 'humidity_in_spec',
                      'pressure_compliant']
            numeric_columns = [c for c in numeric_columns if c not in exclude]
        
        # Matriz de correlación
        corr_matrix = df[numeric_columns].corr(method=method)
        
        # Calcular p-values
        n = len(df)
        p_values = pd.DataFrame(
            np.zeros((len(numeric_columns), len(numeric_columns))),
            index=numeric_columns,
            columns=numeric_columns
        )
        
        for i, col1 in enumerate(numeric_columns):
            for j, col2 in enumerate(numeric_columns):
                if i != j:
                    if method == 'pearson':
                        _, p = stats.pearsonr(df[col1].dropna(), df[col2].dropna())
                    elif method == 'spearman':
                        _, p = stats.spearmanr(df[col1].dropna(), df[col2].dropna())
                    else:
                        _, p = stats.kendalltau(df[col1].dropna(), df[col2].dropna())
                    p_values.loc[col1, col2] = p
                else:
                    p_values.loc[col1, col2] = 0
        
        return corr_matrix, p_values
    
    def generate_summary_report(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen completo.
        
        Args:
            data: Diccionario con DataFrames de cada fuente
            
        Returns:
            Diccionario con el reporte completo
        """
        report = {
            'generated_at': pd.Timestamp.now(),
            'sources': {}
        }
        
        for source_name, df in data.items():
            source_report = {
                'total_records': len(df),
                'date_range': {
                    'start': df['timestamp'].min(),
                    'end': df['timestamp'].max()
                },
                'anomalies': {
                    'count': df['is_anomaly'].sum() if 'is_anomaly' in df.columns else 0,
                    'percentage': df['is_anomaly'].mean() * 100 if 'is_anomaly' in df.columns else 0
                },
                'statistics': self.calculate_statistics(df).to_dict('records')
            }
            
            report['sources'][source_name] = source_report
        
        return report


class PharmaceuticalVisualizer:
    """
    Visualizador de datos farmacéuticos.
    
    Genera gráficos profesionales para:
    - Distribuciones
    - Series temporales
    - Correlaciones
    - Gráficos de control
    - Capacidad de proceso
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 6)):
        """Inicializa el visualizador"""
        self.figsize = figsize
        self.colors = COLORS
        
    def plot_distribution(
        self,
        data: pd.Series,
        title: str,
        xlabel: str,
        limits: Optional[Tuple[float, float]] = None,
        target: Optional[float] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Genera gráfico de distribución con histograma y KDE.
        
        Args:
            data: Serie de datos
            title: Título del gráfico
            xlabel: Etiqueta del eje X
            limits: Límites de especificación (LSL, USL)
            target: Valor objetivo
            ax: Axes existente (opcional)
            
        Returns:
            Figura de matplotlib
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        # Histograma con KDE
        sns.histplot(data, kde=True, ax=ax, color=self.colors['primary'], alpha=0.6)
        
        # Líneas de especificación
        if limits:
            ax.axvline(limits[0], color=self.colors['danger'], linestyle='--', 
                      linewidth=2, label=f'LSL: {limits[0]}')
            ax.axvline(limits[1], color=self.colors['danger'], linestyle='--', 
                      linewidth=2, label=f'USL: {limits[1]}')
        
        # Línea de objetivo
        if target:
            ax.axvline(target, color=self.colors['success'], linestyle='-', 
                      linewidth=2, label=f'Target: {target}')
        
        # Media
        mean = data.mean()
        ax.axvline(mean, color=self.colors['warning'], linestyle='-', 
                  linewidth=2, label=f'Mean: {mean:.2f}')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_control_chart(
        self,
        df: pd.DataFrame,
        value_col: str,
        timestamp_col: str = 'timestamp',
        title: str = 'Gráfico de Control',
        ylabel: str = 'Valor',
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Genera gráfico de control (X-bar).
        
        Args:
            df: DataFrame con los datos
            value_col: Columna con valores
            timestamp_col: Columna temporal
            title: Título del gráfico
            ylabel: Etiqueta del eje Y
            ax: Axes existente (opcional)
            
        Returns:
            Figura de matplotlib
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        # Calcular estadísticas
        mean = df[value_col].mean()
        std = df[value_col].std()
        ucl = mean + 3 * std
        lcl = mean - 3 * std
        
        # Datos
        ax.plot(df[timestamp_col], df[value_col], 'o-', 
               color=self.colors['primary'], alpha=0.7, markersize=3, linewidth=0.5)
        
        # Líneas de control
        ax.axhline(mean, color=self.colors['success'], linestyle='-', 
                  linewidth=2, label=f'CL: {mean:.3f}')
        ax.axhline(ucl, color=self.colors['danger'], linestyle='--', 
                  linewidth=2, label=f'UCL: {ucl:.3f}')
        ax.axhline(lcl, color=self.colors['danger'], linestyle='--', 
                  linewidth=2, label=f'LCL: {lcl:.3f}')
        
        # Marcar puntos fuera de control
        out_of_control = df[(df[value_col] > ucl) | (df[value_col] < lcl)]
        ax.scatter(out_of_control[timestamp_col], out_of_control[value_col], 
                  color=self.colors['danger'], s=50, zorder=5, label='Fuera de control')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Tiempo', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(loc='upper right')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_correlation_heatmap(
        self,
        corr_matrix: pd.DataFrame,
        title: str = 'Matriz de Correlación',
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Genera mapa de calor de correlaciones.
        
        Args:
            corr_matrix: Matriz de correlación
            title: Título del gráfico
            ax: Axes existente (opcional)
            
        Returns:
            Figura de matplotlib
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        else:
            fig = ax.figure
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(
            corr_matrix, 
            mask=mask,
            annot=True, 
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={'shrink': 0.8},
            ax=ax
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_time_series_comparison(
        self,
        df: pd.DataFrame,
        columns: List[str],
        timestamp_col: str = 'timestamp',
        title: str = 'Comparación de Series Temporales',
        normalize: bool = True
    ) -> plt.Figure:
        """
        Compara múltiples series temporales.
        
        Args:
            df: DataFrame con los datos
            columns: Columnas a comparar
            timestamp_col: Columna temporal
            title: Título del gráfico
            normalize: Si normalizar los datos
            
        Returns:
            Figura de matplotlib
        """
        fig, axes = plt.subplots(len(columns), 1, figsize=(14, 3 * len(columns)), 
                                 sharex=True)
        
        if len(columns) == 1:
            axes = [axes]
        
        colors_cycle = [self.colors['primary'], self.colors['secondary'], 
                       self.colors['success'], self.colors['warning']]
        
        for i, col in enumerate(columns):
            data = df[col]
            if normalize:
                data = (data - data.mean()) / data.std()
            
            axes[i].plot(df[timestamp_col], data, 
                        color=colors_cycle[i % len(colors_cycle)], 
                        alpha=0.8, linewidth=0.8)
            axes[i].fill_between(df[timestamp_col], data, alpha=0.3,
                                color=colors_cycle[i % len(colors_cycle)])
            axes[i].set_ylabel(col, fontsize=10)
            axes[i].grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold')
        axes[-1].set_xlabel('Tiempo', fontsize=12)
        axes[-1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_capability_analysis(
        self,
        data: np.ndarray,
        lsl: float,
        usl: float,
        target: float,
        title: str = 'Análisis de Capacidad del Proceso'
    ) -> plt.Figure:
        """
        Genera gráfico de análisis de capacidad.
        
        Args:
            data: Datos del proceso
            lsl: Límite inferior de especificación
            usl: Límite superior de especificación
            target: Valor objetivo
            title: Título del gráfico
            
        Returns:
            Figura de matplotlib
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histograma con límites
        ax1 = axes[0]
        sns.histplot(data, kde=True, ax=ax1, color=self.colors['primary'], alpha=0.6)
        ax1.axvline(lsl, color=self.colors['danger'], linestyle='--', linewidth=2, label=f'LSL: {lsl}')
        ax1.axvline(usl, color=self.colors['danger'], linestyle='--', linewidth=2, label=f'USL: {usl}')
        ax1.axvline(target, color=self.colors['success'], linestyle='-', linewidth=2, label=f'Target: {target}')
        ax1.axvline(np.mean(data), color=self.colors['warning'], linestyle='-', linewidth=2, label=f'Mean: {np.mean(data):.2f}')
        ax1.set_title('Distribución vs Especificaciones', fontsize=12)
        ax1.legend()
        
        # Calcular capacidad
        analyzer = PharmaceuticalAnalyzer()
        capability = analyzer.calculate_process_capability(data, lsl, usl, target)
        
        # Gráfico de barras de capacidad
        ax2 = axes[1]
        metrics = ['Cp', 'Cpk', 'Cpu', 'Cpl']
        values = [capability.get(m, 0) for m in metrics]
        colors = [self.colors['success'] if v >= 1.33 else 
                 self.colors['warning'] if v >= 1.0 else 
                 self.colors['danger'] for v in values]
        
        bars = ax2.bar(metrics, values, color=colors, alpha=0.8)
        ax2.axhline(1.33, color=self.colors['success'], linestyle='--', label='Excelente (1.33)')
        ax2.axhline(1.0, color=self.colors['warning'], linestyle='--', label='Capaz (1.0)')
        
        # Añadir valores sobre las barras
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax2.set_title('Índices de Capacidad', fontsize=12)
        ax2.set_ylabel('Valor', fontsize=11)
        ax2.legend(loc='upper right')
        ax2.set_ylim(0, max(values) * 1.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig
    
    def create_dashboard_summary(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> plt.Figure:
        """
        Crea un dashboard resumen con múltiples gráficos.
        
        Args:
            data: Diccionario con DataFrames de cada fuente
            
        Returns:
            Figura de matplotlib
        """
        fig = plt.figure(figsize=(20, 16))
        
        # Layout del dashboard
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Sistema de Agua - Conductividad
        if 'water' in data:
            ax1 = fig.add_subplot(gs[0, 0])
            water_df = data['water'].head(1000)
            ax1.plot(water_df['timestamp'], water_df['conductivity_uS_cm'], 
                    color=self.colors['water'], alpha=0.7, linewidth=0.8)
            ax1.axhline(1.3, color=self.colors['danger'], linestyle='--', label='Límite USP')
            ax1.set_title('Conductividad del Agua', fontsize=11, fontweight='bold')
            ax1.set_ylabel('μS/cm')
            ax1.legend()
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. Sistema de Agua - TOC
        if 'water' in data:
            ax2 = fig.add_subplot(gs[0, 1])
            sns.histplot(data['water']['toc_ppb'], kde=True, ax=ax2, 
                        color=self.colors['water'], alpha=0.6)
            ax2.axvline(500, color=self.colors['danger'], linestyle='--', label='Límite USP')
            ax2.set_title('Distribución TOC', fontsize=11, fontweight='bold')
            ax2.set_xlabel('ppb')
            ax2.legend()
        
        # 3. Tabletas - Peso
        if 'tablets' in data:
            ax3 = fig.add_subplot(gs[0, 2])
            tablets_df = data['tablets'].head(500)
            ax3.scatter(tablets_df['weight_mg'], tablets_df['hardness_N'], 
                       c=tablets_df['dissolution_pct'], cmap='viridis', alpha=0.6, s=20)
            ax3.set_title('Peso vs Dureza (color: Disolución)', fontsize=11, fontweight='bold')
            ax3.set_xlabel('Peso (mg)')
            ax3.set_ylabel('Dureza (N)')
        
        # 4. Tabletas - Control de Peso
        if 'tablets' in data:
            ax4 = fig.add_subplot(gs[1, 0])
            tablets_sample = data['tablets'].head(200)
            mean = tablets_sample['weight_mg'].mean()
            std = tablets_sample['weight_mg'].std()
            ax4.plot(range(len(tablets_sample)), tablets_sample['weight_mg'], 
                    'o-', color=self.colors['tablet'], markersize=3, alpha=0.7)
            ax4.axhline(mean, color=self.colors['success'], linestyle='-', label='CL')
            ax4.axhline(mean + 3*std, color=self.colors['danger'], linestyle='--', label='UCL/LCL')
            ax4.axhline(mean - 3*std, color=self.colors['danger'], linestyle='--')
            ax4.set_title('Gráfico de Control - Peso', fontsize=11, fontweight='bold')
            ax4.set_ylabel('Peso (mg)')
            ax4.legend()
        
        # 5. Ambiente - Partículas
        if 'environment' in data:
            ax5 = fig.add_subplot(gs[1, 1])
            env_df = data['environment'].head(1000)
            ax5.semilogy(env_df['timestamp'], env_df['particles_05um_per_m3'], 
                        color=self.colors['environment'], alpha=0.7, linewidth=0.8)
            ax5.axhline(352000, color=self.colors['warning'], linestyle='--', label='ISO 7')
            ax5.axhline(3520000, color=self.colors['danger'], linestyle='--', label='ISO 8')
            ax5.set_title('Partículas ≥0.5μm', fontsize=11, fontweight='bold')
            ax5.set_ylabel('partículas/m³ (log)')
            ax5.legend()
            ax5.tick_params(axis='x', rotation=45)
        
        # 6. Ambiente - Condiciones
        if 'environment' in data:
            ax6 = fig.add_subplot(gs[1, 2])
            env_sample = data['environment'].sample(min(500, len(data['environment'])))
            ax6.scatter(env_sample['temperature_C'], env_sample['humidity_pct'], 
                       alpha=0.5, color=self.colors['environment'], s=20)
            ax6.axvline(18, color=self.colors['danger'], linestyle='--', alpha=0.5)
            ax6.axvline(25, color=self.colors['danger'], linestyle='--', alpha=0.5)
            ax6.axhline(30, color=self.colors['danger'], linestyle='--', alpha=0.5)
            ax6.axhline(60, color=self.colors['danger'], linestyle='--', alpha=0.5)
            ax6.set_title('Temperatura vs Humedad', fontsize=11, fontweight='bold')
            ax6.set_xlabel('Temperatura (°C)')
            ax6.set_ylabel('Humedad (%)')
        
        # 7. Correlación - Agua
        if 'water' in data:
            ax7 = fig.add_subplot(gs[2, 0])
            water_cols = ['conductivity_uS_cm', 'toc_ppb', 'ph', 'temperature_C']
            corr = data['water'][water_cols].corr()
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', 
                       center=0, ax=ax7, cbar_kws={'shrink': 0.8})
            ax7.set_title('Correlación - Sistema de Agua', fontsize=11, fontweight='bold')
        
        # 8. Anomalías por fuente
        ax8 = fig.add_subplot(gs[2, 1])
        anomaly_counts = {}
        for source, df in data.items():
            if 'is_anomaly' in df.columns:
                anomaly_counts[source] = df['is_anomaly'].sum()
        
        if anomaly_counts:
            colors_bars = [self.colors['water'], self.colors['tablet'], self.colors['environment']]
            bars = ax8.bar(anomaly_counts.keys(), anomaly_counts.values(), 
                          color=colors_bars[:len(anomaly_counts)], alpha=0.8)
            ax8.set_title('Anomalías por Fuente', fontsize=11, fontweight='bold')
            ax8.set_ylabel('Cantidad')
            for bar, count in zip(bars, anomaly_counts.values()):
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                        str(count), ha='center', va='bottom', fontsize=10)
        
        # 9. KPIs
        ax9 = fig.add_subplot(gs[2, 2])
        ax9.axis('off')
        
        # Calcular KPIs
        kpis = []
        if 'water' in data:
            water_compliance = (data['water']['conductivity_uS_cm'] < 1.3).mean() * 100
            kpis.append(f"Cumplimiento Agua: {water_compliance:.1f}%")
        if 'tablets' in data:
            tablet_yield = data['tablets']['weight_in_spec'].mean() * 100
            kpis.append(f"Rendimiento Tabletas: {tablet_yield:.1f}%")
        if 'environment' in data:
            env_compliance = (data['environment']['iso_classification'] != 'Out_of_Spec').mean() * 100
            kpis.append(f"Cumplimiento Ambiente: {env_compliance:.1f}%")
        
        total_records = sum(len(df) for df in data.values())
        total_anomalies = sum(df['is_anomaly'].sum() for df in data.values() if 'is_anomaly' in df.columns)
        kpis.append(f"Total Registros: {total_records:,}")
        kpis.append(f"Total Anomalías: {total_anomalies:,}")
        
        kpi_text = '\n'.join(kpis)
        ax9.text(0.5, 0.5, kpi_text, transform=ax9.transAxes, 
                fontsize=14, verticalalignment='center', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor=self.colors['light'], alpha=0.8))
        ax9.set_title('Indicadores Clave (KPIs)', fontsize=11, fontweight='bold')
        
        fig.suptitle('Dashboard de Monitoreo Farmacéutico', fontsize=16, fontweight='bold', y=1.01)
        
        return fig


# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    from data_generator import DataGenerator
    
    print("=" * 60)
    print("ANÁLISIS EXPLORATORIO DE DATOS FARMACÉUTICOS")
    print("=" * 60)
    
    # Generar datos
    generator = DataGenerator()
    data = generator.generate_all_data(days=7)
    
    # Analizar
    analyzer = PharmaceuticalAnalyzer()
    visualizer = PharmaceuticalVisualizer()
    
    print("\n" + "-" * 40)
    print("ESTADÍSTICAS - SISTEMA DE AGUA")
    print("-" * 40)
    water_stats = analyzer.calculate_statistics(data['water'])
    print(water_stats.to_string())
    
    print("\n" + "-" * 40)
    print("CAPACIDAD DE PROCESO - PESO DE TABLETAS")
    print("-" * 40)
    capability = analyzer.calculate_process_capability(
        data['tablets']['weight_mg'].values,
        lsl=475, usl=525, target=500
    )
    for k, v in capability.items():
        print(f"  {k}: {v}")
    
    # Generar dashboard
    print("\nGenerando dashboard resumen...")
    fig = visualizer.create_dashboard_summary(data)
    fig.savefig('pharma_dashboard.png', dpi=150, bbox_inches='tight')
    print("Dashboard guardado en: pharma_dashboard.png")
    
    print("\n" + "=" * 60)
    print("Análisis completado")
    print("=" * 60)
