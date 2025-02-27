import streamlit as st
import pandas as pd
from datetime import datetime
from utils.coingecko_api import CoinGeckoAPI
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Crypto Volume/MCap Analysis",
    page_icon="📊",
    layout="wide"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    return CoinGeckoAPI()

# Data fetching function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data() -> Optional[pd.DataFrame]:
    """Fetch data for cryptocurrencies"""
    api_client = get_api_client()

    with st.spinner("Loading cryptocurrency data..."):
        data = api_client.get_market_data(page=1)  # Start with one page
        if not data:
            return None

        try:
            df = pd.DataFrame(data)

            # Calculate total market cap for dominance calculation
            total_market_cap = df['market_cap'].sum()
            if total_market_cap > 0:
                # Calculate metrics
                df['volume_market_cap_ratio'] = (df['total_volume'].fillna(0) / df['market_cap'].fillna(1) * 100).round(2)
                df['market_dominance'] = (df['market_cap'].fillna(0) / total_market_cap * 100).round(2)
            else:
                df['volume_market_cap_ratio'] = 0
                df['market_dominance'] = 0

            df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Ensure numeric columns
            numeric_columns = [
                'volume_change_percentage_24h',
                'volume_change_percentage_1h',
                'volume_change_percentage_5m',
                'price_change_percentage_24h',
                'volume_market_cap_ratio',
                'market_dominance'
            ]

            # Convert columns to numeric with better error handling
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

            return df

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return None

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

        # Pin BTC, ETH, and BTC.D at the top
        st.markdown("### 📊 Key Assets Overview")

        # Filter for BTC and ETH
        btc_data = df[df['symbol'] == 'BTC'].iloc[0] if not df[df['symbol'] == 'BTC'].empty else None
        eth_data = df[df['symbol'] == 'ETH'].iloc[0] if not df[df['symbol'] == 'ETH'].empty else None

        # Create three columns for BTC, ETH, and BTC.D
        key_col1, key_col2, key_col3 = st.columns(3)

        with key_col1:
            st.markdown("#### Bitcoin (BTC)")
            if btc_data is not None:
                st.metric(
                    "Price",
                    f"${btc_data['current_price']:,.2f}",
                    f"{btc_data['price_change_percentage_24h']:+.2f}%"
                )
                st.metric(
                    "Volume/MCap Ratio",
                    f"{btc_data['volume_market_cap_ratio']:.2f}%",
                    f"{btc_data['volume_change_percentage_24h']:+.2f}%"
                )
                st.metric(
                    "Market Dominance",
                    f"{btc_data['market_dominance']:.2f}%"
                )

        with key_col2:
            st.markdown("#### Ethereum (ETH)")
            if eth_data is not None:
                st.metric(
                    "Price",
                    f"${eth_data['current_price']:,.2f}",
                    f"{eth_data['price_change_percentage_24h']:+.2f}%"
                )
                st.metric(
                    "Volume/MCap Ratio",
                    f"{eth_data['volume_market_cap_ratio']:.2f}%",
                    f"{eth_data['volume_change_percentage_24h']:+.2f}%"
                )
                st.metric(
                    "Market Dominance",
                    f"{eth_data['market_dominance']:.2f}%"
                )

        with key_col3:
            st.markdown("#### Market Overview")
            # Calculate total market cap excluding stablecoins
            total_mcap = df['market_cap'].sum()
            btc_dominance = btc_data['market_dominance'] if btc_data is not None else 0
            st.metric(
                "Total Market Cap",
                f"${total_mcap:,.0f}",
                None
            )
            st.metric(
                "BTC.D",
                f"{btc_dominance:.2f}%",
                None
            )
            st.metric(
                "Avg Vol/MCap Ratio",
                f"{df['volume_market_cap_ratio'].mean():.2f}%",
                None
            )

        # Add separator
        st.markdown("---")

        # Key metrics
        st.markdown("### 📊 Market Overview")
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

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

        with metrics_col4:
            avg_vol_change = df['volume_change_percentage_5m'].mean()
            st.metric(
                "Avg 5m Vol Change",
                f"{avg_vol_change:+.2f}%",
                delta_color="normal"
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

            # Display columns
            display_cols = [
                'name', 'symbol', 'current_price', 'market_cap',
                'total_volume', 'volume_market_cap_ratio',
                'volume_change_percentage_5m', 'volume_change_percentage_1h', 'volume_change_percentage_24h',
                'market_dominance', 'price_change_percentage_24h'
            ]

            # Create display DataFrame with proper column names
            display_df = filtered_df[display_cols].copy()
            display_df.columns = [
                'Name', 'Symbol', 'Price (USD)', 'Market Cap (USD)',
                'Volume (24h)', 'Volume/MCap Ratio (%)',
                '5m Vol Change (%)', '1h Vol Change (%)', '24h Vol Change (%)',
                'Market Dominance (%)', '24h Price Change (%)'
            ]

            # Display the dataframe with proper formatting
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "Name": st.column_config.TextColumn(width="medium"),
                    "Symbol": st.column_config.TextColumn(width="small"),
                    "Price (USD)": st.column_config.NumberColumn(format="$%.4f"),
                    "Market Cap (USD)": st.column_config.NumberColumn(format="$%.0f"),
                    "Volume (24h)": st.column_config.NumberColumn(format="$%.0f"),
                    "Volume/MCap Ratio (%)": st.column_config.NumberColumn(format="%.2f%%"),
                    "5m Vol Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "1h Vol Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "24h Vol Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "Market Dominance (%)": st.column_config.NumberColumn(format="%.4f%%"),
                    "24h Price Change (%)": st.column_config.NumberColumn(format="%+.2f%%")
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
