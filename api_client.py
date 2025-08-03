import requests
import time


class Trading212Client:
    def __init__(self, api_key: str, live: bool = True):
        self.api_key = api_key
        self.base_url = "https://live.trading212.com/api/v0"
        self.headers = {
            "Authorization": f"{self.api_key}",
        }

    
    def get_instrument_list(self):
        url = f"{self.base_url}/equity/metadata/instruments"

        max_retries = 5
        retry_delay = 20  # seconds

        for attempt in range(1, max_retries + 1):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                instruments = response.json()
                return instruments

            elif response.status_code == 429:
                print(f"Attempt {attempt}: Rate limited (429). Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)

            else:
                print(f"Failed to fetch instrument list, status code: {response.status_code}")
                return []

        print(f"Failed after {max_retries} attempts due to rate limiting.")
        return []

    def get_current_positions(self):
        url = f"{self.base_url}/equity/portfolio"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        return data
    
    def get_individual_paid_out_divedends(self, ticker: str):
        url = f"{self.base_url}/history/dividends"
        query = {
        "cursor": "0",
        "ticker": ticker,
        "limit": "50"
        }

        response = requests.get(url, headers=self.headers, params=query)
        if response.status_code != 200:
            print(f"Error fetching dividends: {response.status_code}")
            return
        
        data = response.json()
        return data