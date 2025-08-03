import requests
import streamlit as st
from api_client import Trading212Client

from utils import transform_positions, format_dividends_for_display

API_BASE = "https://live.trading212.com/api/v0"

# Usage in Streamlit

def main():
    st.title("Trading 212 Positions Dashboard")

    api_key = st.text_input("Enter your Trading 212 API Key", type="password")

    if api_key:
        client = Trading212Client(api_key)
        
        dividends = client.get_individual_paid_out_divedends("VUSAl_EQ")
        print(f"dividends: {dividends}")  # Debugging line to check the response structure
        st.subheader("Paid Dividends for VUSAl_EQ")
        list_amount = [order['amount'] for order in dividends['items']]
        hello = sum(list_amount)
        st.write(hello)

        instrument_list = client.get_instrument_list()
        positions = client.get_current_positions()
        df = transform_positions(positions, instrument_list)
        st.subheader("Portfolio Positions")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()