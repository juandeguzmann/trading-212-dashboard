import datetime
import pandas as pd
import requests
import streamlit as st
from api_client import Trading212Client
from dateutil import parser

from utils import transform_positions, format_dividends_for_display

API_BASE = "https://live.trading212.com/api/v0"

@st.cache_data(show_spinner=True)
def get_all_dividends(_client):
    return _client.get_dividends()

def show_dashboard(instrument_list):
    df = transform_positions(st.session_state["positions"], instrument_list)
    st.subheader("Portfolio Positions")
    st.dataframe(df, use_container_width=True)

def show_dividends(client, instrument_list):
    st.markdown("### Total Dividends each Month (£)")
    dividends = get_all_dividends(client)
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

def show_individual_stock_info(client, instrument_list):
    instrument_options = {inst['name'] : inst['ticker'] for inst in instrument_list}
    selected_ticker = st.selectbox("Select Instrument", options=list(instrument_options.keys()))
    selected_instrument = instrument_options[selected_ticker]

    history = client.get_historical_order_data(selected_instrument)
    st.write(selected_instrument)
    if history is None:
        st.error("Failed to fetch dividend history for the selected instrument.")
        return
    st.subheader(f"Dividend History for {selected_ticker}")
    st.write(history)

    dividends = client.get_individual_paid_out_dividends(selected_instrument)
    if dividends is not None and 'items' in dividends:
        st.subheader(f"Paid Dividends for {selected_ticker}")
        list_amount = [order['amount'] for order in dividends['items']]
        total_dividends = sum(list_amount)
        st.write(total_dividends)

        st.markdown("#### Dividends by Month")
        df_div = pd.DataFrame(dividends['items'])
        df_div['paidOn'] = pd.to_datetime(df_div['paidOn'], utc=True, errors='coerce')
        df_div['month'] = df_div['paidOn'].dt.to_period('M').astype(str)
        monthly = df_div.groupby('month')['amount'].sum().reset_index()
        monthly = monthly.sort_values('month')
        monthly = monthly.set_index('month')
        st.bar_chart(monthly)
    else:
        st.info("No dividend data available for this instrument.")

def main():
    st.title("Trading 212 Positions Dashboard")
    api_key = st.text_input("Enter your Trading 212 API Key", type="password")
    client = Trading212Client(api_key)

    # Only fetch once per session
    if api_key and ("instrument_list" not in st.session_state) and ("positions" not in st.session_state):
        all_instruments = client.get_instrument_list()
        positions = client.get_current_positions()
        position_tickers = {pos['ticker'] for pos in positions}
        instrument_list = [inst for inst in all_instruments if inst['ticker'] in position_tickers]
        st.session_state["instrument_list"] = instrument_list
        st.session_state["positions"] = positions

    if "instrument_list" in st.session_state:
        instrument_list = st.session_state["instrument_list"]
        tab_1, tab_2, tab_3= st.tabs(["Dashboard", "Dividends", "Individual Stock Info"])
        with tab_1:
            show_dashboard(instrument_list)
        with tab_2:
            show_dividends(client, instrument_list)
        with tab_3:
            show_individual_stock_info(client, instrument_list)

if __name__ == "__main__":
    main()
#     import requests

#     def get_fx_rate_frankfurter(date_str, base="USD", target="GBP"):
#         url = f"https://api.frankfurter.app/{date_str}"
#         params = {"from": base, "to": target}
#         r = requests.get(url, params=params)
#         data = r.json()
#         return data["rates"][target]

#     # Example order data
#     filled_quantity = -4.02944691
#     fill_price = 209.87
#     taxes = [{"fillId": "36803571758", "name": "CURRENCY_CONVERSION_FEE", "quantity": -0.95, "timeCharged": "2025-08-06T13:45:04.699Z"}]
#     order_date = "2025-08-06"

#     # Calculate total order value in USD
#     tax_total = sum(t["quantity"] for t in taxes)
#     total_order_value_usd = filled_quantity * fill_price + tax_total

#     # Get USD to GBP rate for the order date
#     usd_to_gbp = get_fx_rate_frankfurter(order_date, base="USD", target="GBP")

#     # Convert to GBP
#     total_order_value_gbp = total_order_value_usd * usd_to_gbp

#     print(f"Total order value in USD: {total_order_value_usd:.2f}")
#     print(f"USD to GBP rate on {order_date}: {usd_to_gbp}")
#     print(f"Total order value in GBP: {total_order_value_gbp:.2f}")