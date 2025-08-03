import datetime
import pandas as pd
import requests
import streamlit as st
from api_client import Trading212Client
from dateutil import parser

from utils import transform_positions, format_dividends_for_display

API_BASE = "https://live.trading212.com/api/v0"

def main():
    st.title("Trading 212 Positions Dashboard")

    api_key = st.text_input("Enter your Trading 212 API Key", type="password")

    if api_key and "positions" not in st.session_state:
        client = Trading212Client(api_key)
        positions = client.get_current_positions()
        all_instruments = client.get_instrument_list()
        # Get tickers from current positions
        position_tickers = {pos['ticker'] for pos in positions}
        # Filter instruments to only those in positions
        instrument_list = [inst for inst in all_instruments if inst['ticker'] in position_tickers]
        st.session_state["instrument_list"] = instrument_list
        st.session_state["positions"] = positions

    if "instrument_list" in st.session_state:
        instrument_list = st.session_state["instrument_list"]
        instrument_options = {inst['name'] + f" ({inst['ticker']})": inst['ticker'] for inst in instrument_list}
        selected_ticker = st.selectbox("Select Instrument", options=list(instrument_options.keys()))
        selected_instrument = instrument_options[selected_ticker]

        # Only fetch dividends for the selected instrument
        client = Trading212Client(api_key)
        dividends = client.get_individual_paid_out_dividends(selected_instrument)
        st.subheader(f"Paid Dividends for {selected_instrument}")
        list_amount = [order['amount'] for order in dividends['items']]
        total_dividends = sum(list_amount)
        st.write(total_dividends)

        # --- Dividends by Month Chart ---
        st.markdown("#### Dividends by Month")
        if dividends['items']:
            df_div = pd.DataFrame(dividends['items'])
            # Ensure paidOn is parsed as datetime, including timezone
            df_div['paidOn'] = pd.to_datetime(df_div['paidOn'], utc=True, errors='coerce')
            df_div['month'] = df_div['paidOn'].dt.to_period('M').astype(str)
            monthly = df_div.groupby('month')['amount'].sum().reset_index()
            monthly = monthly.sort_values('month')
            monthly = monthly.set_index('month')
            st.bar_chart(monthly)
        else:
            st.info("No dividend data available for this instrument.")

        # --- Total Dividends by Month (All Tickers) ---
        st.markdown("### Total Dividends by Month (All Tickers)")

        @st.cache_data(show_spinner=False)
        def get_all_dividends(api_key):
            client = Trading212Client(api_key)
            return client.get_dividends()

        dividends = get_all_dividends(api_key)

        if isinstance(dividends, dict) and 'items' in dividends:
            data = dividends['items']
        else:
            data = dividends

        df = pd.DataFrame(data)

        def parse_paid_on(date_str):
            try:
                return parser.parse(date_str)
            except Exception:
                return pd.NaT

        if not df.empty and 'paidOn' in df.columns and 'amount' in df.columns:
            df['paidOn'] = df['paidOn'].apply(parse_paid_on)
            df['month'] = df['paidOn'].apply(lambda x: x.strftime('%Y-%m') if pd.notnull(x) else None)
            monthly_dividends = df.groupby('month')['amount'].sum().reset_index()
            monthly_dividends['month'] = pd.to_datetime(monthly_dividends['month'])
            monthly_dividends = monthly_dividends.set_index('month')
            st.bar_chart(monthly_dividends)
        else:
            st.info("No dividend data available for your account.")

        # Show positions only once, not on every instrument change
        df = transform_positions(st.session_state["positions"], instrument_list)
        st.subheader("Portfolio Positions")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()