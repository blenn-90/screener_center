import sys
import pandas as pd
import src.utilities.noshare_static_data as noshare_data
from kucoin.client import Client
import time
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path

def get_pairs():
    client = Client(noshare_data.kc_apikey, noshare_data.kc_secret, noshare_data.kc_passphrase)
    tickers = client.get_symbols()
    
    usdt_tickers = []
    for ticker in tickers:
        if 'USDT' in ticker['symbol'] and not ticker['symbol'].startswith('BUSD')  and not ticker['symbol'].startswith('ETHW') and not ticker['symbol'].startswith('AUSD') and not ticker['symbol'].startswith('USD') and '2L-USDT' not in ticker['symbol'] and '2S-USDT' not in ticker['symbol']and 'DOWN-USDT' not in ticker['symbol'] and '2DOWN-USDT' not in ticker['symbol'] and 'UP-USDT' not in ticker['symbol'] and '2UP-USDT' not in ticker['symbol'] and '3L-USDT' not in ticker['symbol'] and '3S-USDT' not in ticker['symbol']  and 'DOWN-USDT' not in ticker['symbol'] and 'UPUSDT' not in ticker['symbol'] and 'BEAR-USDT' not in ticker['symbol'] and 'BULL-USDT' not in ticker['symbol']  and not ticker['symbol'].startswith('TUSD') and not ticker['symbol'].startswith('EUR') and not ticker['symbol'].startswith('PAX'):
            usdt_tickers.append(ticker['symbol'])

    return usdt_tickers

def read_csv_data(path, timeframe, filename):
    final_path = path + "\\" + timeframe + "\\" + filename
    my_file = Path(final_path)
    if my_file.is_file():
 
        #reading csv file
        data = pd.read_csv(
            final_path,
            usecols=[0,1,2,3,4],
            names=["Date",'Open', 'Close', 'High', 'Low'],
            skiprows=[0]
        )
        #setting dataframe index
        data["Date"] = pd.to_datetime(data["Date"])
        data.set_index("Date", inplace=True)
        return data
    
    return pd.DataFrame()
