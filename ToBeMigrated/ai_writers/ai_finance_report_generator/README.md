# AI Finance Report Generator

An advanced AI-powered financial analysis and report generation system that combines data collection, technical analysis, visualization, and automated report generation.

## Project Structure

```
ai_finance_report_generator/
├── ai_financial_dashboard.py    # Main dashboard interface
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── storage.py              # Data persistence
├── reports/                     # Report generation modules
│   ├── technical_analysis/     # Technical analysis reports
│   ├── fundamental_analysis/   # Fundamental analysis reports
│   ├── options_analysis/      # Options analysis reports
│   ├── portfolio_analysis/    # Portfolio analysis reports
│   ├── market_research/       # Market research reports
│   └── news_analysis/         # News analysis reports
└── README.md                   # This file
```

## Features

### Current Features
- Unified dashboard interface for all financial analysis tools
- Technical Analysis report generation
- Options analysis report generation
- User preferences management
- Recent reports tracking
- Data persistence with JSON storage
- Financial data collection from various sources
- Integration with LLM for report generation

### Planned Features

#### 1. Data Collection Module
- Web scraping for financial news and data
- API integrations (Yahoo Finance, Alpha Vantage, Financial Modeling Prep)
- Real-time market data collection
- Historical data retrieval
- Company financial statements
- Market sentiment data
- Economic indicators
- Sector analysis data

#### 2. Technical Analysis Module
- Moving averages (SMA, EMA, WMA)
- RSI, MACD, Bollinger Bands
- Volume analysis
- Support/Resistance levels
- Trend analysis
- Pattern recognition
- Fibonacci retracements
- Momentum indicators

#### 3. Fundamental Analysis Module
- Financial ratios calculation
- Company valuation metrics
- Growth analysis
- Profitability analysis
- Debt analysis
- Cash flow analysis
- Industry comparison
- Peer analysis

#### 4. Data Visualization Module
- Candlestick charts
- Technical indicator overlays
- Volume charts
- Price action patterns
- Correlation matrices
- Heat maps
- Interactive charts
- Custom chart templates

#### 5. Report Generation Module
- Technical analysis reports
- Fundamental analysis reports
- Market research reports
- Investment recommendations
- Risk assessment reports
- Sector analysis reports
- News impact analysis
- Custom report templates

#### 6. News and Sentiment Analysis Module
- News aggregation
- Sentiment scoring
- Social media analysis
- Market sentiment indicators
- News impact analysis
- Event correlation
- Trend detection
- Sentiment visualization

#### 7. Portfolio Analysis Module
- Portfolio performance analysis
- Risk assessment
- Asset allocation
- Correlation analysis
- Diversification metrics
- Performance attribution
- Portfolio optimization
- Rebalancing suggestions

## Usage

### Basic Usage

```python
from lib.ai_writers.ai_finance_report_generator.ai_financial_dashboard import get_dashboard

# Get dashboard instance
dashboard = get_dashboard()

# Generate technical analysis report
ta_report = dashboard.generate_technical_analysis("AAPL")

# Generate options analysis report
options_report = dashboard.generate_options_analysis("AAPL")

# Get recent reports
recent_reports = dashboard.get_recent_reports()
```

### User Preferences

```python
# Update user preferences
dashboard.update_preferences({
    "report_format": "markdown",
    "include_charts": True,
    "chart_style": "dark",
    "language": "en"
})

# Get current preferences
preferences = dashboard.get_preferences()
```

### Portfolio Analysis

```python
# Create portfolio
portfolio = [
    {"symbol": "AAPL", "shares": 100},
    {"symbol": "GOOGL", "shares": 50}
]

# Generate portfolio report
portfolio_report = dashboard.generate_portfolio_analysis(portfolio)
```

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 