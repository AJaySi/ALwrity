"""
AI Financial Dashboard Module

This module combines the financial dashboard interface with financial report generation capabilities.
It provides a unified interface for managing financial analysis tools and generating reports.
"""

import sys
import os
from textwrap import dedent
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from loguru import logger
logger.remove()
logger.add(sys.stdout,
        colorize=True,
        format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
    )

from ...ai_web_researcher.finance_data_researcher import get_finance_data, get_fin_options_data
from ...gpt_providers.text_generation.main_text_generation import llm_text_gen
from .utils import get_feature_status
from .utils.storage import get_storage_manager

class UserPreferences:
    """Class to manage user preferences and settings."""
    
    def __init__(self):
        self.default_settings = {
            "theme": "light",
            "currency": "USD",
            "timezone": "UTC",
            "date_format": "%Y-%m-%d",
            "default_symbols": [],
            "notifications": True,
            "auto_refresh": False,
            "refresh_interval": 300,  # 5 minutes
            "report_format": "markdown",
            "include_charts": True,
            "chart_style": "default",
            "language": "en"
        }
        self.settings = self.default_settings.copy()
        self.storage = get_storage_manager()
        self.load_settings()
    
    def update_setting(self, key: str, value: Any) -> None:
        """Update a specific setting."""
        if key in self.default_settings:
            self.settings[key] = value
            self.save_settings()
    
    def get_setting(self, key: str) -> Any:
        """Get a specific setting value."""
        return self.settings.get(key, self.default_settings.get(key))
    
    def reset_settings(self) -> None:
        """Reset all settings to default values."""
        self.settings = self.default_settings.copy()
        self.save_settings()
    
    def save_settings(self) -> None:
        """Save current settings to storage."""
        self.storage.save_user_preferences(self.settings)
    
    def load_settings(self) -> None:
        """Load settings from storage."""
        stored_settings = self.storage.load_user_preferences()
        if stored_settings:
            self.settings.update(stored_settings)

