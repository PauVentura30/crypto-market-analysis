"""
Crypto Market Analysis - Data Analyzer
Author: [Tu nombre]
Description: Analyzes cryptocurrency and traditional market data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class MarketAnalyzer:
    """
    Analyzes market data and calculates key metrics
    """
    
    def __init__(self, data_df):
        """
        Initialize analyzer with market data
        
        Args:
            data_df (pd.DataFrame): DataFrame with market data
        """
        self.data = data_df.copy()
        self.returns = self.calculate_returns()
        self.results = {}
    
    def calculate_returns(self):
        """
        Calculate daily returns for all assets
        
        Returns:
            pd.DataFrame: Daily returns
        """
        returns = self.data.pct_change().dropna()
        return returns
    
    def calculate_volatility(self, window=30):
        """
        Calculate rolling volatility
        
        Args:
            window (int): Rolling window size
            
        Returns:
            pd.DataFrame: Volatility data
        """
        volatility = self.returns.rolling(window=window).std() * np.sqrt(365)
        return volatility
    
    def calculate_correlations(self):
        """
        Calculate correlation matrix between assets
        
        Returns:
            pd.DataFrame: Correlation matrix
        """
        correlation_matrix = self.returns.corr()
        return correlation_matrix
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """
        Calculate Sharpe ratio for each asset
        
        Args:
            risk_free_rate (float): Risk-free rate (annual)
            
        Returns:
            pd.Series: Sharpe ratios
        """
        annual_returns = self.returns.mean() * 365
        annual_volatility = self.returns.std() * np.sqrt(365)
        
        sharpe_ratios = (annual_returns - risk_free_rate) / annual_volatility
        return sharpe_ratios
    
    def calculate_performance_metrics(self):
        """
        Calculate comprehensive performance metrics
        
        Returns:
            pd.DataFrame: Performance metrics
        """
        metrics = {}
        
        for column in self.data.columns:
            asset_returns = self.returns[column]
            asset_prices = self.data[column]
            
            # Basic metrics
            total_return = (asset_prices.iloc[-1] / asset_prices.iloc[0]) - 1
            annual_return = asset_returns.mean() * 365
            annual_volatility = asset_returns.std() * np.sqrt(365)
            
            # Risk metrics
            max_drawdown = self.calculate_max_drawdown(asset_prices)
            sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
            
            # Store metrics
            metrics[column] = {
                'Total Return (%)': total_return * 100,
                'Annual Return (%)': annual_return * 100,
                'Annual Volatility (%)': annual_volatility * 100,
                'Sharpe Ratio': sharpe_ratio,
                'Max Drawdown (%)': max_drawdown * 100,
                'Current Price': asset_prices.iloc[-1]
            }
        
        return pd.DataFrame(metrics).T
    
    def calculate_max_drawdown(self, price_series):
        """
        Calculate maximum drawdown
        
        Args:
            price_series (pd.Series): Price series
            
        Returns:
            float: Maximum drawdown
        """
        cumulative = (1 + price_series.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def crypto_vs_traditional_analysis(self):
        """
        Analyze crypto vs traditional markets
        
        Returns:
            dict: Analysis results
        """
        # Separate crypto and traditional assets
        crypto_cols = [col for col in self.data.columns if any(crypto in col.lower() 
                      for crypto in ['bitcoin', 'ethereum', 'cardano', 'solana'])]
        traditional_cols = [col for col in self.data.columns if col not in crypto_cols]
        
        if not crypto_cols or not traditional_cols:
            return {"error": "Need both crypto and traditional assets for comparison"}
        
        # Calculate average performance
        crypto_returns = self.returns[crypto_cols].mean(axis=1)
        traditional_returns = self.returns[traditional_cols].mean(axis=1)
        
        # Performance comparison
        crypto_performance = {
            'avg_daily_return': crypto_returns.mean() * 100,
            'avg_annual_return': crypto_returns.mean() * 365 * 100,
            'volatility': crypto_returns.std() * np.sqrt(365) * 100,
            'sharpe_ratio': (crypto_returns.mean() * 365 - 0.02) / (crypto_returns.std() * np.sqrt(365))
        }
        
        traditional_performance = {
            'avg_daily_return': traditional_returns.mean() * 100,
            'avg_annual_return': traditional_returns.mean() * 365 * 100,
            'volatility': traditional_returns.std() * np.sqrt(365) * 100,
            'sharpe_ratio': (traditional_returns.mean() * 365 - 0.02) / (traditional_returns.std() * np.sqrt(365))
        }
        
        # Correlation analysis
        crypto_traditional_corr = crypto_returns.corr(traditional_returns)
        
        analysis = {
            'crypto_performance': crypto_performance,
            'traditional_performance': traditional_performance,
            'correlation_crypto_traditional': crypto_traditional_corr,
            'crypto_assets': crypto_cols,
            'traditional_assets': traditional_cols
        }
        
        return analysis
    
    def generate_insights(self):
        """
        Generate key insights from the analysis
        
        Returns:
            list: List of insights
        """
        insights = []
        
        # Performance metrics
        performance = self.calculate_performance_metrics()
        
        # Best performer
        best_performer = performance['Total Return (%)'].idxmax()
        best_return = performance.loc[best_performer, 'Total Return (%)']
        insights.append(f"🏆 Best performer: {best_performer} with {best_return:.1f}% total return")
        
        # Most volatile
        most_volatile = performance['Annual Volatility (%)'].idxmax()
        volatility = performance.loc[most_volatile, 'Annual Volatility (%)']
        insights.append(f"📊 Most volatile: {most_volatile} with {volatility:.1f}% annual volatility")
        
        # Best risk-adjusted return
        best_sharpe = performance['Sharpe Ratio'].idxmax()
        sharpe = performance.loc[best_sharpe, 'Sharpe Ratio']
        insights.append(f"⚖️ Best risk-adjusted return: {best_sharpe} with Sharpe ratio of {sharpe:.2f}")
        
        # Correlation insights
        correlations = self.calculate_correlations()
        
        # Find highest correlation (excluding self-correlation)
        corr_matrix = correlations.where(np.triu(np.ones(correlations.shape), k=1).astype(bool))
        max_corr = corr_matrix.max().max()
        max_corr_pair = corr_matrix.stack().idxmax()
        
        insights.append(f"🔗 Highest correlation: {max_corr_pair[0]} and {max_corr_pair[1]} ({max_corr:.2f})")
        
        # Crypto vs Traditional analysis
        comparison = self.crypto_vs_traditional_analysis()
        if 'error' not in comparison:
            crypto_return = comparison['crypto_performance']['avg_annual_return']
            traditional_return = comparison['traditional_performance']['avg_annual_return']
            
            if crypto_return > traditional_return:
                insights.append(f"🚀 Crypto outperformed traditional markets by {crypto_return - traditional_return:.1f}% annually")
            else:
                insights.append(f"🏛️ Traditional markets outperformed crypto by {traditional_return - crypto_return:.1f}% annually")
        
        return insights
    
    def save_analysis(self, filename=None):
        """
        Save analysis results to file
        
        Args:
            filename (str): Optional filename
        """
        if filename is None:
            filename = f"results/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Create results folder if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Generate comprehensive analysis
        performance = self.calculate_performance_metrics()
        insights = self.generate_insights()
        correlations = self.calculate_correlations()
        
        with open(filename, 'w') as f:
            f.write("CRYPTO VS TRADITIONAL MARKETS ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("PERFORMANCE METRICS:\n")
            f.write("-" * 20 + "\n")
            f.write(performance.to_string())
            f.write("\n\n")
            
            f.write("KEY INSIGHTS:\n")
            f.write("-" * 20 + "\n")
            for insight in insights:
                f.write(f"{insight}\n")
            f.write("\n")
            
            f.write("CORRELATION MATRIX:\n")
            f.write("-" * 20 + "\n")
            f.write(correlations.to_string())
            f.write("\n\n")
            
            f.write(f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ Analysis saved to {filename}")

# Example usage
if __name__ == "__main__":
    # This would typically load data from the collector
    print("🔍 Market Analyzer - Run this after collecting data!")
    print("Import this module and use: analyzer = MarketAnalyzer(your_data_df)")