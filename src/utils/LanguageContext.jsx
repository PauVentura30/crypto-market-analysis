import { createContext, useContext, useState } from 'react'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    analysis: 'Analysis',
    correlations: 'Correlations',
    portfolio: 'Portfolio',
    
    // Common
    loading: 'Loading...',
    error: 'Error',
    noData: 'No data available',
    selectAssets: 'Select assets to analyze',
    totalValue: 'Total Value',
    
    // Dashboard
    marketOverview: 'Market Overview',
    priceAnalysis: 'Price Analysis',
    performance: 'Performance',
    volatility: 'Volatility',
    
    // Sidebar
    cryptocurrencies: 'Cryptocurrencies',
    traditionalMarkets: 'Traditional Markets',
    commodities: 'Commodities',
    indices: 'Indices',
    
    // Assets
    bitcoin: 'Bitcoin',
    ethereum: 'Ethereum',
    sp500: 'S&P 500',
    nasdaq: 'NASDAQ',
    gold: 'Gold',
    oil: 'Oil',
    
    // Analysis
    priceComparison: 'Price Comparison',
    correlationMatrix: 'Correlation Matrix',
    volatilityAnalysis: 'Volatility Analysis',
    performanceMetrics: 'Performance Metrics',
    
    // Time periods
    day: '24H',
    week: '7D',
    month: '30D',
    quarter: '3M',
    year: '1Y',
    all: 'All Time',
    
    // Metrics
    change: 'Change',
    volume: 'Volume',
    marketCap: 'Market Cap',
    high: 'High',
    low: 'Low',
    close: 'Close',
    
    // Export
    export: 'Export',
    exportData: 'Export Data',
    exportChart: 'Export Chart',
    
    // Settings
    settings: 'Settings',
    language: 'Language',
    theme: 'Theme',
    currency: 'Currency',
  },
  es: {
    // Navigation
    dashboard: 'Panel',
    analysis: 'Análisis',
    correlations: 'Correlaciones',
    portfolio: 'Portafolio',
    
    // Common
    loading: 'Cargando...',
    error: 'Error',
    noData: 'Sin datos disponibles',
    selectAssets: 'Selecciona activos para analizar',
    totalValue: 'Valor Total',
    
    // Dashboard
    marketOverview: 'Resumen del Mercado',
    priceAnalysis: 'Análisis de Precios',
    performance: 'Rendimiento',
    volatility: 'Volatilidad',
    
    // Sidebar
    cryptocurrencies: 'Criptomonedas',
    traditionalMarkets: 'Mercados Tradicionales',
    commodities: 'Commodities',
    indices: 'Índices',
    
    // Assets
    bitcoin: 'Bitcoin',
    ethereum: 'Ethereum',
    sp500: 'S&P 500',
    nasdaq: 'NASDAQ',
    gold: 'Oro',
    oil: 'Petróleo',
    
    // Analysis
    priceComparison: 'Comparación de Precios',
    correlationMatrix: 'Matriz de Correlación',
    volatilityAnalysis: 'Análisis de Volatilidad',
    performanceMetrics: 'Métricas de Rendimiento',
    
    // Time periods
    day: '24H',
    week: '7D',
    month: '30D',
    quarter: '3M',
    year: '1A',
    all: 'Todo el Tiempo',
    
    // Metrics
    change: 'Cambio',
    volume: 'Volumen',
    marketCap: 'Cap. Mercado',
    high: 'Máximo',
    low: 'Mínimo',
    close: 'Cierre',
    
    // Export
    export: 'Exportar',
    exportData: 'Exportar Datos',
    exportChart: 'Exportar Gráfico',
    
    // Settings
    settings: 'Configuración',
    language: 'Idioma',
    theme: 'Tema',
    currency: 'Moneda',
  }
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en')
  
  const t = (key) => {
    return translations[language][key] || key
  }
  
  const changeLanguage = (lang) => {
    setLanguage(lang)
  }
  
  return (
    <LanguageContext.Provider value={{ language, t, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}