class RecentReport:
    """Class to represent a recently generated report."""
    
    def __init__(self, report_type: str, symbol: Optional[str], timestamp: datetime, content: Optional[str] = None):
        self.report_type = report_type
        self.symbol = symbol
        self.timestamp = timestamp
        self.content = content
        self.id = f"{report_type}_{symbol}_{timestamp.strftime('%Y%m%d%H%M%S')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "id": self.id,
            "type": self.report_type,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecentReport':
        """Create report from dictionary format."""
        return cls(
            report_type=data["type"],
            symbol=data["symbol"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data.get("content")
        )

class FinancialDashboard:
    """Main dashboard class for managing financial analysis tools and generating reports."""
    
    def __init__(self):
        self.features = {
            "technical_analysis": {
                "name": "Technical Analysis",
                "description": "Generate technical analysis reports with indicators and patterns",
                "icon": "📊",
                "route": "/technical-analysis",
                "category": "analysis",
                "dependencies": ["data_collection"],
                "version": "1.0.0"
            },
            "fundamental_analysis": {
                "name": "Fundamental Analysis",
                "description": "Analyze company financials and valuation metrics",
                "icon": "📈",
                "route": "/fundamental-analysis",
                "category": "analysis",
                "dependencies": ["data_collection"],
                "version": "0.1.0"
            },
            "options_analysis": {
                "name": "Options Analysis",
                "description": "Analyze options chains and generate trading strategies",
                "icon": "⚡",
                "route": "/options-analysis",
                "category": "analysis",
                "dependencies": ["data_collection", "options_data"],
                "version": "1.0.0"
            },
            "portfolio_analysis": {
                "name": "Portfolio Analysis",
                "description": "Analyze portfolio performance and risk metrics",
                "icon": "📑",
                "route": "/portfolio-analysis",
                "category": "portfolio",
                "dependencies": ["data_collection", "portfolio_data"],
                "version": "0.1.0"
            },
            "market_research": {
                "name": "Market Research",
                "description": "Generate market research reports and sector analysis",
                "icon": "🔍",
                "route": "/market-research",
                "category": "research",
                "dependencies": ["data_collection", "news_data"],
                "version": "0.1.0"
            },
            "news_analysis": {
                "name": "News Analysis",
                "description": "Analyze news impact and market sentiment",
                "icon": "📰",
                "route": "/news-analysis",
                "category": "research",
                "dependencies": ["data_collection", "news_data"],
                "version": "0.1.0"
            }
        }
        
        self.user_preferences = UserPreferences()
        self.storage = get_storage_manager()
        self.recent_reports: List[RecentReport] = []
        self.max_recent_reports = 10
        self.load_recent_reports()
    
    def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all available features with their status."""
        features_list = []
        for feature_id, feature_info in self.features.items():
            status = get_feature_status(feature_id)
            feature_info.update(status)
            features_list.append(feature_info)
        return features_list
    
    def get_feature(self, feature_id: str) -> Dict[str, Any]:
        """Get information about a specific feature."""
        if feature_id not in self.features:
            raise ValueError(f"Feature {feature_id} not found")
            
        feature_info = self.features[feature_id].copy()
        status = get_feature_status(feature_id)
        feature_info.update(status)
        return feature_info
    
    def get_implemented_features(self) -> List[Dict[str, Any]]:
        """Get only the implemented features."""
        return [f for f in self.get_all_features() if f["implemented"]]
    
    def get_coming_soon_features(self) -> List[Dict[str, Any]]:
        """Get features that are coming soon."""
        return [f for f in self.get_all_features() if f["coming_soon"]]
    
    def get_features_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get features filtered by category."""
        return [f for f in self.get_all_features() if f["category"] == category]
    
    def add_recent_report(self, report_type: str, symbol: Optional[str] = None, content: Optional[str] = None) -> None:
        """Add a report to the recent reports list."""
        report = RecentReport(report_type, symbol, datetime.now(), content)
        self.recent_reports.insert(0, report)
        if len(self.recent_reports) > self.max_recent_reports:
            self.recent_reports.pop()
        self.save_recent_reports()
    
    def get_recent_reports(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent reports."""
        reports = self.recent_reports[:limit] if limit else self.recent_reports
        return [{
            **r.to_dict(),
            "feature_info": self.get_feature(r.report_type)
        } for r in reports]
    
    def save_recent_reports(self) -> None:
        """Save recent reports to storage."""
        reports_data = [r.to_dict() for r in self.recent_reports]
        self.storage.save_recent_reports(reports_data)
    
    def load_recent_reports(self) -> None:
        """Load recent reports from storage."""
        reports_data = self.storage.load_recent_reports()
        self.recent_reports = [RecentReport.from_dict(r) for r in reports_data]
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get a summary of the dashboard state."""
        return {
            "total_features": len(self.features),
            "implemented_features": len(self.get_implemented_features()),
            "coming_soon_features": len(self.get_coming_soon_features()),
            "recent_reports": len(self.recent_reports),
            "categories": list(set(f["category"] for f in self.features.values())),
            "user_preferences": self.user_preferences.settings
        }
    
    def check_feature_dependencies(self, feature_id: str) -> Dict[str, bool]:
        """Check if all dependencies for a feature are met."""
        if feature_id not in self.features:
            raise ValueError(f"Feature {feature_id} not found")
            
        feature = self.features[feature_id]
        dependencies = feature.get("dependencies", [])
        
        return {
            dep: get_feature_status(dep)["implemented"]
            for dep in dependencies
        }
    
    def backup_data(self, backup_dir: Optional[str] = None) -> None:
        """Create a backup of all dashboard data."""
        self.storage.backup_storage(backup_dir)
    
    def restore_from_backup(self, backup_file: str) -> None:
        """Restore dashboard data from a backup file."""
        self.storage.restore_from_backup(backup_file)
        self.user_preferences.load_settings()
        self.load_recent_reports()
    
    def generate_technical_analysis(self, symbol: str) -> str:
        """Generate a technical analysis report for the given symbol."""
        try:
            # Get financial data
            symbol_fin_data = get_finance_data(symbol)
            
            # Generate report
            report_content = self._generate_ta_report(symbol_fin_data, symbol)
            
            # Add to recent reports
            self.add_recent_report("technical_analysis", symbol, report_content)
            
            logger.info(f"Done: Final Technical Analysis for {symbol}")
            return report_content
            
        except Exception as err:
            logger.error(f"Error: Failed to generate Technical Analysis report: {err}")
            raise
    
    def generate_options_analysis(self, symbol: str) -> str:
        """Generate an options analysis report for the given symbol."""
        try:
            # Get options data
            options_data = get_fin_options_data(symbol)
            
            # Generate report
            report_content = self._generate_options_report(options_data, symbol)
            
            # Add to recent reports
            self.add_recent_report("options_analysis", symbol, report_content)
            
            logger.info(f"Done: Options Analysis for {symbol}")
            return report_content
            
        except Exception as err:
            logger.error(f"Error: Failed to generate Options Analysis report: {err}")
            raise
    
    def _generate_ta_report(self, last_day_summary: str, symbol: str) -> str:
        """Generate technical analysis report using LLM."""
        prompt = f"""
            You are a seasoned Technical Analysis (TA) expert, rivaling legends like Charles Dow, John Bollinger, and Alan Andrews. 
            Your deep understanding of market dynamics, coupled with mastery of technical indicators, 
            allows you to decipher complex patterns and offer precise predictions.

            Your expertise extends to practical tools like the pandas_ta module, enabling you to extract valuable insights from raw data.

            **Objective:**
            Analyze the provided technical indicators for {symbol} on its last trading day and predict its price movement over the next few trading sessions.

            **Instructions:**
            1. **Identify Potential Trading Signals:** Highlight specific indicators suggesting bullish, bearish, or neutral signals. Explain the rationale behind each signal, referencing historical patterns or comparable market scenarios.
            2. **Detect Patterns and Divergences:** Analyze the interplay between different indicators. Detect patterns like moving average crossovers, candlestick formations, or divergences between price action and indicators. Explain the significance of each pattern.
            3. **Price Movement Prediction:** Based on your analysis, provide a clear prediction for {symbol}'s price movement in the next few days. State the expected direction (up, down, sideways) and potential price targets if identifiable.
            4. **Risk Assessment:** Briefly discuss any potential risks or factors that could invalidate your predictions, promoting a balanced and informed perspective.

            **Technical Indicators for {symbol} on the Last Trading Day:**
            {last_day_summary}

            Remember, your analysis should be detailed, insightful, and actionable for traders seeking to capitalize on market movements.
        """
        
        try:
            return llm_text_gen(prompt)
        except Exception as err:
            logger.error(f"Failed to generate TA report: {err}")
            raise
    
    def _generate_options_report(self, results_sentences: List[str], ticker: str) -> str:
        """Generate options analysis report using LLM."""
        prompt = f"""
            You are a financial expert specializing in options trading and market sentiment analysis. 
            You have been provided with the following technical analysis of options data for the ticker symbol {ticker} with the nearest expiry date:

            {chr(10).join(results_sentences)}

            Based on this data, provide a comprehensive analysis of the options market for {ticker}.

            Your analysis should include:

            1. **Implied Volatility Interpretation:** Discuss the significance of the average implied volatility for both call and put options. What does it suggest about market expectations of future price movements?
            2. **Volume and Open Interest Insights:** Analyze the volume and open interest for call and put options. What does this data reveal about current market positioning and potential future trading activity?
            3. **Sentiment Analysis:** Evaluate the put-call ratio, implied volatility skew, and overall market sentiment. What do these indicators suggest about trader sentiment and potential future price direction?
            4. **Potential Trading Strategies:** Based on your analysis, suggest potential options trading strategies that could be employed for {ticker}, considering the current market conditions and sentiment.

            Please provide your analysis in a clear and concise manner, suitable for someone with a good understanding of options trading.
        """
        
        try:
            return llm_text_gen(prompt)
        except Exception as err:
            logger.error(f"Failed to generate options report: {err}")
            raise

def get_dashboard() -> FinancialDashboard:
    """Get the financial dashboard instance."""
    return FinancialDashboard() 