import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from googlesearch import search
import time

def load_stock_symbols():
    """Load stock symbols from stocks.txt file"""
    try:
        with open('stocks.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        st.error("stocks.txt file not found. Please create it with one stock symbol per line.")
        return []

def get_stock_data(symbols, start_date, end_date):
    """Fetch stock data for given symbols and date range"""
    data = pd.DataFrame()
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            hist['Symbol'] = symbol
            data = pd.concat([data, hist])
        except Exception as e:
            st.warning(f"Error fetching data for {symbol}: {str(e)}")
    return data

def get_news_links(symbols):
    """Get top 10 news links for each selected stock"""
    news_data = []
    for symbol in symbols:
        query = f"{symbol} stock news {datetime.now().strftime('%Y-%m-%d')}"
        try:
            # Add delay to respect Google's rate limits
            time.sleep(2)
            links = list(search(query, num_results=10))
            for link in links:
                news_data.append({'Stock': symbol, 'News Link': link})
        except Exception as e:
            st.warning(f"Error fetching news for {symbol}: {str(e)}")
    return pd.DataFrame(news_data)

def main():
    st.title("Stock Analysis Dashboard")
    
    # Load stock symbols
    stock_symbols = load_stock_symbols()
    if not stock_symbols:
        return
    
    # Date range for stock data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=360)  # Fetch full year of data
    default_view_start = end_date - timedelta(days=30)  # Default view shows last month
    
    # Stock selection
    selected_stocks = st.multiselect(
        "Select stocks to analyze",
        options=stock_symbols,
        default=[stock_symbols[0]]
    )
    
    if selected_stocks:
        # Fetch and display stock data
        stock_data = get_stock_data(selected_stocks, start_date, end_date)
        
        if not stock_data.empty:
            # Create interactive plot with default range
            fig = px.line(
                stock_data.reset_index(),
                x='Date',
                y='Close',
                color='Symbol',
                title='Stock Price History',
                labels={'Close': 'Closing Price ($)'}
            )
            
            # Set default date range for display
            fig.update_layout(
                xaxis_range=[default_view_start, end_date],
                xaxis_title="Date",
                yaxis_title="Closing Price ($)",
                hovermode='x unified'
            )
            
            # Add range slider to allow viewing full date range
            fig.update_xaxes(rangeslider_visible=True)
            
            st.plotly_chart(fig)
            
            # Fetch and display news
            st.subheader("Latest News")
            with st.spinner('Fetching news articles...'):
                news_df = get_news_links(selected_stocks)
                if not news_df.empty:
                    st.dataframe(
                        news_df,
                        column_config={
                            "News Link": st.column_config.LinkColumn()
                        }
                    )
                else:
                    st.warning("No news articles found.")
        else:
            st.warning("No stock data available for the selected symbols.")

if __name__ == "__main__":
    main()