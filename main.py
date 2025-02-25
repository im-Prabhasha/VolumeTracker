import streamlit as st
import pandas as pd
from datetime import datetime
from utils.coingecko_api import CoinGeckoAPI

# Page configuration
st.set_page_config(
    page_title="Crypto Volume/MCap Analysis",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize API client
@st.cache_resource
def get_api_client():
    return CoinGeckoAPI()

# Data fetching function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data():
    """Fetch data for cryptocurrencies"""
    api_client = get_api_client()

    with st.spinner("Loading cryptocurrency data..."):
        data = api_client.get_market_data(page=1)  # Start with one page
        if not data:
            return None

        df = pd.DataFrame(data)

        # Calculate total market cap for dominance calculation
        total_market_cap = df['market_cap'].sum()

        # Calculate metrics
        df['volume_market_cap_ratio'] = (df['total_volume'] / df['market_cap'] * 100).round(2)  # As percentage
        df['market_dominance'] = (df['market_cap'] / total_market_cap * 100).round(2)  # As percentage
        df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return df

# Main app
def main():
    st.title("🔍 Crypto Volume/Market Cap Analysis")
    st.subheader("Volume to Market Cap Ratio Analysis")

    # Add refresh button and last updated time
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()

    try:
        # Fetch data
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

        high_volume_count = len(df[df['volume_market_cap_ratio'] > 100])
        with metrics_col2:
            st.metric(
                "Volume > Market Cap",
                high_volume_count,
                f"{(high_volume_count/len(df)*100):.1f}% of total"
            )

        with metrics_col3:
            median_ratio = df['volume_market_cap_ratio'].median()
            st.metric(
                "Median Vol/MCap Ratio",
                f"{median_ratio:.1f}%"
            )

        # Show high volume coins by default
        show_high_volume = st.checkbox("Show only coins with Volume > Market Cap (>100%)", value=True)

        if show_high_volume:
            filtered_df = df[df['volume_market_cap_ratio'] > 100].copy()
        else:
            # Filtering options
            st.markdown("### 🔍 Custom Filters")
            col1, col2, col3 = st.columns(3)
            with col1:
                min_ratio = st.number_input("Minimum Volume/MCap Ratio (%)", 0.0, 1000.0, 0.0)
            with col2:
                min_volume = st.number_input("Minimum 24h Volume (USD)", 0.0, 1e12, 10000.0)
            with col3:
                min_dominance = st.number_input("Minimum Market Dominance (%)", 0.0, 100.0, 0.0)

            filtered_df = df[
                (df['volume_market_cap_ratio'] >= min_ratio) &
                (df['total_volume'] >= min_volume) &
                (df['market_dominance'] >= min_dominance)
            ].copy()

        # Data table
        st.markdown("### 📋 Detailed Analysis")
        if len(filtered_df) == 0:
            st.info("No coins match the selected criteria.")
        else:
            st.text(f"Showing {len(filtered_df)} coins matching the criteria")

            # Sort by volume/market cap ratio before formatting
            filtered_df = filtered_df.sort_values('volume_market_cap_ratio', ascending=False)

            # Display columns
            display_cols = [
                'name', 'symbol', 'current_price', 'market_cap',
                'total_volume', 'volume_market_cap_ratio', 'market_dominance',
                'price_change_percentage_24h'
            ]

            formatted_df = filtered_df[display_cols].copy()
            formatted_df.columns = [
                'Name', 'Symbol', 'Price (USD)', 'Market Cap (USD)',
                'Volume (24h)', 'Volume/MCap Ratio (%)', 'Market Dominance (%)',
                '24h Price Change (%)'
            ]

            # Format numeric columns while preserving original values for sorting
            formatted_df_display = formatted_df.copy()
            formatted_df_display['Price (USD)'] = formatted_df['Price (USD)'].map('${:,.4f}'.format)
            formatted_df_display['Market Cap (USD)'] = formatted_df['Market Cap (USD)'].map('${:,.0f}'.format)
            formatted_df_display['Volume (24h)'] = formatted_df['Volume (24h)'].map('${:,.0f}'.format)
            formatted_df_display['Volume/MCap Ratio (%)'] = formatted_df['Volume/MCap Ratio (%)'].map('{:.2f}%'.format)
            formatted_df_display['Market Dominance (%)'] = formatted_df['Market Dominance (%)'].map('{:.4f}%'.format)
            formatted_df_display['24h Price Change (%)'] = formatted_df['24h Price Change (%)'].map('{:+.2f}%'.format)

            st.dataframe(
                formatted_df,
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "Price (USD)": st.column_config.NumberColumn(format="$%.4f"),
                    "Market Cap (USD)": st.column_config.NumberColumn(format="$%.0f"),
                    "Volume (24h)": st.column_config.NumberColumn(format="$%.0f"),
                    "Volume/MCap Ratio (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "Market Dominance (%)": st.column_config.NumberColumn(format="%.4f%%"),
                    "24h Price Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                }
            )

        # Add disclaimer
        st.markdown("""
        ---
        **Disclaimer:** This tool is for informational purposes only. High volume relative to market cap
        might indicate unusual trading activity but should not be used as the sole factor for investment decisions.
        """)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try refreshing the page or try again later.")

if __name__ == "__main__":
    main()
