"""
Crypto Market Analysis - Data Visualizer
Author: [Tu nombre]
Description: Creates visualizations for cryptocurrency and traditional market analysis
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import os

class MarketVisualizer:
    """
    Creates visualizations for market analysis
    """
    
    def __init__(self, data_df, analyzer=None):
        """
        Initialize visualizer with market data
        
        Args:
            data_df (pd.DataFrame): DataFrame with market data
            analyzer (MarketAnalyzer): Optional analyzer instance
        """
        self.data = data_df.copy()
        self.analyzer = analyzer
        
        # Create results folder if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_price_evolution(self, assets=None, normalize=True):
        """
        Plot price evolution over time
        
        Args:
            assets (list): List of assets to plot (None for all)
            normalize (bool): Whether to normalize prices to starting value
            
        Returns:
            plotly.graph_objects.Figure: Interactive plot
        """
        if assets is None:
            assets = self.data.columns.tolist()
        
        fig = go.Figure()
        
        for asset in assets:
            if asset in self.data.columns:
                prices = self.data[asset].dropna()
                
                if normalize:
                    # Normalize to starting value (100)
                    prices = (prices / prices.iloc[0]) * 100
                    y_title = "Normalized Price (Starting Value = 100)"
                else:
                    y_title = "Price (USD)"
                
                fig.add_trace(go.Scatter(
                    x=prices.index,
                    y=prices,
                    name=asset.replace('_price', '').upper(),
                    line=dict(width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Date: %{x}<br>' +
                                'Price: %{y:.2f}<br>' +
                                '<extra></extra>'
                ))
        
        fig.update_layout(
            title="Asset Price Evolution Over Time",
            xaxis_title="Date",
            yaxis_title=y_title,
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def plot_correlation_heatmap(self):
        """
        Plot correlation heatmap
        
        Returns:
            plotly.graph_objects.Figure: Correlation heatmap
        """
        if self.analyzer is None:
            returns = self.data.pct_change().dropna()
            correlations = returns.corr()
        else:
            correlations = self.analyzer.calculate_correlations()
        
        # Clean asset names
        clean_names = [name.replace('_price', '').upper() for name in correlations.columns]
        correlations.columns = clean_names
        correlations.index = clean_names
        
        fig = px.imshow(
            correlations,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Asset Correlation Matrix"
        )
        
        fig.update_layout(
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def plot_volatility_comparison(self, window=30):
        """
        Plot volatility comparison
        
        Args:
            window (int): Rolling window for volatility calculation
            
        Returns:
            plotly.graph_objects.Figure: Volatility plot
        """
        returns = self.data.pct_change().dropna()
        volatility = returns.rolling(window=window).std() * np.sqrt(365) * 100
        
        fig = go.Figure()
        
        for column in volatility.columns:
            fig.add_trace(go.Scatter(
                x=volatility.index,
                y=volatility[column],
                name=column.replace('_price', '').upper(),
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=f"Rolling {window}-Day Volatility (%)",
            xaxis_title="Date",
            yaxis_title="Annualized Volatility (%)",
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def plot_performance_metrics(self):
        """
        Plot performance metrics comparison
        
        Returns:
            plotly.graph_objects.Figure: Performance metrics plot
        """
        if self.analyzer is None:
            print("❌ Need analyzer instance for performance metrics")
            return None
        
        performance = self.analyzer.calculate_performance_metrics()
        
        # Clean asset names
        performance.index = [name.replace('_price', '').upper() for name in performance.index]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Return (%)', 'Annual Volatility (%)', 
                          'Sharpe Ratio', 'Max Drawdown (%)'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Total Return
        fig.add_trace(
            go.Bar(x=performance.index, y=performance['Total Return (%)'], 
                  name='Total Return', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Volatility
        fig.add_trace(
            go.Bar(x=performance.index, y=performance['Annual Volatility (%)'], 
                  name='Volatility', marker_color='lightcoral'),
            row=1, col=2
        )
        
        # Sharpe Ratio
        fig.add_trace(
            go.Bar(x=performance.index, y=performance['Sharpe Ratio'], 
                  name='Sharpe Ratio', marker_color='lightgreen'),
            row=2, col=1
        )
        
        # Max Drawdown
        fig.add_trace(
            go.Bar(x=performance.index, y=performance['Max Drawdown (%)'], 
                  name='Max Drawdown', marker_color='lightsalmon'),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Performance Metrics Comparison",
            showlegend=False,
            template='plotly_white',
            height=800
        )
        
        return fig
    
    def plot_crypto_vs_traditional(self):
        """
        Plot crypto vs traditional markets comparison
        
        Returns:
            plotly.graph_objects.Figure: Comparison plot
        """
        if self.analyzer is None:
            print("❌ Need analyzer instance for crypto vs traditional analysis")
            return None
        
        analysis = self.analyzer.crypto_vs_traditional_analysis()
        
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return None
        
        # Create comparison data
        categories = ['Annual Return (%)', 'Volatility (%)', 'Sharpe Ratio']
        
        crypto_values = [
            analysis['crypto_performance']['avg_annual_return'],
            analysis['crypto_performance']['volatility'],
            analysis['crypto_performance']['sharpe_ratio']
        ]
        
        traditional_values = [
            analysis['traditional_performance']['avg_annual_return'],
            analysis['traditional_performance']['volatility'],
            analysis['traditional_performance']['sharpe_ratio']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Cryptocurrency',
            x=categories,
            y=crypto_values,
            marker_color='orange'
        ))
        
        fig.add_trace(go.Bar(
            name='Traditional Markets',
            x=categories,
            y=traditional_values,
            marker_color='blue'
        ))
        
        fig.update_layout(
            title='Cryptocurrency vs Traditional Markets Performance',
            xaxis_title='Metrics',
            yaxis_title='Value',
            barmode='group',
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def create_dashboard_plots(self):
        """
        Create all plots for the dashboard
        
        Returns:
            dict: Dictionary of all plots
        """
        plots = {}
        
        print("📊 Creating price evolution plot...")
        plots['price_evolution'] = self.plot_price_evolution()
        
        print("📊 Creating correlation heatmap...")
        plots['correlation_heatmap'] = self.plot_correlation_heatmap()
        
        print("📊 Creating volatility comparison...")
        plots['volatility_comparison'] = self.plot_volatility_comparison()
        
        if self.analyzer is not None:
            print("📊 Creating performance metrics...")
            plots['performance_metrics'] = self.plot_performance_metrics()
            
            print("📊 Creating crypto vs traditional comparison...")
            plots['crypto_vs_traditional'] = self.plot_crypto_vs_traditional()
        
        return plots
    
    def save_plots(self, plots_dict=None):
        """
        Save all plots to files
        
        Args:
            plots_dict (dict): Dictionary of plots to save
        """
        if plots_dict is None:
            plots_dict = self.create_dashboard_plots()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for plot_name, fig in plots_dict.items():
            if fig is not None:
                filename = f"results/{plot_name}_{timestamp}.html"
                fig.write_html(filename)
                print(f"✅ Saved {plot_name} to {filename}")

# Example usage
if __name__ == "__main__":
    print("🎨 Market Visualizer - Run this after collecting and analyzing data!")
    print("Import this module and use: visualizer = MarketVisualizer(your_data_df, analyzer)")