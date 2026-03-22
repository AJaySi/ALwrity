# Financial Reports Module

This directory contains the core report generation modules for different types of financial analysis. Each module is designed to handle a specific type of financial report and can be accessed through the main dashboard interface.

## Directory Structure

```
reports/
├── technical_analysis/     # Technical analysis reports
├── fundamental_analysis/   # Fundamental analysis reports
├── options_analysis/      # Options analysis reports
├── portfolio_analysis/    # Portfolio analysis reports
├── market_research/       # Market research reports
└── news_analysis/         # News analysis reports
```

## Report Types

### 1. Technical Analysis Reports
Location: `technical_analysis/`

Generates technical analysis reports including:
- Moving averages (SMA, EMA, WMA)
- RSI, MACD, Bollinger Bands
- Volume analysis
- Support/Resistance levels
- Trend analysis
- Pattern recognition

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.technical_analysis import generate_ta_report

report = generate_ta_report("AAPL")
```

### 2. Fundamental Analysis Reports
Location: `fundamental_analysis/`

Generates fundamental analysis reports including:
- Financial ratios
- Company valuation metrics
- Growth analysis
- Profitability analysis
- Debt analysis
- Cash flow analysis

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.fundamental_analysis import generate_fa_report

report = generate_fa_report("AAPL")
```

### 3. Options Analysis Reports
Location: `options_analysis/`

Generates options analysis reports including:
- Options chain analysis
- Implied volatility analysis
- Options strategies
- Risk metrics
- Greeks analysis

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.options_analysis import generate_options_report

report = generate_options_report("AAPL")
```

### 4. Portfolio Analysis Reports
Location: `portfolio_analysis/`

Generates portfolio analysis reports including:
- Portfolio performance analysis
- Risk assessment
- Asset allocation
- Correlation analysis
- Diversification metrics
- Performance attribution

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.portfolio_analysis import generate_portfolio_report

portfolio = [
    {"symbol": "AAPL", "shares": 100},
    {"symbol": "GOOGL", "shares": 50}
]
report = generate_portfolio_report(portfolio)
```

### 5. Market Research Reports
Location: `market_research/`

Generates market research reports including:
- Sector analysis
- Industry trends
- Market overview
- Competitive analysis
- Market opportunities
- Risk factors

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.market_research import generate_market_research_report

report = generate_market_research_report(sectors=["Technology", "Healthcare"])
```

### 6. News Analysis Reports
Location: `news_analysis/`

Generates news analysis reports including:
- News sentiment analysis
- Market impact analysis
- Event correlation
- Trend detection
- Social media analysis
- News aggregation

Usage:
```python
from lib.ai_writers.ai_finance_report_generator.reports.news_analysis import generate_news_analysis_report

report = generate_news_analysis_report("AAPL")
```

## Common Features

All report modules share the following features:

1. **Data Validation**
   - Input validation for symbols and parameters
   - Error handling for invalid inputs
   - Data type checking

2. **Report Formatting**
   - Markdown formatting
   - Chart generation (when applicable)
   - Customizable templates

3. **Storage Integration**
   - Automatic report storage
   - Recent reports tracking
   - Report versioning

4. **User Preferences**
   - Customizable report formats
   - Language selection
   - Chart style preferences

## Integration with Dashboard

All report modules are integrated with the main dashboard and can be accessed through the `FinancialDashboard` class:

```python
from lib.ai_writers.ai_finance_report_generator.ai_financial_dashboard import get_dashboard

dashboard = get_dashboard()

# Generate reports through dashboard
ta_report = dashboard.generate_technical_analysis("AAPL")
options_report = dashboard.generate_options_analysis("AAPL")

# Get recent reports
recent_reports = dashboard.get_recent_reports()
```

## Adding New Report Types

To add a new report type:

1. Create a new directory in the `reports/` folder
2. Create an `__init__.py` file with the report generation function
3. Add the report type to the dashboard features
4. Implement the report generation logic
5. Add appropriate error handling and validation

Example:
```python
# reports/new_analysis/__init__.py
from typing import Dict, Any
from ...utils import validate_symbol

def generate_new_analysis_report(symbol: str) -> Dict[str, Any]:
    """
    Generate a new type of analysis report.
    
    Args:
        symbol (str): Stock symbol to analyze
        
    Returns:
        Dict[str, Any]: Analysis report
    """
    if not validate_symbol(symbol):
        raise ValueError("Invalid symbol provided")
        
    # Implement report generation logic
    return {
        "symbol": symbol,
        "analysis": "Report content"
    }
```

## Error Handling

All report modules implement consistent error handling:

1. **Input Validation**
   - Symbol validation
   - Parameter validation
   - Data type checking

2. **Data Collection Errors**
   - API errors
   - Network errors
   - Data format errors

3. **Report Generation Errors**
   - LLM errors
   - Template errors
   - Formatting errors

4. **Storage Errors**
   - File system errors
   - Database errors
   - Backup errors

## Contributing

When contributing to the reports module:

1. Follow the existing code structure
2. Add appropriate type hints
3. Include comprehensive docstrings
4. Add error handling
5. Update the dashboard integration
6. Add tests for new functionality

## Dependencies

The reports module depends on:

1. **Data Collection**
   - `finance_data_researcher`
   - `web_scraping_tools`

2. **Analysis Tools**
   - `pandas_ta`
   - `numpy`
   - `scipy`

3. **Visualization**
   - `matplotlib`
   - `plotly`

4. **Text Generation**
   - `llm_text_gen`
   - `gpt_providers`

## License

This module is part of the AI Finance Report Generator project and is licensed under the MIT License. 