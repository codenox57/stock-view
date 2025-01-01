# Stock Analysis Dashboard

This Streamlit application provides real-time stock analysis and news monitoring capabilities. It allows users to track multiple stocks simultaneously, visualize their price history, and access relevant news articles with publication timestamps.

## Important Note
This application was primarily developed through interaction with Claude 3.5 Sonnet, an AI language model created by Anthropic. While the code is functional and follows best practices, users should be aware that it was generated through AI assistance and may benefit from additional testing and validation in production environments.

## Features

The application offers a comprehensive set of features for stock analysis:

- Real-time stock data visualization for multiple stocks
- Interactive price history charts with adjustable time windows
- Automated news aggregation for selected stocks
- Publication date tracking for news articles
- Customizable stock watchlist through configuration file

## Prerequisites

The application requires Python 3.8 or higher. All required Python packages can be installed using pip:

```bash
pip install streamlit yfinance plotly pandas googlesearch-python requests beautifulsoup4 pytz python-dateutil
```

## Configuration

Create a file named `stocks.txt` in the application directory. Add one stock symbol per line, for example:

```text
AAPL
GOOGL
MSFT
AMZN
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd stock-analysis-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create and populate your `stocks.txt` file with desired stock symbols.

## Usage

1. Start the application:
```bash
streamlit run streamlit_app.py
```

2. Access the dashboard through your web browser (typically http://localhost:8501).

3. Use the multi-select dropdown to choose which stocks to analyze.

4. The dashboard will display:
   - An interactive price chart for the selected stocks
   - Recent news articles related to the selected stocks
   - Publication timestamps for news articles where available

## Data Sources

- Stock data is retrieved from Yahoo Finance through the `yfinance` package
- News articles are sourced through Google Search
- Article timestamps are extracted from various metadata sources within each article

## Technical Details

The application implements several robust features for data handling:

- Timezone-aware datetime processing
- Comprehensive error handling for failed requests
- Multiple fallback methods for extracting article dates
- Rate limiting for API requests
- Efficient data caching through Streamlit

## Limitations

Please be aware of the following limitations:

- News article fetching is subject to rate limiting
- Not all news sources provide accurate publication dates
- Stock data may be delayed by market reporting times
- Google Search API has daily quota limits

## Troubleshooting

Common issues and solutions:

1. If stock data fails to load:
   - Verify your internet connection
   - Check that the stock symbols are valid
   - Ensure you have not exceeded API rate limits

2. If news articles are not displaying:
   - Check your internet connection
   - Verify you haven't exceeded Google Search API limits
   - Try reducing the number of selected stocks

3. If timestamps are missing:
   - This is normal for some news sources
   - Articles will still be displayed but may be sorted to the end of the list

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License

[Specify your license here]

## Acknowledgments

This application makes use of several open-source packages:
- Streamlit for the web interface
- YFinance for stock data
- Plotly for interactive visualizations
- BeautifulSoup4 for web scraping
- Pandas for data manipulation