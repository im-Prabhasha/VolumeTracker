# Crypto Volume/Market Cap Analysis Tool

A Streamlit-based dashboard for analyzing cryptocurrency trading volumes relative to their market capitalization. This tool helps identify cryptocurrencies with unusual trading activity by comparing their 24-hour trading volume to market cap ratios.

## Features

- Real-time cryptocurrency data from CoinGecko API
- Volume to Market Cap ratio analysis
- Customizable filters for:
  - Minimum Volume/MCap Ratio
  - Minimum 24h Volume
  - Market Dominance
- Sortable data table with key metrics
- Auto-refresh functionality

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Data Sources

- Cryptocurrency data is fetched from the CoinGecko API
- Data is refreshed every 5 minutes automatically
- Manual refresh available via the refresh button

## Disclaimer

This tool is for informational purposes only. High volume relative to market cap might indicate unusual trading activity but should not be used as the sole factor for investment decisions.
