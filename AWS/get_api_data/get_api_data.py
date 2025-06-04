import datetime
import os
import requests


def get_api_data(event, context):
   api_key = os.getenv("BITCOIN_API")
   today = datetime.datetime.today().strftime('%Y-%m-%d')
   endpoint = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey="
   response = requests.get(f"{endpoint}{api_key}").json() ## requests.get() -function making HTTP requests, and dynamically inserting api key to url i nastepnie .json zmienia strukture json na python
   data = response["Time Series (Digital Currency Daily)"][today]  ## pulls data from today's date
   data["date"] = today
   print(data)
   return data