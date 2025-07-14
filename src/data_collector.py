"""
Crypto Market Analysis - Data Collector
Author: [Tu nombre]
Description: Collects cryptocurrency and traditional market data from APIs
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import time

class CryptoMarketCollector:
    """
    Collects data from cryptocurrency and traditional markets
    """
    
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.data_folder = "data"
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def get_crypto_data(self, crypto_ids, days=365):
        """
        Get cryptocurrency historical data from CoinGecko
        
        Args:
            crypto_ids (list): List of cryptocurrency IDs (e.g., ['bitcoin', 'ethereum'])
            days (int): Number of days of historical data
            
        Returns:
            pd.DataFrame: DataFrame with crypto prices
        """
        crypto_data = {}
        
        for crypto_id in crypto_ids:
            try:
                url = f"{self.coingecko_base_url}/coins/{crypto_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Convert to DataFrame
                prices = data['prices']
                df = pd.DataFrame(prices, columns=['timestamp', f'{crypto_id}_price'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df.drop('timestamp', axis=1)
                df = df.set_index('date')
                
                crypto_data[crypto_id] = df
                
                print(f"✅ Successfully collected {crypto_id} data")
                time.sleep(1)  # Be nice to the API
                
            except Exception as e:
                print(f"❌ Error collecting {crypto_id}: {str(e)}")
                continue
        
        # Combine all crypto data
        if crypto_data:
            combined_df = pd.concat(crypto_data.values(), axis=1)
            return combined_df
        else:
            return pd.DataFrame()
    
    def get_traditional_market_data(self, symbols, period="1y"):
        """
        Get traditional market data from Yahoo Finance
        
        Args:
            symbols (list): List of stock symbols (e.g., ['SPY', 'QQQ'])
            period (str): Period of data ('1y', '2y', '5y', etc.)
            
        Returns:
            pd.DataFrame: DataFrame with traditional market prices
        """
        traditional_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                # Get closing prices
                df = pd.DataFrame()
                df[f'{symbol}_price'] = hist['Close']
                df.index = pd.to_datetime(df.index).date
                df.index = pd.to_datetime(df.index)
                
                traditional_data[symbol] = df
                
                print(f"✅ Successfully collected {symbol} data")
                
            except Exception as e:
                print(f"❌ Error collecting {symbol}: {str(e)}")
                continue
        
        # Combine all traditional market data
        if traditional_data:
            combined_df = pd.concat(traditional_data.values(), axis=1)
            return combined_df
        else:
            return pd.DataFrame()
    
    def get_combined_data(self, crypto_ids=['bitcoin', 'ethereum'], 
                         traditional_symbols=['SPY', 'QQQ', 'GLD'], 
                         days=365):
        """
        Get both crypto and traditional market data combined
        
        Args:
            crypto_ids (list): Cryptocurrency IDs
            traditional_symbols (list): Traditional market symbols
            days (int): Days of historical data
            
        Returns:
            pd.DataFrame: Combined dataset
        """
        print("🚀 Starting data collection...")
        
        # Get crypto data
        print("\n📈 Collecting cryptocurrency data...")
        crypto_df = self.get_crypto_data(crypto_ids, days)
        
        # Get traditional market data
        print("\n📊 Collecting traditional market data...")
        traditional_df = self.get_traditional_market_data(traditional_symbols, "1y")
        
        # Combine datasets
        if not crypto_df.empty and not traditional_df.empty:
            # Align dates
            combined_df = pd.concat([crypto_df, traditional_df], axis=1)
            combined_df = combined_df.dropna()
            
            # Save to CSV
            filename = f"{self.data_folder}/market_data_{datetime.now().strftime('%Y%m%d')}.csv"
            combined_df.to_csv(filename)
            
            print(f"\n✅ Data saved to {filename}")
            print(f"📊 Dataset shape: {combined_df.shape}")
            print(f"📅 Date range: {combined_df.index.min()} to {combined_df.index.max()}")
            
            return combined_df
        else:
            print("❌ Failed to collect data")
            return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    collector = CryptoMarketCollector()
    
    # Define what we want to analyze
    cryptos = ['bitcoin', 'ethereum', 'cardano', 'solana']
    traditional = ['SPY', 'QQQ', 'GLD', 'BTC-USD']  # S&P 500, NASDAQ, Gold, Bitcoin ETF
    
    # Collect data
    data = collector.get_combined_data(
        crypto_ids=cryptos,
        traditional_symbols=traditional,
        days=365
    )
    
    if not data.empty:
        print("\n🎉 Data collection complete!")
        print(data.head())
    else:
        print("❌ No data collected")