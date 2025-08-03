import pandas as pd
import os
import json

def get_valid_ticker(raw_positions) -> list:
    valid_tickers = []
    for pos in raw_positions:
        valid_tickers.append(str(pos.get("ticker")))
    return valid_tickers
    

def transform_positions(raw_positions, instument_list):
    ticker_name_map = {instrument["ticker"]: instrument["name"] for instrument in instument_list}
    table = []

    for pos in raw_positions:
        ticker = str(pos.get("ticker"))
        table.append({
            "Name": ticker_name_map.get(ticker, "Unknown"),
            "ticker": ticker,
            "Quantity": round(pos.get("quantity", 0), 4),
            # "Avg Price": round(pos.get("averagePrice", 0), 2),
            # "Current Price": round(pos.get("currentPrice", 0), 2),
            "P&L (£)": round(pos.get("ppl", 0), 2)
        })

    return pd.DataFrame(table)

def format_dividends_for_display(dividends_response):
    items = dividends_response.get("items", [])
    
    table = []
    for item in items:
        # Parse and format date nicely, e.g. YYYY-MM-DD only
        paid_on = item.get("paidOn", "")
        paid_on_date = paid_on.split("T")[0] if "T" in paid_on else paid_on
        
        table.append({
            "Ticker": item.get("ticker"),
            "Quantity": round(item.get("quantity", 0), 4),
            "Amount (Paid)": round(item.get("amount", 0), 2),
            "Gross Amount/Share": round(item.get("grossAmountPerShare", 0), 6),
            "Amount (€)": round(item.get("amountInEuro", 0), 2),
            "Paid On": paid_on_date,
            "Type": item.get("type")
        })
    
    return pd.DataFrame(table)

