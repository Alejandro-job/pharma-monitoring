"""
================================================================================
PHARMA INDUSTRIAL MONITORING SYSTEM - STREAMLIT CLOUD APP
================================================================================
Dashboard interactivo para monitoreo de sistemas farmacéuticos
Optimizado para despliegue en Streamlit Cloud

Autor: [Tu Nombre]
Versión: 1.0.0
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="PharmaMonitor - Sistema de Monitoreo Industrial",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/tu-usuario/pharma-monitor',
        'Report a bug': 'https://github.com/tu-usuario/pharma-monitor/issues',
        'About': '''
        ## PharmaMonitor v1.0.0
        Sistema de Monitoreo Industrial Farmacéutico
        
        Desarrollado con Python, Streamlit, y Machine Learning
        '''
    }
)

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
st.markdown("""
<style>
    /* Tema oscuro personalizado */
    .main {
        background-color: #0a0a0a;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(135deg, #141414 0%, #1a1a1a 100%);
        border: 1px solid #262626;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00d4aa;
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #fafafa;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #a1a1aa;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        padding: 4px 8px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
    }
    
    .delta-positive {
        background-color: rgba(34, 197, 94, 0.2);
        color: #22c55e;
    }
    
    .delta-negative {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Alertas personalizadas */
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 4px solid #ef4444;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid #f59e0b;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%);
        border-left: 4px solid #22c55e;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    /* Header personalizado */
    .custom-header {
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    .custom-subheader {
        color: #a1a1aa;
        font-size: 1rem;
        margin-top: 0;
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #141414;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: #a1a1aa;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00d4aa !important;
        color: #0a0a0a !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f;
        border-right: 1px solid #262626;
    }
    
    /* Selectbox y inputs */
    .stSelectbox > div > div {
        background-color: #141414;
        border-color: #262626;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: #141414 !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        color: #0a0a0a;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 212, 170, 0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: #00d4aa;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #141414;
        border-radius: 8px;
    }
    
    /* Status indicators */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 12px;
        background-color: rgba(34, 197, 94, 0.2);
        border-radius: 20px;
        font-size: 0.875rem;
        color: #22c55e;
    }
    
    .status-offline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 12px;
        background-color: rgba(239, 68, 68, 0.2);
        border-radius: 20px;
        font-size: 0.875rem;
        color: #ef4444;
    }
    
    /* Pulse animation for live indicator */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# GENERACIÓN DE DATOS SINTÉTICOS
# =============================================================================
@st.cache_data(ttl=300)
def generate_water_data(n_samples: int = 1000) -> pd.DataFrame:
    """Genera datos sintéticos del sistema de agua."""
    np.random.seed(42)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=n_samples,
        freq='15min'
    )
    
    # Parámetros normales
    conductivity = np.random.normal(0.8, 0.15, n_samples)
    toc = np.random.normal(250, 50, n_samples)
    ph = np.random.normal(7.0, 0.3, n_samples)
    temperature = np.random.normal(22, 2, n_samples)
    
    # Añadir anomalías (5%)
    n_anomalies = int(n_samples * 0.05)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    
    conductivity[anomaly_indices] = np.random.uniform(1.3, 2.0, n_anomalies)
    toc[anomaly_indices] = np.random.uniform(500, 800, n_anomalies)
    
    is_anomaly = np.zeros(n_samples, dtype=bool)
    is_anomaly[anomaly_indices] = True
    
    return pd.DataFrame({
        'timestamp': dates,
        'conductivity': np.clip(conductivity, 0.1, 5.0),
        'toc': np.clip(toc, 50, 1000),
        'ph': np.clip(ph, 5.0, 9.0),
        'temperature': np.clip(temperature, 15, 30),
        'is_anomaly': is_anomaly
    })

