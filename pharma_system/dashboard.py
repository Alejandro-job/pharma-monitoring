"""
Dashboard Interactivo de Monitoreo Farmacéutico
================================================
Autor: [Tu Nombre]
Descripción: Dashboard profesional con Streamlit para visualización
             en tiempo real de datos farmacéuticos y alertas.

Ejecutar: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Importar módulos del sistema
from config import get_config, AlertSeverity, DataSource, COLORS, SEVERITY_COLORS
from data_generator import DataGenerator
from analysis import PharmaceuticalAnalyzer
from ml_models import AnomalyDetectionEnsemble
from alerts import AlertEngine

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================

st.set_page_config(
    page_title="PharmaMon Pro | Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS PERSONALIZADO
# =============================================================================

st.markdown("""
<style>
    /* Variables de color */
    :root {
        --primary: #0066CC;
        --secondary: #00A3E0;
        --success: #28A745;
        --warning: #FFC107;
        --danger: #DC3545;
        --dark: #1E1E2E;
        --light: #F8F9FA;
        --water: #00BCD4;
        --tablet: #9C27B0;
        --environment: #4CAF50;
    }
    
    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #ffffff;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-delta {
        font-size: 14px;
        font-weight: 600;
    }
    
    .delta-positive { color: #28A745; }
    .delta-negative { color: #DC3545; }
    
    /* Tarjeta de alerta */
    .alert-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .alert-card:hover {
        background: rgba(255,255,255,0.08);
    }
    
    .alert-critical {
        border-left-color: #DC3545;
        background: rgba(220, 53, 69, 0.1);
    }
    
    .alert-major {
        border-left-color: #FD7E14;
        background: rgba(253, 126, 20, 0.1);
    }
    
    .alert-minor {
        border-left-color: #FFC107;
        background: rgba(255, 193, 7, 0.1);
    }
    
    /* Header de sección */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    
    .section-header h2 {
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        margin: 0;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .badge-critical { background: #DC3545; color: white; }
    .badge-major { background: #FD7E14; color: white; }
    .badge-minor { background: #FFC107; color: #1a1a2e; }
    .badge-success { background: #28A745; color: white; }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: rgba(255,255,255,0.7);
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066CC 0%, #00A3E0 100%);
        color: white;
    }
    
    /* Gráficos */
    .plot-container {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Tabla de datos */
    .dataframe {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px;
    }
    
    .dataframe th {
        background: rgba(0, 102, 204, 0.3) !important;
        color: white !important;
        font-weight: 600;
    }
    
    .dataframe td {
        color: rgba(255,255,255,0.9) !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC 0%, #00A3E0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4);
    }
    
    /* Selectbox y otros inputs */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0066CC 0%, #00A3E0 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 24px;
        color: rgba(255,255,255,0.5);
        font-size: 14px;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 40px;
    }
    
    /* Animación de pulso para alertas críticas */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.3);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# INICIALIZACIÓN DE ESTADO
# =============================================================================

@st.cache_resource
def initialize_system():
    """Inicializa el sistema y genera datos"""
    config = get_config()
    generator = DataGenerator(config)
    analyzer = PharmaceuticalAnalyzer()
    data = generator.generate_all_data(days=7)
    return config, generator, analyzer, data


@st.cache_resource
def train_ml_models(_data):
    """Entrena los modelos de ML"""
    ensemble = AnomalyDetectionEnsemble(
        models=['isolation_forest', 'lof', 'ocsvm'],
        voting_method='soft',
        consensus_threshold=0.4
    )
    
    # Entrenar con datos de agua
    ensemble.fit(_data['water'])
    return ensemble


def get_ml_predictions(ensemble, data, source_name):
    """Obtiene predicciones ML para una fuente de datos"""
    if source_name in data:
        result = ensemble.predict(data[source_name], return_details=True)
        return result
    return None


# =============================================================================
# COMPONENTES DE UI
# =============================================================================

def render_metric_card(label, value, delta=None, delta_type="positive", icon="📊"):
    """Renderiza una tarjeta de métrica"""
    delta_class = "delta-positive" if delta_type == "positive" else "delta-negative"
    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_alert_card(alert):
    """Renderiza una tarjeta de alerta"""
    severity_class = f"alert-{alert.severity.value}"
    badge_class = f"badge-{alert.severity.value}"
    
    st.markdown(f"""
    <div class="alert-card {severity_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="badge {badge_class}">{alert.severity.value.upper()}</span>
            <span style="color: rgba(255,255,255,0.5); font-size: 12px;">
                {alert.timestamp.strftime('%Y-%m-%d %H:%M')}
            </span>
        </div>
        <div style="color: white; font-size: 14px; margin-bottom: 8px;">
            {alert.message}
        </div>
        <div style="display: flex; gap: 16px; font-size: 12px; color: rgba(255,255,255,0.5);">
            <span>Parámetro: {alert.parameter}</span>
            <span>Valor: {alert.value:.3f}</span>
            <span>Límite: {alert.limit:.3f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_gauge_chart(value, title, min_val=0, max_val=100, thresholds=None):
    """Crea un gráfico de gauge"""
    if thresholds is None:
        thresholds = {'normal': 80, 'warning': 90, 'critical': 100}
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': 'white'}},
        number={'font': {'size': 32, 'color': 'white'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': 'white'},
            'bar': {'color': '#00A3E0'},
            'bgcolor': 'rgba(255,255,255,0.1)',
            'borderwidth': 2,
            'bordercolor': 'rgba(255,255,255,0.3)',
            'steps': [
                {'range': [min_val, thresholds['normal']], 'color': 'rgba(40, 167, 69, 0.3)'},
                {'range': [thresholds['normal'], thresholds['warning']], 'color': 'rgba(255, 193, 7, 0.3)'},
                {'range': [thresholds['warning'], max_val], 'color': 'rgba(220, 53, 69, 0.3)'}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_time_series_chart(df, y_cols, title, y_label="Valor"):
    """Crea un gráfico de series temporales"""
    fig = go.Figure()
    
    colors = ['#00BCD4', '#9C27B0', '#4CAF50', '#FFC107', '#DC3545']
    
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=colors[i % len(colors)], width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, '
                      f'{int(colors[i % len(colors)][3:5], 16)}, '
                      f'{int(colors[i % len(colors)][5:7], 16)}, 0.1)'
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='Tiempo',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        hovermode='x unified'
    )
    
    return fig


def create_control_chart(df, value_col, title):
    """Crea un gráfico de control SPC"""
    mean = df[value_col].mean()
    std = df[value_col].std()
    ucl = mean + 3 * std
    lcl = mean - 3 * std
    
    fig = go.Figure()
    
    # Datos
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[value_col],
        mode='lines+markers',
        name='Datos',
        line=dict(color='#00A3E0', width=1),
        marker=dict(size=4)
    ))
    
    # Línea central
    fig.add_hline(y=mean, line_dash="solid", line_color="#28A745", 
                  annotation_text=f"CL: {mean:.2f}")
    
    # UCL y LCL
    fig.add_hline(y=ucl, line_dash="dash", line_color="#DC3545",
                  annotation_text=f"UCL: {ucl:.2f}")
    fig.add_hline(y=lcl, line_dash="dash", line_color="#DC3545",
                  annotation_text=f"LCL: {lcl:.2f}")
    
    # Puntos fuera de control
    out_of_control = df[(df[value_col] > ucl) | (df[value_col] < lcl)]
    if len(out_of_control) > 0:
        fig.add_trace(go.Scatter(
            x=out_of_control['timestamp'],
            y=out_of_control[value_col],
            mode='markers',
            name='Fuera de Control',
            marker=dict(color='#DC3545', size=10, symbol='x')
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=350,
        margin=dict(l=60, r=20, t=60, b=60),
        showlegend=True,
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    
    return fig


def create_distribution_chart(data, title, bins=30):
    """Crea un histograma con KDE"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=bins,
        name='Frecuencia',
        marker=dict(
            color='rgba(0, 163, 224, 0.6)',
            line=dict(color='#00A3E0', width=1)
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Frecuencia'),
        height=300,
        margin=dict(l=60, r=20, t=60, b=40),
        bargap=0.05
    )
    
    return fig


def create_heatmap(corr_matrix, title):
    """Crea un mapa de calor de correlaciones"""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        margin=dict(l=100, r=20, t=60, b=100)
    )
    
    return fig


def create_anomaly_scatter(df, x_col, y_col, anomaly_col, title):
    """Crea un scatter plot con anomalías destacadas"""
    fig = go.Figure()
    
    # Puntos normales
    normal = df[df[anomaly_col] == False] if anomaly_col in df.columns else df
    fig.add_trace(go.Scatter(
        x=normal[x_col],
        y=normal[y_col],
        mode='markers',
        name='Normal',
        marker=dict(color='#00A3E0', size=6, opacity=0.6)
    ))
    
    # Anomalías
    if anomaly_col in df.columns:
        anomalies = df[df[anomaly_col] == True]
        fig.add_trace(go.Scatter(
            x=anomalies[x_col],
            y=anomalies[y_col],
            mode='markers',
            name='Anomalía',
            marker=dict(color='#DC3545', size=10, symbol='x')
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title=x_col, showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title=y_col, showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    
    return fig


# =============================================================================
# PÁGINAS DEL DASHBOARD
# =============================================================================

def page_overview(data, alert_engine):
    """Página de resumen general"""
    st.markdown("""
    <div class="section-header">
        <h2>📊 Resumen Ejecutivo</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    total_records = sum(len(df) for df in data.values())
    total_anomalies = sum(df['is_anomaly'].sum() for df in data.values() if 'is_anomaly' in df.columns)
    
    with col1:
        render_metric_card(
            "Total Registros",
            f"{total_records:,}",
            icon="📈"
        )
    
    with col2:
        render_metric_card(
            "Anomalías Detectadas",
            f"{total_anomalies:,}",
            delta=f"{(total_anomalies/total_records)*100:.1f}%",
            delta_type="negative" if total_anomalies > 0 else "positive",
            icon="⚠️"
        )
    
    with col3:
        # Calcular cumplimiento
        water_compliance = (data['water']['conductivity_uS_cm'] < 1.3).mean() * 100
        render_metric_card(
            "Cumplimiento Agua",
            f"{water_compliance:.1f}%",
            icon="💧"
        )
    
    with col4:
        tablet_yield = data['tablets']['weight_in_spec'].mean() * 100
        render_metric_card(
            "Rendimiento Tabletas",
            f"{tablet_yield:.1f}%",
            icon="💊"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos de resumen
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge de cumplimiento general
        overall_compliance = (water_compliance + tablet_yield) / 2
        fig = create_gauge_chart(
            overall_compliance,
            "Cumplimiento General GMP",
            min_val=0,
            max_val=100,
            thresholds={'normal': 95, 'warning': 98, 'critical': 100}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribución de anomalías por fuente
        anomaly_data = {
            'Fuente': ['Agua', 'Tabletas', 'Ambiente'],
            'Anomalías': [
                data['water']['is_anomaly'].sum(),
                data['tablets']['is_anomaly'].sum(),
                data['environment']['is_anomaly'].sum()
            ]
        }
        fig = px.pie(
            anomaly_data,
            values='Anomalías',
            names='Fuente',
            title='Distribución de Anomalías',
            color_discrete_sequence=['#00BCD4', '#9C27B0', '#4CAF50']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tendencias recientes
    st.markdown("""
    <div class="section-header">
        <h2>📈 Tendencias de las Últimas 24 Horas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtrar últimas 24 horas
    cutoff = data['water']['timestamp'].max() - timedelta(hours=24)
    water_24h = data['water'][data['water']['timestamp'] >= cutoff]
    
    fig = create_time_series_chart(
        water_24h,
        ['conductivity_uS_cm', 'toc_ppb'],
        'Parámetros de Agua (24h)',
        'Valor'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertas activas
    st.markdown("""
    <div class="section-header">
        <h2>🚨 Alertas Activas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    alerts = alert_engine.get_alerts(acknowledged=False, limit=5)
    
    if alerts:
        for alert in alerts:
            render_alert_card(alert)
    else:
        st.success("No hay alertas activas en este momento.")


def page_water_system(data, analyzer):
    """Página del sistema de agua"""
    st.markdown("""
    <div class="section-header">
        <h2>💧 Sistema de Agua Purificada</h2>
    </div>
    """, unsafe_allow_html=True)
    
    water_df = data['water']
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_cond = water_df['conductivity_uS_cm'].mean()
        render_metric_card(
            "Conductividad Promedio",
            f"{avg_cond:.3f} μS/cm",
            delta=f"Límite: 1.3",
            icon="⚡"
        )
    
    with col2:
        avg_toc = water_df['toc_ppb'].mean()
        render_metric_card(
            "TOC Promedio",
            f"{avg_toc:.1f} ppb",
            delta=f"Límite: 500",
            icon="🧪"
        )
    
    with col3:
        avg_ph = water_df['ph'].mean()
        render_metric_card(
            "pH Promedio",
            f"{avg_ph:.2f}",
            delta="Rango: 5.0-7.0",
            icon="📊"
        )
    
    with col4:
        compliance = (water_df['conductivity_uS_cm'] < 1.3).mean() * 100
        render_metric_card(
            "Cumplimiento",
            f"{compliance:.1f}%",
            delta_type="positive" if compliance >= 95 else "negative",
            icon="✅"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["📈 Series Temporales", "📊 Distribuciones", "🔗 Correlaciones"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_control_chart(
                water_df.head(500),
                'conductivity_uS_cm',
                'Gráfico de Control - Conductividad'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_control_chart(
                water_df.head(500),
                'toc_ppb',
                'Gráfico de Control - TOC'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Serie temporal completa
        fig = create_time_series_chart(
            water_df.head(2000),
            ['conductivity_uS_cm'],
            'Conductividad a lo largo del tiempo',
            'μS/cm'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = create_distribution_chart(
                water_df['conductivity_uS_cm'],
                'Distribución de Conductividad'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_distribution_chart(
                water_df['toc_ppb'],
                'Distribución de TOC'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = create_distribution_chart(
                water_df['ph'],
                'Distribución de pH'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        numeric_cols = ['conductivity_uS_cm', 'toc_ppb', 'ph', 'temperature_C', 'endotoxin_EU_mL']
        corr_matrix = water_df[numeric_cols].corr()
        
        fig = create_heatmap(corr_matrix, 'Matriz de Correlación - Sistema de Agua')
        st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas detalladas
    with st.expander("📋 Estadísticas Detalladas"):
        stats = analyzer.calculate_statistics(water_df)
        st.dataframe(stats, use_container_width=True)


def page_tablet_production(data, analyzer):
    """Página de producción de tabletas"""
    st.markdown("""
    <div class="section-header">
        <h2>💊 Producción de Tabletas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    tablet_df = data['tablets']
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_weight = tablet_df['weight_mg'].mean()
        render_metric_card(
            "Peso Promedio",
            f"{avg_weight:.2f} mg",
            delta=f"Target: 500 mg",
            icon="⚖️"
        )
    
    with col2:
        avg_hardness = tablet_df['hardness_N'].mean()
        render_metric_card(
            "Dureza Promedio",
            f"{avg_hardness:.1f} N",
            delta="Rango: 70-130 N",
            icon="💪"
        )
    
    with col3:
        avg_dissolution = tablet_df['dissolution_pct'].mean()
        render_metric_card(
            "Disolución Promedio",
            f"{avg_dissolution:.1f}%",
            delta="Mínimo: 80%",
            icon="💧"
        )
    
    with col4:
        yield_rate = tablet_df['weight_in_spec'].mean() * 100
        render_metric_card(
            "Rendimiento",
            f"{yield_rate:.1f}%",
            delta_type="positive" if yield_rate >= 95 else "negative",
            icon="✅"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["📈 Control de Proceso", "📊 Análisis de Capacidad", "🔍 Anomalías"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_control_chart(
                tablet_df.head(300),
                'weight_mg',
                'Gráfico de Control - Peso de Tableta'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_control_chart(
                tablet_df.head(300),
                'hardness_N',
                'Gráfico de Control - Dureza'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Scatter de peso vs dureza
        fig = create_anomaly_scatter(
            tablet_df,
            'weight_mg',
            'hardness_N',
            'is_anomaly',
            'Relación Peso vs Dureza'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de peso con límites
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=tablet_df['weight_mg'],
                nbinsx=40,
                marker_color='rgba(156, 39, 176, 0.6)',
                name='Peso'
            ))
            # Límites de especificación
            fig.add_vline(x=475, line_dash="dash", line_color="#DC3545",
                         annotation_text="LSL")
            fig.add_vline(x=525, line_dash="dash", line_color="#DC3545",
                         annotation_text="USL")
            fig.add_vline(x=500, line_dash="solid", line_color="#28A745",
                         annotation_text="Target")
            
            fig.update_layout(
                title='Distribución de Peso vs Especificaciones',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Capacidad del proceso
            weights = tablet_df['weight_mg'].values
            mean = weights.mean()
            std = weights.std()
            lsl, usl = 475, 525
            
            cp = (usl - lsl) / (6 * std)
            cpk = min((usl - mean) / (3 * std), (mean - lsl) / (3 * std))
            
            metrics = ['Cp', 'Cpk']
            values = [cp, cpk]
            colors = ['#28A745' if v >= 1.33 else '#FFC107' if v >= 1.0 else '#DC3545' for v in values]
            
            fig = go.Figure(go.Bar(
                x=metrics,
                y=values,
                marker_color=colors,
                text=[f'{v:.3f}' for v in values],
                textposition='outside'
            ))
            
            fig.add_hline(y=1.33, line_dash="dash", line_color="#28A745",
                         annotation_text="Excelente (1.33)")
            fig.add_hline(y=1.0, line_dash="dash", line_color="#FFC107",
                         annotation_text="Capaz (1.0)")
            
            fig.update_layout(
                title='Índices de Capacidad del Proceso',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350,
                yaxis=dict(range=[0, max(values) * 1.4])
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Detección de anomalías
        anomalies = tablet_df[tablet_df['is_anomaly'] == True]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Total Anomalías", len(anomalies))
            st.metric("% del Total", f"{(len(anomalies)/len(tablet_df))*100:.2f}%")
            
            if len(anomalies) > 0:
                st.markdown("**Lotes afectados:**")
                affected_batches = anomalies['batch_number'].unique()[:5]
                for batch in affected_batches:
                    st.code(batch)
        
        with col2:
            if len(anomalies) > 0:
                fig = px.scatter(
                    tablet_df.head(1000),
                    x='weight_mg',
                    y='dissolution_pct',
                    color='is_anomaly',
                    color_discrete_map={True: '#DC3545', False: '#00A3E0'},
                    title='Anomalías: Peso vs Disolución'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def page_environment(data, analyzer):
    """Página de monitoreo ambiental"""
    st.markdown("""
    <div class="section-header">
        <h2>🌡️ Monitoreo Ambiental</h2>
    </div>
    """, unsafe_allow_html=True)
    
    env_df = data['environment']
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_particles = env_df['particles_05um_per_m3'].mean()
        render_metric_card(
            "Partículas ≥0.5μm",
            f"{avg_particles:,.0f}",
            delta="Límite ISO 7: 352,000",
            icon="🔬"
        )
    
    with col2:
        avg_temp = env_df['temperature_C'].mean()
        render_metric_card(
            "Temperatura",
            f"{avg_temp:.1f}°C",
            delta="Rango: 18-25°C",
            icon="🌡️"
        )
    
    with col3:
        avg_humidity = env_df['humidity_pct'].mean()
        render_metric_card(
            "Humedad",
            f"{avg_humidity:.1f}%",
            delta="Rango: 30-60%",
            icon="💨"
        )
    
    with col4:
        iso_compliance = (env_df['iso_classification'] != 'Out_of_Spec').mean() * 100
        render_metric_card(
            "Cumplimiento ISO",
            f"{iso_compliance:.1f}%",
            delta_type="positive" if iso_compliance >= 95 else "negative",
            icon="✅"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["📈 Tendencias", "🗺️ Por Zona", "📊 Clasificación ISO"])
    
    with tab1:
        # Serie temporal de partículas
        fig = go.Figure()
        
        env_sample = env_df.head(2000)
        
        fig.add_trace(go.Scatter(
            x=env_sample['timestamp'],
            y=env_sample['particles_05um_per_m3'],
            mode='lines',
            name='Partículas ≥0.5μm',
            line=dict(color='#4CAF50')
        ))
        
        # Límites ISO
        fig.add_hline(y=352000, line_dash="dash", line_color="#FFC107",
                     annotation_text="ISO 7")
        fig.add_hline(y=3520000, line_dash="dash", line_color="#DC3545",
                     annotation_text="ISO 8")
        
        fig.update_layout(
            title='Conteo de Partículas en el Tiempo',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis_type="log",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Temperatura y humedad
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_control_chart(
                env_sample,
                'temperature_C',
                'Gráfico de Control - Temperatura'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_control_chart(
                env_sample,
                'humidity_pct',
                'Gráfico de Control - Humedad'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Análisis por zona
        zone_stats = env_df.groupby('zone').agg({
            'particles_05um_per_m3': 'mean',
            'temperature_C': 'mean',
            'humidity_pct': 'mean',
            'pressure_diff_Pa': 'mean'
        }).round(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                zone_stats.reset_index(),
                x='zone',
                y='particles_05um_per_m3',
                title='Partículas Promedio por Zona',
                color='particles_05um_per_m3',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Temperatura',
                x=zone_stats.index,
                y=zone_stats['temperature_C'],
                marker_color='#00BCD4'
            ))
            fig.add_trace(go.Bar(
                name='Humedad',
                x=zone_stats.index,
                y=zone_stats['humidity_pct'],
                marker_color='#9C27B0'
            ))
            fig.update_layout(
                title='Condiciones por Zona',
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(zone_stats, use_container_width=True)
    
    with tab3:
        # Clasificación ISO
        iso_counts = env_df['iso_classification'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=iso_counts.values,
                names=iso_counts.index,
                title='Distribución de Clasificación ISO',
                color_discrete_sequence=['#28A745', '#FFC107', '#DC3545']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cumplimiento de condiciones
            compliance_data = {
                'Parámetro': ['Temperatura', 'Humedad', 'Presión'],
                'Cumplimiento (%)': [
                    env_df['temp_in_spec'].mean() * 100,
                    env_df['humidity_in_spec'].mean() * 100,
                    env_df['pressure_compliant'].mean() * 100
                ]
            }
            
            fig = px.bar(
                compliance_data,
                x='Parámetro',
                y='Cumplimiento (%)',
                title='Cumplimiento por Parámetro',
                color='Cumplimiento (%)',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)


def page_ml_analysis(data, ensemble):
    """Página de análisis de Machine Learning"""
    st.markdown("""
    <div class="section-header">
        <h2>🤖 Análisis de Machine Learning</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de fuente
    source = st.selectbox(
        "Seleccionar fuente de datos",
        options=['water', 'tablets', 'environment'],
        format_func=lambda x: {'water': '💧 Sistema de Agua', 
                               'tablets': '💊 Producción de Tabletas',
                               'environment': '🌡️ Monitoreo Ambiental'}[x]
    )
    
    df = data[source]
    y_true = df['is_anomaly'].values if 'is_anomaly' in df.columns else None
    
    # Entrenar y predecir
    with st.spinner("Ejecutando modelos de ML..."):
        # Re-entrenar para esta fuente específica
        source_ensemble = AnomalyDetectionEnsemble(
            models=['isolation_forest', 'lof', 'ocsvm'],
            voting_method='soft'
        )
        source_ensemble.fit(df)
        result = source_ensemble.predict(df, return_details=True)
    
    # Resultados del ensemble
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card(
            "Anomalías Detectadas",
            f"{result.ensemble_predictions.sum():,}",
            delta=f"{result.ensemble_predictions.mean()*100:.2f}%",
            icon="⚠️"
        )
    
    with col2:
        if y_true is not None:
            from sklearn.metrics import f1_score
            f1 = f1_score(y_true, result.ensemble_predictions, zero_division=0)
            render_metric_card(
                "F1-Score",
                f"{f1:.3f}",
                icon="🎯"
            )
    
    with col3:
        render_metric_card(
            "Modelos en Ensemble",
            f"{len(result.individual_results)}",
            icon="🧠"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Resultados por modelo
    tab1, tab2, tab3 = st.tabs(["📊 Comparación de Modelos", "📈 Scores de Anomalía", "🔍 Detalle de Detecciones"])
    
    with tab1:
        # Comparación de detecciones por modelo
        model_data = []
        for name, res in result.individual_results.items():
            model_data.append({
                'Modelo': name,
                'Anomalías': res.anomaly_count,
                'Porcentaje': res.anomaly_percentage
            })
        
        model_df = pd.DataFrame(model_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                model_df,
                x='Modelo',
                y='Anomalías',
                title='Anomalías Detectadas por Modelo',
                color='Modelo',
                color_discrete_sequence=['#00BCD4', '#9C27B0', '#4CAF50', '#FFC107']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Matriz de confusión si hay etiquetas
            if y_true is not None:
                from sklearn.metrics import confusion_matrix
                cm = confusion_matrix(y_true, result.ensemble_predictions)
                
                fig = px.imshow(
                    cm,
                    labels=dict(x="Predicción", y="Real", color="Cantidad"),
                    x=['Normal', 'Anomalía'],
                    y=['Normal', 'Anomalía'],
                    title='Matriz de Confusión (Ensemble)',
                    color_continuous_scale='Blues',
                    text_auto=True
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Distribución de scores
        fig = go.Figure()
        
        for name, res in result.individual_results.items():
            fig.add_trace(go.Histogram(
                x=res.scores,
                name=name,
                opacity=0.6,
                nbinsx=50
            ))
        
        fig.update_layout(
            title='Distribución de Scores de Anomalía',
            barmode='overlay',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title='Score',
            yaxis_title='Frecuencia',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Score del ensemble a lo largo del tiempo
        df_with_scores = df.copy()
        df_with_scores['ensemble_score'] = result.ensemble_scores
        df_with_scores['is_detected'] = result.ensemble_predictions
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_with_scores['timestamp'],
            y=df_with_scores['ensemble_score'],
            mode='lines',
            name='Score',
            line=dict(color='#00A3E0')
        ))
        
        # Threshold
        fig.add_hline(y=result.consensus_threshold, line_dash="dash", 
                     line_color="#DC3545", annotation_text="Threshold")
        
        fig.update_layout(
            title='Score de Anomalía en el Tiempo',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Detalle de anomalías detectadas
        anomaly_indices = np.where(result.ensemble_predictions == 1)[0]
        
        if len(anomaly_indices) > 0:
            anomaly_df = df.iloc[anomaly_indices].copy()
            anomaly_df['ensemble_score'] = result.ensemble_scores[anomaly_indices]
            
            st.markdown(f"**Total de anomalías detectadas: {len(anomaly_df)}**")
            
            # Ordenar por score
            anomaly_df_sorted = anomaly_df.sort_values('ensemble_score', ascending=False)
            
            st.dataframe(
                anomaly_df_sorted.head(100),
                use_container_width=True,
                height=400
            )
            
            # Botón de descarga
            csv = anomaly_df_sorted.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Anomalías (CSV)",
                data=csv,
                file_name=f"anomalias_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.success("No se detectaron anomalías con el umbral actual.")


def page_alerts(data, alert_engine):
    """Página de gestión de alertas"""
    st.markdown("""
    <div class="section-header">
        <h2>🚨 Centro de Alertas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Generar alertas de los datos actuales
    for source_name, df in data.items():
        source = DataSource(df['source'].iloc[0])
        alert_engine.evaluate_threshold(df.head(1000), source)
    
    # Resumen
    summary = alert_engine.get_alert_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Total Alertas",
            f"{summary['total']:,}",
            icon="📋"
        )
    
    with col2:
        render_metric_card(
            "Críticas",
            f"{summary['by_severity']['critical']}",
            delta_type="negative" if summary['by_severity']['critical'] > 0 else "positive",
            icon="🔴"
        )
    
    with col3:
        render_metric_card(
            "Sin Reconocer",
            f"{summary['unacknowledged']}",
            icon="⏳"
        )
    
    with col4:
        render_metric_card(
            "Últimas 24h",
            f"{summary['last_24h']}",
            icon="🕐"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.selectbox(
            "Severidad",
            options=['Todas', 'critical', 'major', 'minor'],
            format_func=lambda x: {'Todas': 'Todas', 'critical': 'Crítica', 
                                   'major': 'Mayor', 'minor': 'Menor'}[x]
        )
    
    with col2:
        source_filter = st.selectbox(
            "Fuente",
            options=['Todas', 'water_system', 'tablet_production', 'environmental_monitoring'],
            format_func=lambda x: {'Todas': 'Todas', 'water_system': 'Agua',
                                   'tablet_production': 'Tabletas',
                                   'environmental_monitoring': 'Ambiente'}[x]
        )
    
    with col3:
        ack_filter = st.selectbox(
            "Estado",
            options=['Todas', 'unacknowledged', 'acknowledged'],
            format_func=lambda x: {'Todas': 'Todas', 'unacknowledged': 'Sin Reconocer',
                                   'acknowledged': 'Reconocidas'}[x]
        )
    
    # Obtener alertas filtradas
    severity = AlertSeverity(severity_filter) if severity_filter != 'Todas' else None
    source = DataSource(source_filter) if source_filter != 'Todas' else None
    acknowledged = None
    if ack_filter == 'acknowledged':
        acknowledged = True
    elif ack_filter == 'unacknowledged':
        acknowledged = False
    
    alerts = alert_engine.get_alerts(
        severity=severity,
        source=source,
        acknowledged=acknowledged,
        limit=50
    )
    
    # Mostrar alertas
    if alerts:
        st.markdown(f"**Mostrando {len(alerts)} alertas**")
        
        for alert in alerts:
            render_alert_card(alert)
    else:
        st.info("No hay alertas que coincidan con los filtros seleccionados.")
    
    # Estadísticas
    with st.expander("📊 Estadísticas de Alertas"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Por severidad
            severity_data = {
                'Severidad': ['Crítica', 'Mayor', 'Menor', 'Info'],
                'Cantidad': [
                    summary['by_severity']['critical'],
                    summary['by_severity']['major'],
                    summary['by_severity']['minor'],
                    summary['by_severity']['info']
                ]
            }
            fig = px.pie(
                severity_data,
                values='Cantidad',
                names='Severidad',
                title='Distribución por Severidad',
                color_discrete_sequence=['#DC3545', '#FD7E14', '#FFC107', '#17A2B8']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Por fuente
            source_data = {
                'Fuente': ['Agua', 'Tabletas', 'Ambiente'],
                'Cantidad': [
                    summary['by_source']['water'],
                    summary['by_source']['tablets'],
                    summary['by_source']['environment']
                ]
            }
            fig = px.pie(
                source_data,
                values='Cantidad',
                names='Fuente',
                title='Distribución por Fuente',
                color_discrete_sequence=['#00BCD4', '#9C27B0', '#4CAF50']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal del dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: white; font-size: 28px; margin: 0;">💊 PharmaMon</h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-top: 8px;">
                Sistema de Monitoreo Industrial
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navegación
        page = st.radio(
            "Navegación",
            options=[
                "📊 Resumen",
                "💧 Sistema de Agua",
                "💊 Producción de Tabletas",
                "🌡️ Monitoreo Ambiental",
                "🤖 Análisis ML",
                "🚨 Centro de Alertas"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("""
        <div style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: 8px;">
            <p style="color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;">
                <strong>Versión:</strong> 2.0.0<br>
                <strong>Última actualización:</strong><br>
                {}<br>
                <strong>Estado:</strong> 
                <span style="color: #28A745;">● Operativo</span>
            </p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botón de actualización
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    
    # Inicializar sistema
    config, generator, analyzer, data = initialize_system()
    ensemble = train_ml_models(data)
    alert_engine = AlertEngine()
    
    # Renderizar página seleccionada
    if "Resumen" in page:
        page_overview(data, alert_engine)
    elif "Sistema de Agua" in page:
        page_water_system(data, analyzer)
    elif "Producción de Tabletas" in page:
        page_tablet_production(data, analyzer)
    elif "Monitoreo Ambiental" in page:
        page_environment(data, analyzer)
    elif "Análisis ML" in page:
        page_ml_analysis(data, ensemble)
    elif "Centro de Alertas" in page:
        page_alerts(data, alert_engine)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>PharmaMon Pro v2.0 | Desarrollado para monitoreo farmacéutico GMP</p>
        <p>© 2024 - Sistema de Demostración</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
