import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from googlesearch import search
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pytz
import re
from dateutil import parser
import json

def standardize_datetime(dt):
    """Standardize datetime objects to UTC timezone"""
    if pd.isnull(dt):
        return pd.NaT
    
    # Convert string to datetime if necessary
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except:
            return pd.NaT
    
    # Handle timezone-naive datetimes
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    else:
        # Convert to UTC
        dt = dt.astimezone(pytz.UTC)
    
    return dt

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

def extract_date_from_json_ld(soup):
    """Extract date from JSON-LD structured data"""
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    for script in script_tags:
        try:
            data = json.loads(script.string)
            # Handle both single objects and lists of objects
            if isinstance(data, list):
                data = data[0]
            
            # Check various date fields
            date_fields = [
                'dateModified',
                'datePublished',
                'dateCreated',
                'uploadDate'
            ]
            
            for field in date_fields:
                if field in data:
                    try:
                        return pd.to_datetime(data[field])
                    except:
                        continue
                        
        except:
            continue
    return None

def extract_date_from_meta_tags(soup):
    """Extract date from meta tags using multiple formats and properties"""
    meta_date_properties = [
        'article:modified_time',
        'article:published_time',
        'og:updated_time',
        'og:published_time',
        'lastmod',
        'pubdate',
        'date',
        'sailthru.date',
        'citation_publication_date',
        'dcterms.modified',
        'dcterms.created',
        'parsely-pub-date'
    ]
    
    for prop in meta_date_properties:
        # Check both property and name attributes
        meta_tag = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
        if meta_tag and meta_tag.get('content'):
            try:
                return pd.to_datetime(meta_tag['content'])
            except:
                continue
    return None

def extract_date_from_common_patterns(html_text):
    """Extract date using common patterns in HTML"""
    # Common date patterns in HTML
    patterns = [
        r'datetime="([^"]+)"',
        r'published-date="([^"]+)"',
        r'class="date[^"]*">([^<]+)',
        r'class="time[^"]*">([^<]+)',
        r'data-date="([^"]+)"',
        r'"datePublished":"([^"]+)"',
        r'"dateModified":"([^"]+)"',
        # Add patterns for common date formats
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_text)
        for match in matches:
            try:
                return pd.to_datetime(match)
            except:
                continue
    return None

def get_page_last_modified(url):
    """Enhanced function to fetch the last modified date of a webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Try HTTP headers first
        last_modified = response.headers.get('last-modified')
        if last_modified:
            try:
                return standardize_datetime(last_modified)
            except:
                pass
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple methods to find the date
        date = None
        
        # 1. Check JSON-LD structured data
        date = extract_date_from_json_ld(soup)
        if date:
            return standardize_datetime(date)
            
        # 2. Check meta tags
        date = extract_date_from_meta_tags(soup)
        if date:
            return standardize_datetime(date)
            
        # 3. Check common patterns in HTML
        date = extract_date_from_common_patterns(response.text)
        if date:
            return standardize_datetime(date)
            
        # 4. Try time tag
        time_tag = soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime') or time_tag.get('data-datetime')
            if datetime_attr:
                try:
                    return standardize_datetime(datetime_attr)
                except:
                    pass
        
        return None
        
    except Exception as e:
        print(f"Error fetching date for {url}: {str(e)}")
        return None

def get_news_links(symbols):
    """Get top 10 news links for each selected stock with their last modified dates"""
    news_data = []
    for symbol in symbols:
        query = f"{symbol} stock news {datetime.now().strftime('%Y-%m-%d')}"
        try:
            time.sleep(2)  # Respect rate limits
            links = list(search(query, num_results=10))
            
            for link in links:
                last_modified = get_page_last_modified(link)
                news_data.append({
                    'Stock': symbol,
                    'News Link': link,
                    'Last Updated': last_modified
                })
        except Exception as e:
            st.warning(f"Error fetching news for {symbol}: {str(e)}")
    
    df = pd.DataFrame(news_data)
    
    # Ensure all timestamps are in UTC
    df['Last Updated'] = df['Last Updated'].apply(lambda x: standardize_datetime(x) if pd.notnull(x) else pd.NaT)
    
    return df

def main():
    st.title("Stock Analysis Dashboard")
    
    # Load stock symbols
    stock_symbols = load_stock_symbols()
    if not stock_symbols:
        return
    
    # Date range for stock data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=360)
    default_view_start = end_date - timedelta(days=30)
    
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
            with st.spinner('Fetching news articles and their timestamps...'):
                news_df = get_news_links(selected_stocks)
                if not news_df.empty:
                    st.dataframe(
                        news_df.sort_values('Last Updated', ascending=False),  # Sort by most recent
                        column_config={
                            "News Link": st.column_config.LinkColumn(),
                            "Last Updated": st.column_config.DatetimeColumn(
                                "Last Updated",
                                format="DD/MM/YYYY HH:mm:ss",
                                help="Article publication or last modified date"
                            )
                        }
                    )
                    
                    # Add note about timestamp availability
                    st.caption("Note: Dates shown are based on article metadata where available.")
                else:
                    st.warning("No news articles found.")
        else:
            st.warning("No stock data available for the selected symbols.")

if __name__ == "__main__":
    main()