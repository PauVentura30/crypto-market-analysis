"""
Analysis service classes for financial calculations and technical analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
import structlog

logger = structlog.get_logger()


class PerformanceAnalyzer:
    """Class for performance and risk analysis calculations"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate simple returns from price series"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
            else:
                returns.append(0)
        
        return returns
    
    def calculate_log_returns(self, prices: List[float]) -> List[float]:
        """Calculate logarithmic returns"""
        if len(prices) < 2:
            return []
        
        return [np.log(prices[i] / prices[i-1]) for i in range(1, len(prices)) if prices[i-1] > 0]
    
    def calculate_total_return(self, prices: List[float]) -> float:
        """Calculate total return over the period"""
        if len(prices) < 2 or prices[0] == 0:
            return 0.0
        
        return (prices[-1] - prices[0]) / prices[0] * 100
    
    def calculate_annualized_return(self, returns: List[float], periods_per_year: int = 252) -> float:
        """Calculate annualized return"""
        if not returns:
            return 0.0
        
        avg_return = np.mean(returns)
        return (1 + avg_return) ** periods_per_year - 1
    
    def calculate_volatility(self, returns: List[float], annualized: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(returns) < 2:
            return 0.0
        
        vol = np.std(returns, ddof=1)
        
        if annualized:
            vol *= np.sqrt(252)  # Annualize assuming 252 trading days
        
        return vol * 100  # Return as percentage
    
    def calculate_rolling_volatility(self, returns: List[float], window: int = 20) -> List[float]:
        """Calculate rolling volatility"""
        if len(returns) < window:
            return []
        
        rolling_vol = []
        for i in range(window, len(returns) + 1):
            window_returns = returns[i-window:i]
            vol = np.std(window_returns, ddof=1) * np.sqrt(252) * 100
            rolling_vol.append(vol)
        
        return rolling_vol
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        avg_return = np.mean(returns)
        vol = np.std(returns, ddof=1)
        
        if vol == 0:
            return 0.0
        
        # Annualize the ratio
        annual_avg_return = (1 + avg_return) ** 252 - 1
        annual_vol = vol * np.sqrt(252)
        
        return (annual_avg_return - self.risk_free_rate) / annual_vol
    
    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(prices) < 2:
            return 0.0
        
        peak = prices[0]
        max_dd = 0.0
        
        for price in prices[1:]:
            if price > peak:
                peak = price
            
            drawdown = (peak - price) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd * 100  # Return as percentage
    
    def calculate_calmar_ratio(self, returns: List[float], prices: List[float]) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)"""
        if len(returns) < 2 or len(prices) < 2:
            return 0.0
        
        annual_return = self.calculate_annualized_return(returns)
        max_dd = self.calculate_max_drawdown(prices)
        
        if max_dd == 0:
            return 0.0
        
        return annual_return / (max_dd / 100)
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if len(returns) < 2:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100) * 100
    
    def calculate_cvar(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if len(returns) < 2:
            return 0.0
        
        var = self.calculate_var(returns, confidence_level) / 100
        tail_returns = [r for r in returns if r <= var]
        
        if not tail_returns:
            return 0.0
        
        return np.mean(tail_returns) * 100
    
    def calculate_garch_volatility(self, returns: List[float]) -> float:
        """Simplified GARCH-like volatility calculation"""
        if len(returns) < 10:
            return self.calculate_volatility(returns)
        
        # Simple EWMA as GARCH approximation
        lambda_param = 0.94
        ewma_var = np.var(returns[:10])
        
        for ret in returns[10:]:
            ewma_var = lambda_param * ewma_var + (1 - lambda_param) * ret**2
        
        return np.sqrt(ewma_var * 252) * 100
    
    def detect_volatility_clustering(self, returns: List[float]) -> Dict[str, Any]:
        """Detect volatility clustering patterns"""
        if len(returns) < 20:
            return {"clustering_detected": False, "strength": 0}
        
        # Calculate absolute returns
        abs_returns = [abs(r) for r in returns]
        
        # Test for autocorrelation in absolute returns
        try:
            from scipy.stats import pearsonr
            
            # Lag-1 autocorrelation
            lag1_corr, p_value = pearsonr(abs_returns[:-1], abs_returns[1:])
            
            clustering_strength = abs(lag1_corr)
            clustering_detected = p_value < 0.05 and clustering_strength > 0.1
            
            return {
                "clustering_detected": clustering_detected,
                "strength": clustering_strength,
                "p_value": p_value
            }
        except:
            return {"clustering_detected": False, "strength": 0}
    
    def identify_volatility_regime(self, returns: List[float]) -> str:
        """Identify current volatility regime"""
        if len(returns) < 30:
            return "insufficient_data"
        
        recent_vol = self.calculate_volatility(returns[-20:])
        overall_vol = self.calculate_volatility(returns)
        
        if recent_vol > overall_vol * 1.5:
            return "high_volatility"
        elif recent_vol < overall_vol * 0.7:
            return "low_volatility"
        else:
            return "normal_volatility"
    
    def assess_market_regime(self, volatility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall market regime based on multiple assets"""
        if not volatility_results:
            return {"regime": "unknown", "confidence": 0}
        
        regimes = []
        for symbol, analysis in volatility_results.items():
            regimes.append(analysis.get("volatility_regime", "normal_volatility"))
        
        regime_counts = {}
        for regime in regimes:
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        dominant_regime = max(regime_counts, key=regime_counts.get)
        confidence = regime_counts[dominant_regime] / len(regimes)
        
        return {
            "regime": dominant_regime,
            "confidence": confidence,
            "regime_distribution": regime_counts
        }


