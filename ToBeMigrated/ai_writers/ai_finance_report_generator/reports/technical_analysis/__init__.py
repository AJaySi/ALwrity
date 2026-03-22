"""
Technical Analysis Reports Module

This module handles the generation of technical analysis reports using yfinance data and pandas_ta for indicators.
"""

from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta
from loguru import logger
from ...utils import validate_symbol
from ...ai_financial_dashboard import get_dashboard

class TechnicalAnalysis:
    def __init__(self, symbol: str, timeframe: str = "1d", period: str = "1y"):
        """
        Initialize Technical Analysis.
        
        Args:
            symbol (str): Stock symbol to analyze
            timeframe (str): Data timeframe (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        logger.info(f"Initializing Technical Analysis for {symbol} with timeframe {timeframe} and period {period}")
        self.symbol = symbol
        self.timeframe = timeframe
        self.period = period
        self.data = None
        self.indicators = {}
        self.stock = yf.Ticker(symbol)
        
    def fetch_data(self) -> None:
        """Fetch historical price data using yfinance"""
        try:
            logger.info(f"Fetching historical data for {self.symbol}")
            # Get historical data
            self.data = self.stock.history(period=self.period, interval=self.timeframe)
            logger.debug(f"Retrieved {len(self.data)} data points")
            
            # Get additional info
            logger.info("Fetching company information")
            self.info = self.stock.info
            
            # Calculate basic metrics
            logger.debug("Calculating basic metrics")
            self.data['Returns'] = self.data['Close'].pct_change()
            self.data['Volatility'] = self.data['Returns'].rolling(window=20).std()
            
            logger.success(f"Successfully fetched data for {self.symbol}")
            
        except Exception as e:
            logger.error(f"Error fetching data for {self.symbol}: {str(e)}")
            raise ValueError(f"Error fetching data for {self.symbol}: {str(e)}")
        
    def calculate_indicators(self) -> None:
        """Calculate technical indicators using pandas_ta"""
        if self.data is None:
            logger.error("Data not fetched. Call fetch_data() first.")
            raise ValueError("Data not fetched. Call fetch_data() first.")
            
        logger.info("Calculating technical indicators")
        
        # Moving Averages
        logger.debug("Calculating Moving Averages")
        self.indicators['sma_20'] = self.data.ta.sma(length=20)
        self.indicators['sma_50'] = self.data.ta.sma(length=50)
        self.indicators['sma_200'] = self.data.ta.sma(length=200)
        self.indicators['ema_20'] = self.data.ta.ema(length=20)
        
        # RSI
        logger.debug("Calculating RSI")
        self.indicators['rsi'] = self.data.ta.rsi()
        
        # MACD
        logger.debug("Calculating MACD")
        macd = self.data.ta.macd()
        self.indicators['macd'] = macd['MACD_12_26_9']
        self.indicators['macd_signal'] = macd['MACDs_12_26_9']
        self.indicators['macd_hist'] = macd['MACDh_12_26_9']
        
        # Bollinger Bands
        logger.debug("Calculating Bollinger Bands")
        bbands = self.data.ta.bbands()
        self.indicators['bb_upper'] = bbands['BBU_20_2.0']
        self.indicators['bb_middle'] = bbands['BBM_20_2.0']
        self.indicators['bb_lower'] = bbands['BBL_20_2.0']
        
        # Volume Analysis
        logger.debug("Calculating Volume indicators")
        self.indicators['volume_sma'] = self.data['Volume'].rolling(window=20).mean()
        self.indicators['obv'] = self.data.ta.obv()
        
        # Additional Indicators
        logger.debug("Calculating additional indicators")
        self.indicators['stoch'] = self.data.ta.stoch()
        self.indicators['adx'] = self.data.ta.adx()
        self.indicators['atr'] = self.data.ta.atr()
        
        logger.success("Successfully calculated all technical indicators")
        
    def identify_patterns(self) -> List[Dict[str, Any]]:
        """Identify chart patterns"""
        logger.info("Identifying chart patterns")
        patterns = []
        
        # Candlestick Patterns
        if len(self.data) >= 3:
            logger.debug("Analyzing candlestick patterns")
            # Doji
            doji = self.data.ta.cdl_doji()
            if doji['CDL_DOJI'].iloc[-1] != 0:
                logger.debug("Doji pattern detected")
                patterns.append({
                    'type': 'doji',
                    'date': self.data.index[-1],
                    'significance': 'neutral'
                })
            
            # Engulfing
            engulfing = self.data.ta.cdl_engulfing()
            if engulfing['CDL_ENGULFING'].iloc[-1] != 0:
                logger.debug("Engulfing pattern detected")
                patterns.append({
                    'type': 'engulfing',
                    'date': self.data.index[-1],
                    'significance': 'bullish' if engulfing['CDL_ENGULFING'].iloc[-1] > 0 else 'bearish'
                })
        
        logger.info(f"Identified {len(patterns)} patterns")
        return patterns
        
    def find_support_resistance(self) -> Dict[str, List[float]]:
        """Find support and resistance levels using price action"""
        logger.info("Finding support and resistance levels")
        levels = {
            'support': [],
            'resistance': []
        }
        
        # Use recent price action to identify levels
        recent_data = self.data.tail(100)
        logger.debug(f"Analyzing {len(recent_data)} recent data points for S/R levels")
        
        # Find local minima and maxima
        for i in range(2, len(recent_data) - 2):
            # Support level
            if (recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-1] and 
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-2] and
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+1] and
                recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+2]):
                levels['support'].append(recent_data['Low'].iloc[i])
            
            # Resistance level
            if (recent_data['High'].iloc[i] > recent_data['High'].iloc[i-1] and 
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i-2] and
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i+1] and
                recent_data['High'].iloc[i] > recent_data['High'].iloc[i+2]):
                levels['resistance'].append(recent_data['High'].iloc[i])
        
        # Remove duplicates and sort
        levels['support'] = sorted(list(set(levels['support'])))
        levels['resistance'] = sorted(list(set(levels['resistance'])))
        
        logger.info(f"Found {len(levels['support'])} support and {len(levels['resistance'])} resistance levels")
        return levels
        
    def generate_chart(self) -> go.Figure:
        """Generate interactive chart using plotly"""
        logger.info("Generating interactive chart")
        fig = go.Figure()
        
        # Candlestick chart
        logger.debug("Adding candlestick chart")
        fig.add_trace(go.Candlestick(
            x=self.data.index,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='Price'
        ))
        
        # Moving Averages
        logger.debug("Adding moving averages")
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.indicators['sma_20'],
            name='SMA 20',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.indicators['sma_50'],
            name='SMA 50',
            line=dict(color='orange')
        ))
        
        # Bollinger Bands
        logger.debug("Adding Bollinger Bands")
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.indicators['bb_upper'],
            name='BB Upper',
            line=dict(color='gray', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.indicators['bb_lower'],
            name='BB Lower',
            line=dict(color='gray', dash='dash'),
            fill='tonexty'
        ))
        
        # Volume
        logger.debug("Adding volume bars")
        fig.add_trace(go.Bar(
            x=self.data.index,
            y=self.data['Volume'],
            name='Volume',
            marker_color='rgba(0,0,255,0.3)'
        ))
        
        # Layout
        logger.debug("Setting chart layout")
        fig.update_layout(
            title=f'{self.symbol} Technical Analysis',
            yaxis_title='Price',
            xaxis_title='Date',
            template='plotly_dark'
        )
        
        logger.success("Successfully generated chart")
        return fig
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of technical analysis"""
        logger.info("Generating analysis summary")
        current_price = self.data['Close'].iloc[-1]
        sma_20 = self.indicators['sma_20'].iloc[-1]
        sma_50 = self.indicators['sma_50'].iloc[-1]
        rsi = self.indicators['rsi'].iloc[-1]
        
        summary = {
            'current_price': current_price,
            'price_change': self.data['Returns'].iloc[-1] * 100,
            'trend': 'bullish' if current_price > sma_20 > sma_50 else 'bearish',
            'rsi_signal': 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral',
            'volatility': self.data['Volatility'].iloc[-1],
            'volume_trend': 'increasing' if self.data['Volume'].iloc[-1] > self.indicators['volume_sma'].iloc[-1] else 'decreasing'
        }
        
        logger.debug(f"Analysis summary: {summary}")
        return summary
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive technical analysis report"""
        logger.info(f"Generating comprehensive report for {self.symbol}")
        
        self.fetch_data()
        self.calculate_indicators()
        patterns = self.identify_patterns()
        levels = self.find_support_resistance()
        chart = self.generate_chart()
        summary = self._generate_summary()
        
        report = {
            'symbol': self.symbol,
            'timestamp': datetime.now(),
            'company_info': self.info,
            'indicators': self.indicators,
            'patterns': patterns,
            'levels': levels,
            'chart': chart,
            'summary': summary
        }
        
        logger.success(f"Successfully generated report for {self.symbol}")
        return report

def generate_ta_report(symbol: str) -> Dict[str, Any]:
    """
    Generate a technical analysis report for the given symbol.
    
    Args:
        symbol (str): Stock symbol to analyze
        
    Returns:
        Dict[str, Any]: Technical analysis report
    """
    logger.info(f"Generating technical analysis report for {symbol}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol provided: {symbol}")
        raise ValueError("Invalid symbol provided")
        
    try:
        analysis = TechnicalAnalysis(symbol)
        report = analysis.generate_report()
        
        # Add to dashboard's recent reports
        dashboard = get_dashboard()
        dashboard.add_recent_report("technical_analysis", symbol, report)
        
        logger.success(f"Successfully completed technical analysis for {symbol}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating technical analysis report for {symbol}: {str(e)}")
        raise 