"""
Crypto Market Analysis - Ultra Modern Dashboard
Author: [Tu nombre]
Description: Elegant, responsive, multilingual dashboard for cryptocurrency and traditional market analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_collector import CryptoMarketCollector
    from analyzer import MarketAnalyzer
    from visualizer import MarketVisualizer
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# =============================================================================
# TRANSLATIONS & CONFIGURATION
# =============================================================================

TRANSLATIONS = {
    'en': {
        'title': 'Crypto vs Traditional Markets Analysis',
        'subtitle': 'Professional Financial Analytics Dashboard',
        'config_title': 'Configuration',
        'data_selection': 'Asset Selection',
        'crypto_label': 'Cryptocurrencies',
        'traditional_label': 'Traditional Assets',
        'time_period': 'Analysis Period',
        'collect_data': 'Collect Live Data',
        'load_sample': 'Load Sample Data',
        'collecting': 'Collecting market data...',
        'success_collect': 'Data collected successfully!',
        'error_collect': 'Failed to collect data',
        'select_assets': 'Please select at least one cryptocurrency and one traditional asset',
        'no_sample': 'No sample data found. Please collect data first.',
        'welcome_msg': 'Please select your assets and collect data using the sidebar to start the analysis.',
        'dashboard_features': 'Dashboard Features:',
        'price_evolution': 'Track how crypto and traditional assets perform over time',
        'correlation_analysis': 'See how different assets move in relation to each other',
        'volatility_comparison': 'Compare risk levels across asset classes',
        'performance_metrics': 'Analyze returns, Sharpe ratios, and drawdowns',
        'market_insights': 'Get automated insights about market behavior',
        'available_assets': 'Available Assets:',
        'cryptocurrencies': 'Cryptocurrencies:',
        'traditional_markets': 'Traditional Markets:',
        'data_overview': 'Data Overview',
        'date_range': 'Date Range',
        'assets_count': 'Assets',
        'data_points': 'Data Points',
        'last_update': 'Last Update',
        'tab_prices': 'Price Evolution',
        'tab_correlations': 'Correlations',
        'tab_volatility': 'Volatility',
        'tab_performance': 'Performance',
        'tab_insights': 'Insights',
        'normalize_prices': 'Normalize Prices',
        'normalize_help': 'Start all assets at 100 for easy comparison',
        'select_display': 'Select assets to display',
        'select_one_asset': 'Please select at least one asset to display',
        'understanding_corr': 'Understanding Correlations',
        'corr_explanation': 'Correlation ranges from -1 to +1:',
        'positive_corr': '+1: Perfect positive correlation',
        'no_corr': '0: No correlation',
        'negative_corr': '-1: Perfect negative correlation',
        'color_coding': 'Color coding:',
        'red_negative': 'Red: Negative correlation',
        'white_neutral': 'White: No correlation',
        'blue_positive': 'Blue: Positive correlation',
        'diversification_note': 'High correlations between different asset classes may indicate reduced diversification benefits.',
        'volatility_analysis': 'Volatility Analysis',
        'rolling_window': 'Rolling Window (days)',
        'volatility_help': 'Number of days for volatility calculation',
        'volatility_insights': 'Volatility Insights: Higher volatility indicates higher risk but also potential for higher returns. Crypto assets typically show higher volatility than traditional assets.',
        'performance_summary': 'Performance Summary Table',
        'performance_charts': 'Performance Comparison Charts',
        'crypto_vs_traditional': 'Crypto vs Traditional Markets',
        'key_findings': 'Key Findings',
        'detailed_analysis': 'Detailed Analysis',
        'risk_return_analysis': 'Risk-Return Analysis',
        'risk_vs_return': 'Risk vs Return Analysis',
        'annual_volatility': 'Annual Volatility (%)',
        'annual_return': 'Annual Return (%)',
        'market_summary': 'Market Summary',
        'crypto_performance': 'Cryptocurrency Performance:',
        'traditional_performance': 'Traditional Markets Performance:',
        'avg_annual_return': 'Average Annual Return',
        'volatility': 'Volatility',
        'sharpe_ratio': 'Sharpe Ratio',
        'correlation_crypto_traditional': 'Correlation between Crypto & Traditional',
        'export_analysis': 'Export Analysis',
        'save_report': 'Save Analysis Report',
        'save_charts': 'Save All Charts',
        'download_csv': 'Download Data (CSV)',
        'report_saved': 'Analysis report saved to results folder!',
        'charts_saved': 'All charts saved to results folder!',
        'footer_text': 'Crypto vs Traditional Markets Analysis Dashboard | Built with Streamlit & Python',
        'data_sources': 'Data sources: CoinGecko API & Yahoo Finance | For educational purposes only'
    },
    'es': {
        'title': 'Análisis Cripto vs Mercados Tradicionales',
        'subtitle': 'Dashboard Profesional de Análisis Financiero',
        'config_title': 'Configuración',
        'data_selection': 'Selección de Activos',
        'crypto_label': 'Criptomonedas',
        'traditional_label': 'Activos Tradicionales',
        'time_period': 'Período de Análisis',
        'collect_data': 'Recopilar Datos en Vivo',
        'load_sample': 'Cargar Datos de Muestra',
        'collecting': 'Recopilando datos del mercado...',
        'success_collect': '¡Datos recopilados exitosamente!',
        'error_collect': 'Error al recopilar datos',
        'select_assets': 'Por favor selecciona al menos una criptomoneda y un activo tradicional',
        'no_sample': 'No se encontraron datos de muestra. Por favor recopila datos primero.',
        'welcome_msg': 'Por favor selecciona tus activos y recopila datos usando la barra lateral para comenzar el análisis.',
        'dashboard_features': 'Características del Dashboard:',
        'price_evolution': 'Rastrea cómo se comportan los activos cripto y tradicionales a lo largo del tiempo',
        'correlation_analysis': 'Ve cómo se mueven los diferentes activos en relación entre sí',
        'volatility_comparison': 'Compara los niveles de riesgo entre clases de activos',
        'performance_metrics': 'Analiza rendimientos, ratios de Sharpe y drawdowns',
        'market_insights': 'Obtén insights automatizados sobre el comportamiento del mercado',
        'available_assets': 'Activos Disponibles:',
        'cryptocurrencies': 'Criptomonedas:',
        'traditional_markets': 'Mercados Tradicionales:',
        'data_overview': 'Resumen de Datos',
        'date_range': 'Rango de Fechas',
        'assets_count': 'Activos',
        'data_points': 'Puntos de Datos',
        'last_update': 'Última Actualización',
        'tab_prices': 'Evolución de Precios',
        'tab_correlations': 'Correlaciones',
        'tab_volatility': 'Volatilidad',
        'tab_performance': 'Rendimiento',
        'tab_insights': 'Insights',
        'normalize_prices': 'Normalizar Precios',
        'normalize_help': 'Iniciar todos los activos en 100 para fácil comparación',
        'select_display': 'Seleccionar activos a mostrar',
        'select_one_asset': 'Por favor selecciona al menos un activo para mostrar',
        'understanding_corr': 'Entendiendo las Correlaciones',
        'corr_explanation': 'La correlación va de -1 a +1:',
        'positive_corr': '+1: Correlación positiva perfecta',
        'no_corr': '0: Sin correlación',
        'negative_corr': '-1: Correlación negativa perfecta',
        'color_coding': 'Código de colores:',
        'red_negative': 'Rojo: Correlación negativa',
        'white_neutral': 'Blanco: Sin correlación',
        'blue_positive': 'Azul: Correlación positiva',
        'diversification_note': 'Las altas correlaciones entre diferentes clases de activos pueden indicar beneficios de diversificación reducidos.',
        'volatility_analysis': 'Análisis de Volatilidad',
        'rolling_window': 'Ventana Móvil (días)',
        'volatility_help': 'Número de días para el cálculo de volatilidad',
        'volatility_insights': 'Insights de Volatilidad: Una mayor volatilidad indica mayor riesgo pero también potencial para mayores rendimientos. Los activos cripto típicamente muestran mayor volatilidad que los activos tradicionales.',
        'performance_summary': 'Tabla Resumen de Rendimiento',
        'performance_charts': 'Gráficos de Comparación de Rendimiento',
        'crypto_vs_traditional': 'Cripto vs Mercados Tradicionales',
        'key_findings': 'Hallazgos Clave',
        'detailed_analysis': 'Análisis Detallado',
        'risk_return_analysis': 'Análisis Riesgo-Rendimiento',
        'risk_vs_return': 'Análisis Riesgo vs Rendimiento',
        'annual_volatility': 'Volatilidad Anual (%)',
        'annual_return': 'Rendimiento Anual (%)',
        'market_summary': 'Resumen del Mercado',
        'crypto_performance': 'Rendimiento de Criptomonedas:',
        'traditional_performance': 'Rendimiento de Mercados Tradicionales:',
        'avg_annual_return': 'Rendimiento Anual Promedio',
        'volatility': 'Volatilidad',
        'sharpe_ratio': 'Ratio de Sharpe',
        'correlation_crypto_traditional': 'Correlación entre Cripto y Tradicional',
        'export_analysis': 'Exportar Análisis',
        'save_report': 'Guardar Reporte de Análisis',
        'save_charts': 'Guardar Todos los Gráficos',
        'download_csv': 'Descargar Datos (CSV)',
        'report_saved': '¡Reporte de análisis guardado en la carpeta results!',
        'charts_saved': '¡Todos los gráficos guardados en la carpeta results!',
        'footer_text': 'Dashboard de Análisis Cripto vs Mercados Tradicionales | Construido con Streamlit & Python',
        'data_sources': 'Fuentes de datos: CoinGecko API & Yahoo Finance | Solo para propósitos educativos'
    }
}

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Crypto Market Analysis | Professional Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/crypto-market-analysis',
        'Report a bug': 'https://github.com/your-username/crypto-market-analysis/issues',
        'About': "# Professional Crypto Market Analysis Dashboard\nBuilt with ❤️ using Streamlit & Python"
    }
)

# =============================================================================
# ULTRA MODERN CSS STYLING
# =============================================================================

st.markdown("""
<style>
    /* ====== GLOBAL STYLES ====== */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ====== MAIN CONTAINER ====== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        margin: 1rem auto;
    }
    
    /* ====== SIDEBAR STYLING ====== */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
        padding: 1rem;
    }
    
    /* ====== HEADER STYLES ====== */
    .main-header {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        background-size: 300% 300%;
        animation: gradientShift 3s ease-in-out infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.05em;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* ====== CARD COMPONENTS ====== */
    .metric-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* ====== INSIGHT BOXES ====== */
    .insight-box {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .insight-box:hover {
        transform: translateX(4px);
        border-left-color: #764ba2;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    }
    
    /* ====== BUTTONS ====== */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(45deg, #5a6fd8, #6b42a1);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ====== LANGUAGE TOGGLE ====== */
    .language-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .lang-btn {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    
    .lang-btn.active {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        backdrop-filter: blur(10px);
    }
    
    .lang-btn:hover {
        background: rgba(255, 255, 255, 0.15);
        color: white;
    }
    
    /* ====== TABS ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 0.5rem;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        padding: 0.7rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* ====== METRICS ====== */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: rgba(255, 255, 255, 0.9);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    /* ====== SELECTBOX & MULTISELECT ====== */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(20px);
    }
    
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(20px);
    }
    
    /* ====== DATAFRAMES ====== */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* ====== FOOTER ====== */
    .footer {
        margin-top: 3rem;
        padding: 2rem 0;
        text-align: center;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border-radius: 0 0 20px 20px;
    }
    
    .footer-text {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
        margin: 0.3rem 0;
    }
    
    /* ====== RESPONSIVE DESIGN ====== */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            margin: 0.5rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .main-subtitle {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .language-toggle {
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.3rem;
        }
        
        .lang-btn {
            padding: 0.3rem 0.6rem;
            font-size: 0.8rem;
        }
        
        [data-testid="metric-container"] {
            padding: 0.8rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.8rem;
            font-size: 0.85rem;
        }
        
        .insight-box {
            padding: 1rem;
            margin: 0.8rem 0;
        }
    }
    
    /* ====== PLOTLY CHARTS ====== */
    .js-plotly-plot .plotly .user-select-none {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
    }
    
    /* ====== LOADING ANIMATIONS ====== */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* ====== SCROLLBAR ====== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* ====== SIDEBAR RESPONSIVE ====== */
    @media (max-width: 768px) {
        .css-1d391kg {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .css-1d391kg.css-1v3fvcr {
            transform: translateX(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

# Initialize language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Initialize data states
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = None

# Get current translations
def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# =============================================================================
# LANGUAGE TOGGLE
# =============================================================================

col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    st.markdown("""
    <div class="language-toggle">
        <button class="lang-btn {}" onclick="window.location.reload()">🇺🇸 EN</button>
        <button class="lang-btn {}" onclick="window.location.reload()">🇪🇸 ES</button>
    </div>
    """.format(
        'active' if st.session_state.language == 'en' else '',
        'active' if st.session_state.language == 'es' else ''
    ), unsafe_allow_html=True)

# Language selector (hidden but functional)
lang_col1, lang_col2 = st.columns([6, 1])
with lang_col2:
    language = st.selectbox(
        "🌐",
        options=['en', 'es'],
        index=0 if st.session_state.language == 'en' else 1,
        format_func=lambda x: '🇺🇸 EN' if x == 'en' else '🇪🇸 ES',
        key='language_selector'
    )
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

# =============================================================================
# HEADER
# =============================================================================

st.markdown(f"""
<div class="main-header">{t('title')}</div>
<div class="main-subtitle">{t('subtitle')}</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR CONFIGURATION
# =============================================================================

with st.sidebar:
    st.markdown(f"## 🔧 {t('config_title')}")
    st.markdown("---")
    
    # Data collection settings
    st.markdown(f"### 📊 {t('data_selection')}")
    
    # Cryptocurrency selection
    crypto_options = ['bitcoin', 'ethereum', 'cardano', 'solana', 'chainlink', 'polkadot']
    selected_cryptos = st.multiselect(
        t('crypto_label'),
        crypto_options,
        default=['bitcoin', 'ethereum', 'cardano', 'solana']
    )
    
    # Traditional markets selection
    traditional_options = ['SPY', 'QQQ', 'GLD', 'TLT', 'VTI', 'BTC-USD']
    selected_traditional = st.multiselect(
        t('traditional_label'),
        traditional_options,
        default=['SPY', 'QQQ', 'GLD']
    )
    
    # Time period
    days_back = st.selectbox(
        t('time_period'),
        [30, 90, 180, 365, 730],
        index=3,
        format_func=lambda x: f"{x} días" if st.session_state.language == 'es' and x < 365 
                              else f"{x//365} año{'s' if x//365 > 1 else ''}" if st.session_state.language == 'es' and x >= 365
                              else f"{x} days" if x < 365 
                              else f"{x//365} year{'s' if x//365 > 1 else ''}"
    )
    
    st.markdown("---")
    
    # Data collection buttons
    if st.button(f"🚀 {t('collect_data')}", type="primary", use_container_width=True):
        if not selected_cryptos or not selected_traditional:
            st.error(t('select_assets'))
        else:
            with st.spinner(t('collecting')):
                try:
                    collector = CryptoMarketCollector()
                    data = collector.get_combined_data(
                        crypto_ids=selected_cryptos,
                        traditional_symbols=selected_traditional,
                        days=days_back
                    )
                    
                    if not data.empty:
                        st.session_state.data = data
                        st.session_state.analyzer = MarketAnalyzer(data)
                        st.session_state.visualizer = MarketVisualizer(data, st.session_state.analyzer)
                        st.session_state.data_loaded = True
                        st.success(t('success_collect'))
                        st.rerun()
                    else:
                        st.error(t('error_collect'))
                        
                except Exception as e:
                    st.error(f"{t('error_collect')}: {str(e)}")
    
    # Load sample data button
    if st.button(f"📝 {t('load_sample')}", use_container_width=True):
        with st.spinner(t('collecting')):
            try:
                # Check if sample data exists
                sample_files = [f for f in os.listdir("data") if f.startswith("market_data_") and f.endswith(".csv")]
                
                if sample_files:
                    # Load the most recent file
                    latest_file = max(sample_files)
                    data = pd.read_csv(f"data/{latest_file}", index_col=0, parse_dates=True)
                    
                    st.session_state.data = data
                    st.session_state.analyzer = MarketAnalyzer(data)
                    st.session_state.visualizer = MarketVisualizer(data, st.session_state.analyzer)
                    st.session_state.data_loaded = True
                    st.success(f"{t('success_collect')} {latest_file}")
                    st.rerun()
                else:
                    st.warning(t('no_sample'))
                    
            except Exception as e:
                st.error(f"{t('error_collect')}: {str(e)}")

# =============================================================================
# MAIN CONTENT
# =============================================================================

if not st.session_state.data_loaded:
    # Welcome message with enhanced styling
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: white; margin-bottom: 1rem;">👋 {t('welcome_msg')}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #667eea; margin-bottom: 1rem;">🎯 {t('dashboard_features')}</h4>
            <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.8;">
                <li><strong>{t('price_evolution').split(':')[0]}:</strong> {t('price_evolution').split(': ', 1)[1] if ': ' in t('price_evolution') else t('price_evolution')}</li>
                <li><strong>{t('correlation_analysis').split(':')[0]}:</strong> {t('correlation_analysis').split(': ', 1)[1] if ': ' in t('correlation_analysis') else t('correlation_analysis')}</li>
                <li><strong>{t('volatility_comparison').split(':')[0]}:</strong> {t('volatility_comparison').split(': ', 1)[1] if ': ' in t('volatility_comparison') else t('volatility_comparison')}</li>
                <li><strong>{t('performance_metrics').split(':')[0]}:</strong> {t('performance_metrics').split(': ', 1)[1] if ': ' in t('performance_metrics') else t('performance_metrics')}</li>
                <li><strong>{t('market_insights').split(':')[0]}:</strong> {t('market_insights').split(': ', 1)[1] if ': ' in t('market_insights') else t('market_insights')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #764ba2; margin-bottom: 1rem;">📊 {t('available_assets')}</h4>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea;">{t('cryptocurrencies')}</strong>
                <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0;">Bitcoin, Ethereum, Cardano, Solana, Chainlink, Polkadot</p>
            </div>
            <div>
                <strong style="color: #667eea;">{t('traditional_markets')}</strong>
                <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0;">SPY (S&P 500), QQQ (NASDAQ), GLD (Gold), TLT (Treasury Bonds), VTI (Total Stock Market), BTC-USD (Bitcoin ETF)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Data overview with enhanced metrics
    st.markdown(f"## 📊 {t('data_overview')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = f"{st.session_state.data.index.min().strftime('%Y-%m-%d')} - {st.session_state.data.index.max().strftime('%Y-%m-%d')}"
        st.metric(f"📅 {t('date_range')}", date_range)
    
    with col2:
        st.metric(f"📈 {t('assets_count')}", len(st.session_state.data.columns))
    
    with col3:
        st.metric(f"📊 {t('data_points')}", f"{len(st.session_state.data):,}")
    
    with col4:
        latest_date = st.session_state.data.index.max().strftime('%Y-%m-%d')
        st.metric(f"🕐 {t('last_update')}", latest_date)
    
    # Enhanced navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"📈 {t('tab_prices')}", 
        f"🔗 {t('tab_correlations')}", 
        f"📊 {t('tab_volatility')}", 
        f"🏆 {t('tab_performance')}", 
        f"🔍 {t('tab_insights')}"
    ])
    
    with tab1:
        st.markdown(f"### 💹 {t('tab_prices')}")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            normalize_prices = st.checkbox(
                t('normalize_prices'), 
                value=True, 
                help=t('normalize_help')
            )
            
            # Asset selection for plotting
            available_assets = st.session_state.data.columns.tolist()
            selected_for_plot = st.multiselect(
                t('select_display'),
                available_assets,
                default=available_assets[:6]  # Show first 6 by default
            )
        
        with col1:
            if selected_for_plot:
                fig = st.session_state.visualizer.plot_price_evolution(
                    assets=selected_for_plot,
                    normalize=normalize_prices
                )
                # Enhanced plot styling
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(t('select_one_asset'))
    
    with tab2:
        st.markdown(f"### 🔗 {t('tab_correlations')}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = st.session_state.visualizer.plot_correlation_heatmap()
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #667eea; margin-bottom: 1rem;">💡 {t('understanding_corr')}</h4>
                <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;"><strong>{t('corr_explanation')}</strong></p>
                <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                    <li><strong>+1:</strong> {t('positive_corr').split(': ', 1)[1] if ': ' in t('positive_corr') else t('positive_corr')}</li>
                    <li><strong>0:</strong> {t('no_corr').split(': ', 1)[1] if ': ' in t('no_corr') else t('no_corr')}</li>
                    <li><strong>-1:</strong> {t('negative_corr').split(': ', 1)[1] if ': ' in t('negative_corr') else t('negative_corr')}</li>
                </ul>
                <p style="color: rgba(255, 255, 255, 0.9); margin-top: 1rem;"><strong>{t('color_coding')}</strong></p>
                <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                    <li>🔴 {t('red_negative')}</li>
                    <li>⚪ {t('white_neutral')}</li>
                    <li>🔵 {t('blue_positive')}</li>
                </ul>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 1rem;">{t('diversification_note')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"### 📊 {t('volatility_analysis')}")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            volatility_window = st.slider(
                t('rolling_window'),
                min_value=7,
                max_value=90,
                value=30,
                help=t('volatility_help')
            )
        
        with col1:
            fig = st.session_state.visualizer.plot_volatility_comparison(window=volatility_window)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>📝 {t('volatility_insights')}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown(f"### 🏆 {t('tab_performance')}")
        
        # Performance metrics table
        performance_df = st.session_state.analyzer.calculate_performance_metrics()
        
        st.markdown(f"#### 📋 {t('performance_summary')}")
        st.dataframe(
            performance_df.round(2),
            use_container_width=True
        )
        
        # Performance visualization
        st.markdown(f"#### 📊 {t('performance_charts')}")
        fig = st.session_state.visualizer.plot_performance_metrics()
        if fig:
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=800
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Crypto vs Traditional comparison
        st.markdown(f"#### ⚖️ {t('crypto_vs_traditional')}")
        fig = st.session_state.visualizer.plot_crypto_vs_traditional()
        if fig:
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown(f"### 🔍 {t('tab_insights')}")
        
        # Generate insights
        insights = st.session_state.analyzer.generate_insights()
        
        st.markdown(f"#### 🧠 {t('key_findings')}")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"""
            <div class="insight-box">
                <strong>{i}.</strong> {insight}
            </div>
            """, unsafe_allow_html=True)
        
        # Additional analysis
        st.markdown(f"#### 📈 {t('detailed_analysis')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"##### 🎯 {t('risk_return_analysis')}")
            performance_df = st.session_state.analyzer.calculate_performance_metrics()
            
            # Create risk-return scatter plot
            fig = go.Figure()
            
            for asset in performance_df.index:
                fig.add_trace(go.Scatter(
                    x=[performance_df.loc[asset, 'Annual Volatility (%)']],
                    y=[performance_df.loc[asset, 'Annual Return (%)']],
                    mode='markers+text',
                    name=asset.replace('_price', '').upper(),
                    text=[asset.replace('_price', '').upper()],
                    textposition="top center",
                    marker=dict(size=12, opacity=0.8)
                ))
            
            fig.update_layout(
                title=t('risk_vs_return'),
                xaxis_title=t('annual_volatility'),
                yaxis_title=t('annual_return'),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"##### 📊 {t('market_summary')}")
            
            # Calculate summary statistics
            analysis = st.session_state.analyzer.crypto_vs_traditional_analysis()
            
            if 'error' not in analysis:
                crypto_perf = analysis['crypto_performance']
                trad_perf = analysis['traditional_performance']
                
                st.markdown(f"""
                <div class="metric-card">
                    <h5 style="color: #667eea;">{t('crypto_performance')}</h5>
                    <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                        <li>{t('avg_annual_return')}: {crypto_perf['avg_annual_return']:.1f}%</li>
                        <li>{t('volatility')}: {crypto_perf['volatility']:.1f}%</li>
                        <li>{t('sharpe_ratio')}: {crypto_perf['sharpe_ratio']:.2f}</li>
                    </ul>
                    
                    <h5 style="color: #764ba2; margin-top: 1rem;">{t('traditional_performance')}</h5>
                    <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                        <li>{t('avg_annual_return')}: {trad_perf['avg_annual_return']:.1f}%</li>
                        <li>{t('volatility')}: {trad_perf['volatility']:.1f}%</li>
                        <li>{t('sharpe_ratio')}: {trad_perf['sharpe_ratio']:.2f}</li>
                    </ul>
                    
                    <p style="color: rgba(255, 255, 255, 0.9); margin-top: 1rem;">
                        <strong>{t('correlation_crypto_traditional')}:</strong> {analysis['correlation_crypto_traditional']:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Export options
        st.markdown(f"#### 💾 {t('export_analysis')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"📄 {t('save_report')}", use_container_width=True):
                st.session_state.analyzer.save_analysis()
                st.success(t('report_saved'))
        
        with col2:
            if st.button(f"📊 {t('save_charts')}", use_container_width=True):
                st.session_state.visualizer.save_plots()
                st.success(t('charts_saved'))
        
        with col3:
            # Download data as CSV
            csv = st.session_state.data.to_csv()
            st.download_button(
                label=f"📥 {t('download_csv')}",
                data=csv,
                file_name=f"market_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# =============================================================================
# FOOTER
# =============================================================================

st.markdown(f"""
<div class="footer">
    <p class="footer-text"><strong>{t('footer_text')}</strong></p>
    <p class="footer-text">{t('data_sources')}</p>
</div>
""", unsafe_allow_html=True)