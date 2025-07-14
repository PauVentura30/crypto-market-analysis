# 📈 Crypto Market Analysis Dashboard

Un dashboard profesional y modular para el análisis de criptomonedas vs mercados tradicionales, construido con Streamlit.

## 🚀 Características

- **📊 Análisis Multi-Asset**: Compara criptomonedas con activos tradicionales
- **🔍 Visualizaciones Interactivas**: Gráficos profesionales con Plotly
- **🌐 Multiidioma**: Soporte para Español e Inglés
- **📱 Responsive**: Diseño adaptativo para dispositivos móviles
- **🎨 Diseño Moderno**: Interfaz glassmorphism con animaciones suaves
- **📈 Métricas Avanzadas**: Correlaciones, volatilidad, Sharpe ratio, etc.

## 📁 Estructura del Proyecto

```
dashboard/
├── streamlit_app.py              # Aplicación principal
├── components/                   # Componentes modulares
│   ├── __init__.py
│   ├── navbar.py                # Barra de navegación
│   ├── sidebar.py               # Barra lateral
│   ├── footer.py                # Pie de página
│   └── translations.py          # Traducciones
├── styles/                      # Estilos CSS
│   ├── __init__.py
│   └── main.py                  # CSS principal
├── utils/                       # Utilidades
│   ├── __init__.py
│   └── helpers.py               # Funciones auxiliares
├── requirements.txt             # Dependencias
└── README.md                    # Este archivo
```

## 🛠️ Instalación

1. **Clona el repositorio**:
```bash
git clone <tu-repositorio>
cd dashboard
```

2. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configura los módulos de datos** (opcional):
   - Coloca tus archivos `data_collector.py`, `analyzer.py`, y `visualizer.py` en un directorio `src/`
   - O modifica las importaciones en `streamlit_app.py` según tu estructura

## 🏃‍♂️ Ejecución

```bash
streamlit run streamlit_app.py
```

El dashboard estará disponible en `http://localhost:8501`

## 🎯 Uso

### 1. Selección de Activos
- **Criptomonedas**: Bitcoin, Ethereum, Cardano, Solana, Chainlink, Polkadot
- **Activos Tradicionales**: SPY, QQQ, GLD, TLT, VTI, BTC-USD
- **Período**: 30 días a 2 años

### 2. Recopilación de Datos
- **Datos en Vivo**: Conecta con APIs para datos actuales
- **Datos de Muestra**: Carga datos previamente guardados

### 3. Análisis Disponibles
- **Evolución de Precios**: Tracking temporal con normalización
- **Correlaciones**: Matriz de correlación interactiva
- **Volatilidad**: Análisis de riesgo con ventanas móviles
- **Rendimiento**: Métricas de performance y Sharpe ratios
- **Insights**: Análisis automatizado con exportación

## 🔧 Personalización

### Añadir Nuevos Idiomas
En `components/translations.py`:
```python
TRANSLATIONS = {
    'en': { ... },
    'es': { ... },
    'fr': { ... }  # Nuevo idioma
}
```

### Modificar Estilos
En `styles/main.py`:
```python
# Cambia las variables CSS
:root {
    --primary-color: #tu-color;
    --secondary-color: #tu-color;
}
```

### Añadir Nuevas Métricas
En `utils/helpers.py`:
```python
def tu_nueva_metrica(data):
    # Tu lógica aquí
    return resultado
```

## 📊 Módulos de Datos Requeridos

Para funcionalidad completa, necesitas estos módulos en `src/`:

### `data_collector.py`
```python
class CryptoMarketCollector:
    def get_combined_data(self, crypto_ids, traditional_symbols, days):
        # Recopila datos de APIs
        return pandas_dataframe
```

### `analyzer.py`
```python
class MarketAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def calculate_performance_metrics(self):
        # Calcula métricas
        return dataframe
    
    def generate_insights(self):
        # Genera insights
        return list_of_insights
```

### `visualizer.py`
```python
class MarketVisualizer:
    def __init__(self, data, analyzer):
        self.data = data
        self.analyzer = analyzer
    
    def plot_price_evolution(self, assets, normalize):
        # Crea gráfico de precios
        return plotly_figure
```

## 🌟 Características Técnicas

- **Framework**: Streamlit
- **Visualización**: Plotly
- **Estilos**: CSS moderno con glassmorphism
- **Responsive**: Mobile-first design
- **Performance**: Lazy loading y caching
- **Accesibilidad**: ARIA labels y contrast ratios

## 🚀 Deployment

### Streamlit Cloud
```bash
# Sube tu código a GitHub
# Conecta con Streamlit Cloud
# Deploy automático
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

### Heroku
```bash
# Añade Procfile
echo "web: streamlit run streamlit_app.py --server.port=$PORT" > Procfile
```

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Reconocimientos

- **Streamlit** - Framework principal
- **Plotly** - Visualizaciones interactivas
- **CoinGecko API** - Datos de criptomonedas
- **Yahoo Finance** - Datos de mercados tradicionales

## 📞 Soporte

¿Preguntas o problemas? 

- 📧 Email: tu-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/tu-repo/issues)
- 💬 Discusiones: [GitHub Discussions](https://github.com/tu-usuario/tu-repo/discussions)

---

**⚠️ Disclaimer**: Esta herramienta es solo para fines educativos y de investigación. No constituye asesoramiento financiero.