@st.cache_data(ttl=300)
def generate_tablet_data(n_samples: int = 1000) -> pd.DataFrame:
    """Genera datos sintéticos de producción de tabletas."""
    np.random.seed(43)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=n_samples,
        freq='15min'
    )
    
    # Parámetros normales
    weight = np.random.normal(200, 3, n_samples)
    hardness = np.random.normal(65, 5, n_samples)
    friability = np.random.normal(0.5, 0.1, n_samples)
    thickness = np.random.normal(4.0, 0.1, n_samples)
    dissolution = np.random.normal(85, 5, n_samples)
    
    # Añadir anomalías (4%)
    n_anomalies = int(n_samples * 0.04)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    
    weight[anomaly_indices] = np.random.uniform(180, 188, n_anomalies)
    hardness[anomaly_indices] = np.random.uniform(45, 52, n_anomalies)
    
    is_anomaly = np.zeros(n_samples, dtype=bool)
    is_anomaly[anomaly_indices] = True
    
    batch_ids = [f"BATCH-{i//50:04d}" for i in range(n_samples)]
    
    return pd.DataFrame({
        'timestamp': dates,
        'batch_id': batch_ids,
        'weight': np.clip(weight, 150, 250),
        'hardness': np.clip(hardness, 30, 100),
        'friability': np.clip(friability, 0.1, 2.0),
        'thickness': np.clip(thickness, 3.0, 5.0),
        'dissolution': np.clip(dissolution, 60, 100),
        'is_anomaly': is_anomaly
    })

@st.cache_data(ttl=300)
def generate_environment_data(n_samples: int = 1000) -> pd.DataFrame:
    """Genera datos sintéticos del monitoreo ambiental."""
    np.random.seed(44)
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=n_samples,
        freq='15min'
    )
    
    # Parámetros normales (ISO Clase 7)
    particles_05 = np.random.normal(150000, 30000, n_samples)
    particles_50 = np.random.normal(3000, 500, n_samples)
    temperature = np.random.normal(21, 1, n_samples)
    humidity = np.random.normal(45, 5, n_samples)
    pressure_diff = np.random.normal(15, 2, n_samples)
    
    # Añadir anomalías (3%)
    n_anomalies = int(n_samples * 0.03)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    
    particles_05[anomaly_indices] = np.random.uniform(350000, 500000, n_anomalies)
    humidity[anomaly_indices] = np.random.uniform(60, 75, n_anomalies)
    
    is_anomaly = np.zeros(n_samples, dtype=bool)
    is_anomaly[anomaly_indices] = True
    
    zones = np.random.choice(['Producción A', 'Producción B', 'Empaque', 'Almacén'], n_samples)
    
    return pd.DataFrame({
        'timestamp': dates,
        'zone': zones,
        'particles_05': np.clip(particles_05, 50000, 600000).astype(int),
        'particles_50': np.clip(particles_50, 500, 10000).astype(int),
        'temperature': np.clip(temperature, 18, 25),
        'humidity': np.clip(humidity, 30, 70),
        'pressure_diff': np.clip(pressure_diff, 5, 30),
        'is_anomaly': is_anomaly
    })

# =============================================================================
# FUNCIONES DE VISUALIZACIÓN
# =============================================================================
def create_gauge_chart(value: float, min_val: float, max_val: float, 
                       title: str, unit: str, thresholds: Dict) -> go.Figure:
    """Crea un gráfico de medidor (gauge)."""
    
    # Determinar color basado en umbrales
    if 'critical_max' in thresholds and value > thresholds['critical_max']:
        color = "#ef4444"
    elif 'warning_max' in thresholds and value > thresholds['warning_max']:
        color = "#f59e0b"
    elif 'critical_min' in thresholds and value < thresholds['critical_min']:
        color = "#ef4444"
    elif 'warning_min' in thresholds and value < thresholds['warning_min']:
        color = "#f59e0b"
    else:
        color = "#22c55e"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={'suffix': f" {unit}", 'font': {'size': 24, 'color': '#fafafa'}},
        title={'text': title, 'font': {'size': 14, 'color': '#a1a1aa'}},
        gauge={
            'axis': {
                'range': [min_val, max_val],
                'tickcolor': '#a1a1aa',
                'tickfont': {'color': '#a1a1aa'}
            },
            'bar': {'color': color},
            'bgcolor': '#262626',
            'borderwidth': 0,
            'steps': [
                {'range': [min_val, thresholds.get('warning_min', min_val)], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [thresholds.get('warning_min', min_val), thresholds.get('warning_max', max_val)], 'color': 'rgba(34, 197, 94, 0.3)'},
                {'range': [thresholds.get('warning_max', max_val), max_val], 'color': 'rgba(245, 158, 11, 0.3)'},
            ],
            'threshold': {
                'line': {'color': '#ef4444', 'width': 2},
                'thickness': 0.75,
                'value': thresholds.get('critical_max', max_val)
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fafafa'},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_time_series(df: pd.DataFrame, column: str, title: str, 
                       color: str = "#00d4aa") -> go.Figure:
    """Crea un gráfico de serie temporal."""
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[column],
        mode='lines',
        name=column,
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
    ))
    
    # Marcar anomalías si existen
    if 'is_anomaly' in df.columns:
        anomalies = df[df['is_anomaly']]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies['timestamp'],
                y=anomalies[column],
                mode='markers',
                name='Anomalías',
                marker=dict(color='#ef4444', size=10, symbol='x')
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#fafafa')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        xaxis=dict(
            gridcolor='#262626',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='#262626',
            showgrid=True,
            zeroline=False
        ),
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a1a1aa')
        ),
        margin=dict(l=40, r=20, t=60, b=40)
    )
    
    return fig

