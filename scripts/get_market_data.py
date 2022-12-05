from decouple import config
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import datetime
import json
import requests

COIN_API_KEY = config('COIN_API_KEY')

BASE_URL_COINAPI = "https://rest.coinapi.io/v1"

START_TIME = 1640995200 # January 1, 2022 in Unix time (seconds)
PERIOD = 2592000 # 30 days in seconds
NUM_PERIODS = 5

def queryMarketData(symbol, period_begin_time, period_end_time):
    period_begin_time = datetime.datetime.utcfromtimestamp(period_begin_time).isoformat()
    period_end_time = datetime.datetime.utcfromtimestamp(period_end_time).isoformat()

    response = requests.get(f"{BASE_URL_COINAPI}/ohlcv/{symbol}/history", params = {
        "period_id": "1DAY",
        "time_start": period_begin_time,
        "time_end": period_end_time,
        "apiKey": COIN_API_KEY
    })
    response = response.json()

    price_sum = 0
    volume_sum = 0
    for period_data in response:
        price_sum += float(period_data["price_open"])
        volume_sum += float(period_data["volume_traded"])
    price_average = price_sum / len(response)
    volume_average = volume_sum / len(response)

    return price_average, volume_average

print("Beginning market data queries...")

daos_to_query = ["HOP", "RAI", "RARI", "COMP", "UDT", "SILO", "T", "RAD", "CTX", "TRU", "ANGLE", "OUSD"]

for dao in daos_to_query:
    try:
        average_prices = []
        average_volumes = []
        for j in range(NUM_PERIODS):
            period_begin_time = START_TIME + j * PERIOD
            period_end_time = START_TIME + (j + 1) * PERIOD - 1

            price_average, volume_average = queryMarketData(f"COINBASE_SPOT_{dao}_USD", period_begin_time, period_end_time)
            average_prices.append(price_average)
            average_volumes.append(volume_average)
        print(f"Successfully retrieved market data for {dao} token")
        print(average_prices)
        print(average_volumes)
    except:
        print(f"Market data does not exist on Coinbase for {dao} token")
        continue