class TechnicalAnalyzer:
    """Class for technical analysis calculations"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with OHLCV data
        Expected columns: timestamp, open, high, low, close, volume
        """
        self.data = data.copy()
        self.data.set_index('timestamp', inplace=True)
    
    def calculate_sma(self, period: int = 20) -> Dict[str, Any]:
        """Calculate Simple Moving Average"""
        sma = self.data['close'].rolling(window=period).mean()
        current_sma = sma.iloc[-1] if not sma.empty else None
        current_price = self.data['close'].iloc[-1]
        
        return {
            "values": sma.tolist(),
            "current_value": current_sma,
            "signal": "bullish" if current_price > current_sma else "bearish",
            "period": period
        }
    
    def calculate_ema(self, period: int = 20) -> Dict[str, Any]:
        """Calculate Exponential Moving Average"""
        ema = self.data['close'].ewm(span=period).mean()
        current_ema = ema.iloc[-1] if not ema.empty else None
        current_price = self.data['close'].iloc[-1]
        
        return {
            "values": ema.tolist(),
            "current_value": current_ema,
            "signal": "bullish" if current_price > current_ema else "bearish",
            "period": period
        }
    
    def calculate_rsi(self, period: int = 14) -> Dict[str, Any]:
        """Calculate Relative Strength Index"""
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        # Generate signal
        if current_rsi > 70:
            signal = "overbought"
        elif current_rsi < 30:
            signal = "oversold"
        else:
            signal = "neutral"
        
        return {
            "values": rsi.tolist(),
            "current_value": current_rsi,
            "signal": signal,
            "overbought_level": 70,
            "oversold_level": 30
        }
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = self.data['close'].ewm(span=fast).mean()
        ema_slow = self.data['close'].ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        current_macd = macd_line.iloc[-1] if not macd_line.empty else 0
        current_signal = signal_line.iloc[-1] if not signal_line.empty else 0
        current_histogram = histogram.iloc[-1] if not histogram.empty else 0
        
        # Generate signal
        if current_macd > current_signal and current_histogram > 0:
            macd_signal = "bullish"
        elif current_macd < current_signal and current_histogram < 0:
            macd_signal = "bearish"
        else:
            macd_signal = "neutral"
        
        return {
            "macd_line": macd_line.tolist(),
            "signal_line": signal_line.tolist(),
            "histogram": histogram.tolist(),
            "current_macd": current_macd,
            "current_signal": current_signal,
            "current_histogram": current_histogram,
            "signal": macd_signal
        }
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        sma = self.data['close'].rolling(window=period).mean()
        std = self.data['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = self.data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1] if not upper_band.empty else current_price
        current_lower = lower_band.iloc[-1] if not lower_band.empty else current_price
        current_sma = sma.iloc[-1] if not sma.empty else current_price
        
        # Generate signal
        if current_price > current_upper:
            bb_signal = "overbought"
        elif current_price < current_lower:
            bb_signal = "oversold"
        else:
            bb_signal = "neutral"
        
        return {
            "upper_band": upper_band.tolist(),
            "middle_band": sma.tolist(),
            "lower_band": lower_band.tolist(),
            "current_upper": current_upper,
            "current_middle": current_sma,
            "current_lower": current_lower,
            "signal": bb_signal,
            "bandwidth": ((current_upper - current_lower) / current_sma) * 100 if current_sma != 0 else 0
        }
    
    def find_support_resistance(self, window: int = 20) -> Dict[str, Any]:
        """Find support and resistance levels"""
        highs = self.data['high'].rolling(window=window, center=True).max()
        lows = self.data['low'].rolling(window=window, center=True).min()
        
        # Find local peaks and troughs
        resistance_levels = []
        support_levels = []
        
        for i in range(window, len(self.data) - window):
            if self.data['high'].iloc[i] == highs.iloc[i]:
                resistance_levels.append(self.data['high'].iloc[i])
            if self.data['low'].iloc[i] == lows.iloc[i]:
                support_levels.append(self.data['low'].iloc[i])
        
        # Get current levels
        current_price = self.data['close'].iloc[-1]
        
        # Find nearest support and resistance
        resistance_above = [r for r in resistance_levels if r > current_price]
        support_below = [s for s in support_levels if s < current_price]
        
        nearest_resistance = min(resistance_above) if resistance_above else None
        nearest_support = max(support_below) if support_below else None
        
        return {
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "all_support_levels": sorted(set(support_levels), reverse=True)[:5],
            "all_resistance_levels": sorted(set(resistance_levels))[:5],
            "current_price": current_price
        }
    
    def generate_signals(self, indicators: List[str]) -> Dict[str, str]:
        """Generate combined trading signals"""
        signals = {}
        
        for indicator in indicators:
            if indicator == "sma":
                signals["sma"] = self.calculate_sma()["signal"]
            elif indicator == "ema":
                signals["ema"] = self.calculate_ema()["signal"]
            elif indicator == "rsi":
                signals["rsi"] = self.calculate_rsi()["signal"]
            elif indicator == "macd":
                signals["macd"] = self.calculate_macd()["signal"]
            elif indicator == "bollinger":
                signals["bollinger"] = self.calculate_bollinger_bands()["signal"]
        
        # Overall signal
        bullish_count = sum(1 for signal in signals.values() if signal == "bullish")
        bearish_count = sum(1 for signal in signals.values() if signal == "bearish")
        
        if bullish_count > bearish_count:
            signals["overall"] = "bullish"
        elif bearish_count > bullish_count:
            signals["overall"] = "bearish"
        else:
            signals["overall"] = "neutral"
        
        return signals
    
    def assess_sentiment(self) -> Dict[str, Any]:
        """Assess market sentiment based on technical indicators"""
        current_price = self.data['close'].iloc[-1]
        
        # Price momentum
        price_change_1d = ((current_price - self.data['close'].iloc[-2]) / self.data['close'].iloc[-2]) * 100 if len(self.data) > 1 else 0
        price_change_5d = ((current_price - self.data['close'].iloc[-6]) / self.data['close'].iloc[-6]) * 100 if len(self.data) > 5 else 0
        
        # Volume analysis
        avg_volume = self.data['volume'].tail(20).mean() if 'volume' in self.data.columns else 0
        current_volume = self.data['volume'].iloc[-1] if 'volume' in self.data.columns else 0
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Volatility
        returns = self.data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 1 else 0
        
        # Sentiment score calculation
        sentiment_score = 0
        
        # Price momentum contribution
        if price_change_1d > 2:
            sentiment_score += 2
        elif price_change_1d > 0:
            sentiment_score += 1
        elif price_change_1d < -2:
            sentiment_score -= 2
        elif price_change_1d < 0:
            sentiment_score -= 1
        
        # Volume contribution
        if volume_ratio > 1.5:
            sentiment_score += 1
        elif volume_ratio < 0.7:
            sentiment_score -= 1
        
        # Volatility contribution (high volatility can be negative)
        if volatility > 50:
            sentiment_score -= 1
        
        # Convert to sentiment label
        if sentiment_score >= 2:
            sentiment_label = "very_bullish"
        elif sentiment_score == 1:
            sentiment_label = "bullish"
        elif sentiment_score == 0:
            sentiment_label = "neutral"
        elif sentiment_score == -1:
            sentiment_label = "bearish"
        else:
            sentiment_label = "very_bearish"
        
        return {
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "price_momentum_1d": price_change_1d,
            "price_momentum_5d": price_change_5d,
            "volume_ratio": volume_ratio,
            "volatility": volatility,
            "analysis_factors": {
                "price_trend": "positive" if price_change_1d > 0 else "negative",
                "volume_trend": "high" if volume_ratio > 1.2 else "normal" if volume_ratio > 0.8 else "low",
                "volatility_level": "high" if volatility > 30 else "normal" if volatility > 15 else "low"
            }
        }


class CorrelationAnalyzer:
    """Class for correlation analysis between assets"""
    
    def __init__(self):
        pass
    
    def calculate_correlation_matrix(self, price_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate correlation matrix for multiple assets"""
        if len(price_data) < 2:
            return {}
        
        # Create DataFrame from price data
        df = pd.DataFrame(price_data)
        
        # Calculate returns
        returns_df = df.pct_change().dropna()
        
        if returns_df.empty:
            return {}
        
        # Correlation matrix
        correlation_matrix = returns_df.corr()
        
        # Convert to dictionary format
        correlation_dict = {}
        for asset1 in correlation_matrix.columns:
            correlation_dict[asset1] = {}
            for asset2 in correlation_matrix.columns:
                correlation_dict[asset1][asset2] = correlation_matrix.loc[asset1, asset2]
        
        # Find strongest correlations
        strong_correlations = []
        for asset1 in correlation_matrix.columns:
            for asset2 in correlation_matrix.columns:
                if asset1 != asset2:
                    corr_value = correlation_matrix.loc[asset1, asset2]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            "asset1": asset1,
                            "asset2": asset2,
                            "correlation": corr_value,
                            "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                        })
        
        return {
            "correlation_matrix": correlation_dict,
            "strong_correlations": strong_correlations,
            "average_correlation": correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, 1)].mean(),
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def calculate_rolling_correlation(
        self, 
        price_data1: List[float], 
        price_data2: List[float], 
        window: int = 30
    ) -> List[float]:
        """Calculate rolling correlation between two assets"""
        if len(price_data1) != len(price_data2) or len(price_data1) < window:
            return []
        
        df = pd.DataFrame({
            'asset1': price_data1,
            'asset2': price_data2
        })
        
        returns_df = df.pct_change().dropna()
        
        if len(returns_df) < window:
            return []
        
        rolling_corr = returns_df['asset1'].rolling(window=window).corr(returns_df['asset2'])
        
        return rolling_corr.dropna().tolist()
    
    def analyze_correlation_stability(
        self, 
        price_data1: List[float], 
        price_data2: List[float]
    ) -> Dict[str, Any]:
        """Analyze correlation stability over time"""
        rolling_corr = self.calculate_rolling_correlation(price_data1, price_data2)
        
        if not rolling_corr:
            return {"stable": False, "reason": "insufficient_data"}
        
        corr_std = np.std(rolling_corr)
        corr_mean = np.mean(rolling_corr)
        
        # Stability criteria
        is_stable = corr_std < 0.2  # Standard deviation threshold
        
        return {
            "stable": is_stable,
            "mean_correlation": corr_mean,
            "correlation_volatility": corr_std,
            "stability_score": 1 - min(corr_std / 0.5, 1),  # Normalized stability score
            "recent_correlation": rolling_corr[-1] if rolling_corr else 0,
            "correlation_trend": "increasing" if len(rolling_corr) > 10 and rolling_corr[-5:] > rolling_corr[-10:-5] else "decreasing" if len(rolling_corr) > 10 else "stable"
        }


class RiskAnalyzer:
    """Class for risk analysis and metrics"""
    
    def __init__(self):
        self.confidence_levels = [0.90, 0.95, 0.99]
    
    def calculate_portfolio_var(
        self, 
        returns_data: Dict[str, List[float]], 
        weights: Dict[str, float],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Calculate portfolio Value at Risk"""
        if not returns_data or not weights:
            return {}
        
        # Create returns DataFrame
        df = pd.DataFrame(returns_data)
        
        # Calculate portfolio returns
        portfolio_returns = []
        for i in range(len(df)):
            port_return = sum(df.iloc[i][asset] * weights.get(asset, 0) for asset in df.columns)
            portfolio_returns.append(port_return)
        
        # Calculate VaR
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        
        # Calculate Expected Shortfall (CVaR)
        tail_returns = [r for r in portfolio_returns if r <= var]
        cvar = np.mean(tail_returns) if tail_returns else var
        
        return {
            "var": var * 100,  # Convert to percentage
            "cvar": cvar * 100,
            "confidence_level": confidence_level,
            "portfolio_volatility": np.std(portfolio_returns) * np.sqrt(252) * 100,
            "worst_return": min(portfolio_returns) * 100,
            "best_return": max(portfolio_returns) * 100
        }
    
    def calculate_beta(self, asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta (systematic risk) relative to market"""
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0
        
        # Calculate covariance and variance
        asset_array = np.array(asset_returns)
        market_array = np.array(market_returns)
        
        covariance = np.cov(asset_array, market_array)[0, 1]
        market_variance = np.var(market_array, ddof=1)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return beta
    
    def assess_risk_profile(self, returns: List[float]) -> Dict[str, Any]:
        """Assess overall risk profile of an asset"""
        if len(returns) < 10:
            return {"risk_level": "unknown", "reason": "insufficient_data"}
        
        volatility = np.std(returns) * np.sqrt(252) * 100
        var_95 = np.percentile(returns, 5) * 100
        max_loss = min(returns) * 100
        
        # Risk categorization
        if volatility > 50:
            risk_level = "very_high"
        elif volatility > 30:
            risk_level = "high"
        elif volatility > 15:
            risk_level = "medium"
        elif volatility > 8:
            risk_level = "low"
        else:
            risk_level = "very_low"
        
        return {
            "risk_level": risk_level,
            "volatility": volatility,
            "var_95": var_95,
            "maximum_loss": max_loss,
            "risk_score": min(volatility / 10, 10),  # 0-10 scale
            "risk_factors": {
                "volatility_risk": "high" if volatility > 30 else "moderate" if volatility > 15 else "low",
                "tail_risk": "high" if var_95 < -5 else "moderate" if var_95 < -2 else "low",
                "extreme_loss_risk": "high" if max_loss < -20 else "moderate" if max_loss < -10 else "low"
            }
        }