def create_correlation_heatmap(df: pd.DataFrame, columns: List[str]) -> go.Figure:
    """Crea un mapa de calor de correlación."""
    
    corr_matrix = df[columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=columns,
        y=columns,
        colorscale=[
            [0, '#ef4444'],
            [0.5, '#262626'],
            [1, '#22c55e']
        ],
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont=dict(size=12, color='#fafafa'),
        hovertemplate='%{x} vs %{y}: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Matriz de Correlación', font=dict(size=16, color='#fafafa')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        xaxis=dict(side='bottom'),
        margin=dict(l=80, r=20, t=60, b=80)
    )
    
    return fig

def create_distribution_chart(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Crea un histograma con curva de densidad."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df[column],
        name='Distribución',
        marker_color='#00d4aa',
        opacity=0.7,
        nbinsx=30
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#fafafa')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        xaxis=dict(gridcolor='#262626'),
        yaxis=dict(gridcolor='#262626', title='Frecuencia'),
        bargap=0.05,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    
    return fig

def create_box_plot(df: pd.DataFrame, column: str, group_by: str, title: str) -> go.Figure:
    """Crea un box plot agrupado."""
    
    fig = px.box(
        df, 
        x=group_by, 
        y=column,
        color=group_by,
        color_discrete_sequence=['#00d4aa', '#06b6d4', '#8b5cf6', '#f59e0b']
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#fafafa')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        xaxis=dict(gridcolor='#262626'),
        yaxis=dict(gridcolor='#262626'),
        showlegend=False,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    
    return fig

# =============================================================================
# COMPONENTES DE UI
# =============================================================================
def render_metric_card(label: str, value: str, delta: Optional[str] = None, 
                       delta_positive: bool = True) -> str:
    """Renderiza una tarjeta de métrica personalizada."""
    
    delta_html = ""
    if delta:
        delta_class = "delta-positive" if delta_positive else "delta-negative"
        delta_html = f'<span class="metric-delta {delta_class}">{delta}</span>'
    
    return f"""
    <div class="metric-card">
        <p class="metric-label">{label}</p>
        <p class="metric-value">{value}</p>
        {delta_html}
    </div>
    """

def render_alert(message: str, severity: str = "warning") -> str:
    """Renderiza una alerta personalizada."""
    return f"""
    <div class="alert-{severity}">
        {message}
    </div>
    """

# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar():
    """Renderiza el sidebar de la aplicación."""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 class="custom-header">PharmaMonitor</h1>
            <p class="custom-subheader">Sistema de Monitoreo Industrial</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Estado del sistema
        st.markdown("""
        <div class="status-online">
            <span class="live-indicator"></span>
            Sistema Online
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navegación
        st.subheader("📊 Navegación")
        page = st.radio(
            "Seleccionar vista",
            ["Dashboard", "Sistema de Agua", "Producción de Tabletas", 
             "Monitoreo Ambiental", "Alertas", "Análisis ML", "Configuración"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filtros de tiempo
        st.subheader("⏱️ Rango de Tiempo")
        time_range = st.selectbox(
            "Período",
            ["Última hora", "Últimas 4 horas", "Últimas 24 horas", 
             "Última semana", "Último mes"],
            index=2
        )
        
        st.markdown("---")
        
        # Opciones de actualización
        st.subheader("🔄 Actualización")
        auto_refresh = st.toggle("Auto-actualización", value=True)
        if auto_refresh:
            refresh_interval = st.slider("Intervalo (seg)", 10, 300, 60)
            st.caption(f"Próxima actualización en {refresh_interval}s")
        
        st.markdown("---")
        
        # Info del sistema
        st.subheader("ℹ️ Información")
        st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("Versión: 1.0.0")
        st.caption("Autor: [Tu Nombre]")
        
        return page, time_range, auto_refresh

# =============================================================================
# PÁGINAS
# =============================================================================
def page_dashboard():
    """Página principal del dashboard."""
    
    st.markdown('<h1 class="custom-header">Dashboard Principal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Vista general del sistema de monitoreo farmacéutico</p>', unsafe_allow_html=True)
    
    # Cargar datos
    water_df = generate_water_data()
    tablet_df = generate_tablet_data()
    env_df = generate_environment_data()
    
    # KPIs principales
    st.subheader("📈 Indicadores Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(water_df) + len(tablet_df) + len(env_df)
        st.metric("Total Registros", f"{total_records:,}", "+156 hoy")
    
    with col2:
        total_anomalies = (water_df['is_anomaly'].sum() + 
                         tablet_df['is_anomaly'].sum() + 
                         env_df['is_anomaly'].sum())
        st.metric("Anomalías Detectadas", total_anomalies, "-12 vs ayer", delta_color="inverse")
    
    with col3:
        compliance = ((total_records - total_anomalies) / total_records) * 100
        st.metric("Cumplimiento GMP", f"{compliance:.1f}%", "+0.5%")
    
    with col4:
        st.metric("Sistemas Activos", "3/3", "Todos operativos")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Sistema de Agua")
        fig = create_time_series(
            water_df.tail(200), 
            'conductivity', 
            'Conductividad (últimas 50h)',
            '#06b6d4'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💊 Producción de Tabletas")
        fig = create_time_series(
            tablet_df.tail(200), 
            'weight', 
            'Peso de Tabletas (últimas 50h)',
            '#22c55e'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Segunda fila de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Condiciones Ambientales")
        fig = create_time_series(
            env_df.tail(200), 
            'temperature', 
            'Temperatura (últimas 50h)',
            '#f59e0b'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribución de Anomalías")
        anomaly_data = pd.DataFrame({
            'Sistema': ['Agua', 'Tabletas', 'Ambiente'],
            'Anomalías': [
                water_df['is_anomaly'].sum(),
                tablet_df['is_anomaly'].sum(),
                env_df['is_anomaly'].sum()
            ]
        })
        
        fig = px.pie(
            anomaly_data, 
            values='Anomalías', 
            names='Sistema',
            color_discrete_sequence=['#06b6d4', '#22c55e', '#f59e0b'],
            hole=0.4
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a1a1aa'),
            legend=dict(font=dict(color='#a1a1aa'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Alertas recientes
    st.subheader("⚠️ Alertas Recientes")
    
    alerts_data = [
        {"time": "Hace 5 min", "system": "Agua", "message": "Conductividad elevada: 1.35 μS/cm", "severity": "warning"},
        {"time": "Hace 23 min", "system": "Ambiente", "message": "Humedad alta en Zona B: 62%", "severity": "warning"},
        {"time": "Hace 1 hora", "system": "Tabletas", "message": "Peso fuera de rango en BATCH-0045", "severity": "critical"},
        {"time": "Hace 2 horas", "system": "Agua", "message": "TOC normalizado", "severity": "success"},
    ]
    
    for alert in alerts_data:
        icon = "🔴" if alert['severity'] == 'critical' else "🟡" if alert['severity'] == 'warning' else "🟢"
        st.markdown(f"{icon} **{alert['time']}** - [{alert['system']}] {alert['message']}")

def page_water_system():
    """Página del sistema de agua."""
    
    st.markdown('<h1 class="custom-header">Sistema de Agua</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Monitoreo de calidad de agua farmacéutica</p>', unsafe_allow_html=True)
    
    water_df = generate_water_data()
    
    # Métricas actuales
    st.subheader("📊 Valores Actuales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_cond = water_df['conductivity'].iloc[-1]
        st.metric("Conductividad", f"{current_cond:.2f} μS/cm", 
                 f"{current_cond - water_df['conductivity'].iloc[-2]:.2f}")
    
    with col2:
        current_toc = water_df['toc'].iloc[-1]
        st.metric("TOC", f"{current_toc:.0f} ppb",
                 f"{current_toc - water_df['toc'].iloc[-2]:.0f}")
    
    with col3:
        current_ph = water_df['ph'].iloc[-1]
        st.metric("pH", f"{current_ph:.2f}",
                 f"{current_ph - water_df['ph'].iloc[-2]:.2f}")
    
    with col4:
        current_temp = water_df['temperature'].iloc[-1]
        st.metric("Temperatura", f"{current_temp:.1f}°C",
                 f"{current_temp - water_df['temperature'].iloc[-2]:.1f}")
    
    st.markdown("---")
    
    # Gráficos de medidores
    st.subheader("🎯 Indicadores de Estado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig = create_gauge_chart(
            current_cond, 0, 2, "Conductividad", "μS/cm",
            {'warning_max': 1.0, 'critical_max': 1.3}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_gauge_chart(
            current_toc, 0, 600, "TOC", "ppb",
            {'warning_max': 400, 'critical_max': 500}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = create_gauge_chart(
            current_ph, 5, 9, "pH", "",
            {'warning_min': 6.0, 'warning_max': 8.0, 'critical_min': 5.5, 'critical_max': 8.5}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        fig = create_gauge_chart(
            current_temp, 15, 30, "Temperatura", "°C",
            {'warning_min': 18, 'warning_max': 26, 'critical_min': 16, 'critical_max': 28}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Series temporales
    st.subheader("📈 Tendencias")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Conductividad", "TOC", "pH", "Temperatura"])
    
    with tab1:
        fig = create_time_series(water_df.tail(500), 'conductivity', 
                                'Conductividad del Agua', '#06b6d4')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_time_series(water_df.tail(500), 'toc', 
                                'Carbono Orgánico Total', '#8b5cf6')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = create_time_series(water_df.tail(500), 'ph', 
                                'Nivel de pH', '#22c55e')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = create_time_series(water_df.tail(500), 'temperature', 
                                'Temperatura del Agua', '#f59e0b')
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlaciones
    st.subheader("🔗 Análisis de Correlación")
    
    fig = create_correlation_heatmap(water_df, ['conductivity', 'toc', 'ph', 'temperature'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Datos recientes
    st.subheader("📋 Datos Recientes")
    
    st.dataframe(
        water_df.tail(20)[['timestamp', 'conductivity', 'toc', 'ph', 'temperature', 'is_anomaly']].sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True
    )

def page_tablets():
    """Página de producción de tabletas."""
    
    st.markdown('<h1 class="custom-header">Producción de Tabletas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Control de calidad en línea de producción</p>', unsafe_allow_html=True)
    
    tablet_df = generate_tablet_data()
    
    # Métricas actuales
    st.subheader("📊 Valores Actuales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Peso", f"{tablet_df['weight'].iloc[-1]:.1f} mg")
    
    with col2:
        st.metric("Dureza", f"{tablet_df['hardness'].iloc[-1]:.1f} N")
    
    with col3:
        st.metric("Friabilidad", f"{tablet_df['friability'].iloc[-1]:.2f}%")
    
    with col4:
        st.metric("Espesor", f"{tablet_df['thickness'].iloc[-1]:.2f} mm")
    
    with col5:
        st.metric("Disolución", f"{tablet_df['dissolution'].iloc[-1]:.1f}%")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_time_series(tablet_df.tail(300), 'weight', 
                                'Peso de Tabletas', '#22c55e')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_time_series(tablet_df.tail(300), 'hardness', 
                                'Dureza de Tabletas', '#8b5cf6')
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribuciones
    st.subheader("📊 Distribuciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = create_distribution_chart(tablet_df, 'weight', 'Distribución de Peso')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_distribution_chart(tablet_df, 'hardness', 'Distribución de Dureza')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = create_distribution_chart(tablet_df, 'dissolution', 'Distribución de Disolución')
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis por lote
    st.subheader("📦 Análisis por Lote")
    
    batch_stats = tablet_df.groupby('batch_id').agg({
        'weight': ['mean', 'std'],
        'hardness': ['mean', 'std'],
        'is_anomaly': 'sum'
    }).round(2)
    batch_stats.columns = ['Peso_Media', 'Peso_STD', 'Dureza_Media', 'Dureza_STD', 'Anomalías']
    batch_stats = batch_stats.reset_index()
    
    st.dataframe(batch_stats.tail(10), use_container_width=True, hide_index=True)

def page_environment():
    """Página de monitoreo ambiental."""
    
    st.markdown('<h1 class="custom-header">Monitoreo Ambiental</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Condiciones de salas limpias ISO Clase 7</p>', unsafe_allow_html=True)
    
    env_df = generate_environment_data()
    
    # Métricas actuales
    st.subheader("📊 Valores Actuales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Partículas 0.5μm", f"{env_df['particles_05'].iloc[-1]:,}/m³")
    
    with col2:
        st.metric("Partículas 5.0μm", f"{env_df['particles_50'].iloc[-1]:,}/m³")
    
    with col3:
        st.metric("Temperatura", f"{env_df['temperature'].iloc[-1]:.1f}°C")
    
    with col4:
        st.metric("Humedad", f"{env_df['humidity'].iloc[-1]:.1f}%")
    
    with col5:
        st.metric("Δ Presión", f"{env_df['pressure_diff'].iloc[-1]:.1f} Pa")
    
    st.markdown("---")
    
    # Gráficos por zona
    st.subheader("🏭 Estado por Zona")
    
    fig = create_box_plot(env_df, 'particles_05', 'zone', 'Partículas 0.5μm por Zona')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_time_series(env_df.tail(300), 'temperature', 
                                'Temperatura Ambiental', '#f59e0b')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_time_series(env_df.tail(300), 'humidity', 
                                'Humedad Relativa', '#06b6d4')
        st.plotly_chart(fig, use_container_width=True)

def page_alerts():
    """Página de gestión de alertas."""
    
    st.markdown('<h1 class="custom-header">Centro de Alertas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Gestión de alertas y notificaciones del sistema</p>', unsafe_allow_html=True)
    
    # Simulación de alertas
    alerts = [
        {"id": 1, "time": datetime.now() - timedelta(minutes=5), "system": "Agua", 
         "message": "Conductividad elevada: 1.35 μS/cm", "severity": "warning", "status": "active"},
        {"id": 2, "time": datetime.now() - timedelta(minutes=23), "system": "Ambiente", 
         "message": "Humedad alta en Producción B: 62%", "severity": "warning", "status": "active"},
        {"id": 3, "time": datetime.now() - timedelta(hours=1), "system": "Tabletas", 
         "message": "Peso fuera de especificación en BATCH-0045", "severity": "critical", "status": "acknowledged"},
        {"id": 4, "time": datetime.now() - timedelta(hours=2), "system": "Agua", 
         "message": "TOC normalizado después de limpieza", "severity": "info", "status": "resolved"},
        {"id": 5, "time": datetime.now() - timedelta(hours=3), "system": "Ambiente", 
         "message": "Presión diferencial baja en Almacén", "severity": "warning", "status": "resolved"},
    ]
    
    # Resumen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active = len([a for a in alerts if a['status'] == 'active'])
        st.metric("Alertas Activas", active)
    
    with col2:
        critical = len([a for a in alerts if a['severity'] == 'critical'])
        st.metric("Críticas", critical)
    
    with col3:
        warnings = len([a for a in alerts if a['severity'] == 'warning'])
        st.metric("Advertencias", warnings)
    
    with col4:
        resolved = len([a for a in alerts if a['status'] == 'resolved'])
        st.metric("Resueltas (24h)", resolved)
    
    st.markdown("---")
    
    # Lista de alertas
    st.subheader("📋 Lista de Alertas")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        severity_filter = st.multiselect(
            "Severidad",
            ["critical", "warning", "info"],
            default=["critical", "warning"]
        )
    
    with filter_col2:
        status_filter = st.multiselect(
            "Estado",
            ["active", "acknowledged", "resolved"],
            default=["active", "acknowledged"]
        )
    
    with filter_col3:
        system_filter = st.multiselect(
            "Sistema",
            ["Agua", "Tabletas", "Ambiente"],
            default=["Agua", "Tabletas", "Ambiente"]
        )
    
    # Mostrar alertas filtradas
    for alert in alerts:
        if (alert['severity'] in severity_filter and 
            alert['status'] in status_filter and 
            alert['system'] in system_filter):
            
            severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}[alert['severity']]
            status_badge = {"active": "🔔 Activa", "acknowledged": "👁️ Vista", "resolved": "✅ Resuelta"}[alert['status']]
            
            with st.expander(f"{severity_icon} [{alert['system']}] {alert['message']}", expanded=alert['status']=='active'):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Hora:** {alert['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                with col2:
                    st.write(f"**Estado:** {status_badge}")
                with col3:
                    if alert['status'] == 'active':
                        if st.button("Reconocer", key=f"ack_{alert['id']}"):
                            st.success("Alerta reconocida")

def page_ml_analysis():
    """Página de análisis con Machine Learning."""
    
    st.markdown('<h1 class="custom-header">Análisis ML</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Modelos de detección de anomalías</p>', unsafe_allow_html=True)
    
    # Información de modelos
    st.subheader("🤖 Modelos Disponibles")
    
    models_info = [
        {"name": "Isolation Forest", "accuracy": 0.94, "f1": 0.92, "status": "Activo"},
        {"name": "Local Outlier Factor", "accuracy": 0.91, "f1": 0.89, "status": "Activo"},
        {"name": "One-Class SVM", "accuracy": 0.88, "f1": 0.86, "status": "Standby"},
        {"name": "Autoencoder", "accuracy": 0.96, "f1": 0.94, "status": "Activo"},
        {"name": "Ensemble (Votación)", "accuracy": 0.97, "f1": 0.95, "status": "Activo"},
    ]
    
    for model in models_info:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**{model['name']}**")
        with col2:
            st.progress(model['accuracy'], text=f"Accuracy: {model['accuracy']:.0%}")
        with col3:
            st.progress(model['f1'], text=f"F1-Score: {model['f1']:.0%}")
        with col4:
            if model['status'] == 'Activo':
                st.success("Activo")
            else:
                st.warning("Standby")
    
    st.markdown("---")
    
    # Curva ROC
    st.subheader("📈 Curva ROC")
    
    # Generar datos de ejemplo para ROC
    fpr = np.array([0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1])
    tpr = np.array([0, 0.65, 0.80, 0.88, 0.92, 0.95, 0.98, 1])
    
    fig = go.Figure()
    
    # Línea diagonal (clasificador aleatorio)
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Aleatorio',
        line=dict(color='#a1a1aa', dash='dash')
    ))
    
    # Curva ROC
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines+markers',
        name='Ensemble (AUC = 0.96)',
        line=dict(color='#00d4aa', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.1)'
    ))
    
    fig.update_layout(
        title='Curva ROC - Modelo Ensemble',
        xaxis_title='Tasa de Falsos Positivos',
        yaxis_title='Tasa de Verdaderos Positivos',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        xaxis=dict(gridcolor='#262626'),
        yaxis=dict(gridcolor='#262626'),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Matriz de confusión
    st.subheader("🎯 Matriz de Confusión")
    
    confusion_matrix = np.array([[847, 23], [12, 118]])
    
    fig = go.Figure(data=go.Heatmap(
        z=confusion_matrix,
        x=['Predicción: Normal', 'Predicción: Anomalía'],
        y=['Real: Normal', 'Real: Anomalía'],
        text=confusion_matrix,
        texttemplate='%{text}',
        textfont=dict(size=20, color='white'),
        colorscale=[[0, '#262626'], [1, '#00d4aa']],
        showscale=False
    ))
    
    fig.update_layout(
        title='Matriz de Confusión - Ensemble',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a1a1aa'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas detalladas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Verdaderos Negativos", "847")
    with col2:
        st.metric("Falsos Positivos", "23")
    with col3:
        st.metric("Falsos Negativos", "12")
    with col4:
        st.metric("Verdaderos Positivos", "118")

def page_settings():
    """Página de configuración."""
    
    st.markdown('<h1 class="custom-header">Configuración</h1>', unsafe_allow_html=True)
    st.markdown('<p class="custom-subheader">Ajustes del sistema de monitoreo</p>', unsafe_allow_html=True)
    
    # Umbrales de alertas
    st.subheader("⚠️ Umbrales de Alertas")
    
    with st.expander("Sistema de Agua", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Conductividad máxima (μS/cm)", 0.5, 2.0, 1.3)
            st.slider("TOC máximo (ppb)", 200, 800, 500)
        with col2:
            st.slider("pH mínimo", 5.0, 7.0, 6.0)
            st.slider("pH máximo", 7.0, 9.0, 8.0)
    
    with st.expander("Producción de Tabletas"):
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Peso mínimo (mg)", 180, 200, 190)
            st.slider("Peso máximo (mg)", 200, 220, 210)
        with col2:
            st.slider("Dureza mínima (N)", 40, 60, 55)
            st.slider("Friabilidad máxima (%)", 0.5, 2.0, 1.0)
    
    with st.expander("Monitoreo Ambiental"):
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Partículas 0.5μm máx (/m³)", 100000, 500000, 352000)
            st.slider("Temperatura mínima (°C)", 15, 20, 18)
        with col2:
            st.slider("Temperatura máxima (°C)", 22, 28, 25)
            st.slider("Humedad máxima (%)", 50, 70, 60)
    
    st.markdown("---")
    
    # Configuración de ML
    st.subheader("🤖 Configuración de ML")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Modelo principal", 
                    ["Ensemble", "Isolation Forest", "LOF", "One-Class SVM", "Autoencoder"])
        st.slider("Umbral de anomalía", 0.5, 0.99, 0.95)
    
    with col2:
        st.number_input("Ventana de datos (horas)", 1, 168, 24)
        st.toggle("Re-entrenamiento automático", value=True)
    
    st.markdown("---")
    
    # Notificaciones
    st.subheader("🔔 Notificaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.toggle("Notificaciones por email", value=True)
        st.text_input("Email de alertas", "alertas@pharma.com")
    
    with col2:
        st.toggle("Notificaciones push", value=False)
        st.multiselect("Severidades a notificar", 
                      ["Crítica", "Mayor", "Menor"], 
                      default=["Crítica", "Mayor"])
    
    st.markdown("---")
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Configuración", use_container_width=True):
            st.success("Configuración guardada correctamente")
    
    with col2:
        if st.button("🔄 Restaurar Valores", use_container_width=True):
            st.info("Valores restaurados a configuración por defecto")
    
    with col3:
        if st.button("📤 Exportar Configuración", use_container_width=True):
            st.download_button(
                "Descargar JSON",
                data='{"version": "1.0.0"}',
                file_name="pharma_config.json",
                mime="application/json"
            )

# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================
def main():
    """Función principal de la aplicación."""
    
    # Renderizar sidebar y obtener selecciones
    page, time_range, auto_refresh = render_sidebar()
    
    # Renderizar página seleccionada
    if page == "Dashboard":
        page_dashboard()
    elif page == "Sistema de Agua":
        page_water_system()
    elif page == "Producción de Tabletas":
        page_tablets()
    elif page == "Monitoreo Ambiental":
        page_environment()
    elif page == "Alertas":
        page_alerts()
    elif page == "Análisis ML":
        page_ml_analysis()
    elif page == "Configuración":
        page_settings()

if __name__ == "__main__":
    main()
