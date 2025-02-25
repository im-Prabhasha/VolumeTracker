import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
from utils.coingecko_api import CoinGeckoAPI

# Page configuration
st.set_page_config(
    page_title="Crypto Volume Analysis",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize API client
@st.cache_resource
def get_api_client():
    return CoinGeckoAPI()

# Data fetching function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data():
    api_client = get_api_client()
    data = api_client.get_market_data()
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df['volume_market_cap_ratio'] = df['total_volume'] / df['market_cap']
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return df

# Main app
def main():
    st.title("🔍 Crypto Volume Analysis")
    st.subheader("Identifying High Volume Cryptocurrencies")
    
    # Add refresh button and last updated time
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
    
    # Fetch data with loading state
    with st.spinner("Fetching latest cryptocurrency data..."):
        df = fetch_crypto_data()
    
    if df is None:
        st.error("⚠️ Failed to fetch data. Please try again later.")
        return
    
    with col2:
        st.text(f"Last updated: {df['timestamp'].iloc[0]}")
    
    # Key metrics
    st.markdown("### 📊 Market Overview")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            "Total Cryptocurrencies",
            len(df),
            "Analyzed"
        )
    
    with metrics_col2:
        volume_exceeding = len(df[df['volume_market_cap_ratio'] > 1])
        st.metric(
            "Volume > Market Cap",
            volume_exceeding,
            f"{(volume_exceeding/len(df)*100):.1f}% of total"
        )
    
    with metrics_col3:
        avg_ratio = df['volume_market_cap_ratio'].median()
        st.metric(
            "Median Volume/MCap Ratio",
            f"{avg_ratio:.2f}x"
        )
    
    # Filter for interesting cases
    high_volume_df = df[df['volume_market_cap_ratio'] > 1].copy()
    
    # Visualization
    st.markdown("### 📈 Volume to Market Cap Ratio Distribution")
    fig = px.scatter(
        high_volume_df,
        x='market_cap',
        y='total_volume',
        color='volume_market_cap_ratio',
        hover_name='name',
        log_x=True,
        log_y=True,
        color_continuous_scale='Viridis',
        title='Volume vs Market Cap (Filtered for Volume > MCap)'
    )
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("### 📋 Detailed Analysis")
    
    # Prepare display columns
    display_cols = [
        'name', 'symbol', 'current_price', 'market_cap',
        'total_volume', 'volume_market_cap_ratio', 'price_change_percentage_24h'
    ]
    
    formatted_df = high_volume_df[display_cols].copy()
    formatted_df.columns = [
        'Name', 'Symbol', 'Price (USD)', 'Market Cap (USD)',
        'Volume (24h)', 'Volume/MCap Ratio', '24h Change (%)'
    ]
    
    # Format numeric columns
    formatted_df['Price (USD)'] = formatted_df['Price (USD)'].map('${:,.2f}'.format)
    formatted_df['Market Cap (USD)'] = formatted_df['Market Cap (USD)'].map('${:,.0f}'.format)
    formatted_df['Volume (24h)'] = formatted_df['Volume (24h)'].map('${:,.0f}'.format)
    formatted_df['Volume/MCap Ratio'] = formatted_df['Volume/MCap Ratio'].map('{:.2f}x'.format)
    formatted_df['24h Change (%)'] = formatted_df['24h Change (%)'].map('{:+.2f}%'.format)
    
    st.dataframe(
        formatted_df,
        use_container_width=True,
        height=400
    )
    
    # Add disclaimer
    st.markdown("""
    ---
    **Disclaimer:** This tool is for informational purposes only. High volume relative to market cap
    might indicate unusual trading activity but should not be used as the sole factor for investment decisions.
    """)

if __name__ == "__main__":
    main()
