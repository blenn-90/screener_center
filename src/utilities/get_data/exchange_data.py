import time as tm
from datetime import time, datetime, timedelta
from kucoin.client import Client
import sys
import pandas as pd
from os import listdir
from os.path import isfile, join
from pathlib import Path

def job():
    #kucoin apikeys to request data from kucoin api
    kc_apikey = '65783ae7208b020001e209f0'
    kc_secret = 'a5caeddb-e8d5-40cc-b4d9-68c9f27160bd'
    kc_passphrase = 'fF1GYDzRwGPKupHz'
    print("start update")
    client = Client(kc_apikey, kc_secret, kc_passphrase)
    usdt_tickers = get_pairs()
    for pair in usdt_tickers:
        interval = '4hour'

        timeframe = "kucoin_4h"
        path = "/home/blenn/mysite/screener_center/data"
        data = read_csv_data(path, timeframe, pair+".csv")
        final_hist_df = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low'])
        final_hist_df.set_index("Date", inplace=True)
        numeric_columns = ['Open', 'Close', 'High', 'Low']
        final_hist_df[numeric_columns] = final_hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
        # ts stores the time in seconds
        ts = tm.time()
        if not data.empty:
            last_data= datetime.timestamp(data.index[-1]) + 14400
        else:
            last_data = ts - 17280000

        historical = client.get_kline_data( pair, kline_type=interval, start=int(last_data) + 14400, end=int(ts))
        if not historical:
            print("no historical")
        else:
            hist_df = pd.DataFrame(historical)
            hist_df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Amount', 'Volume']
            hist_df['Date'] = pd.to_datetime(hist_df['Date'], unit='s')
            hist_df['Date']=hist_df['Date'].dt.round('15min')
            hist_df.set_index("Date", inplace=True)
            hist_df = hist_df.drop(columns=['Amount','Volume'])
            numeric_columns = ['Open', 'Close', 'High', 'Low']
            hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)
            #hist_df['Date'] = hist_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            final_hist_df = (final_hist_df.copy() if hist_df.empty else hist_df.copy() if final_hist_df.empty else pd.concat([final_hist_df, hist_df])) # if both DataFrames non empty)
        final_hist_df.sort_values(by='Date', inplace = True)

        if not data.empty:
            temp_df = pd.concat([data, final_hist_df])
            temp_df.to_csv(path + "/kucoin_4h/"+pair+".csv")
        else:
            final_hist_df.to_csv(path + "/kucoin_4h/"+pair+".csv")

def get_pairs():
    #kucoin apikeys to request data from kucoin api
    kc_apikey = '65783ae7208b020001e209f0'
    kc_secret = 'a5caeddb-e8d5-40cc-b4d9-68c9f27160bd'
    kc_passphrase = 'fF1GYDzRwGPKupHz'
    client = Client(kc_apikey, kc_secret, kc_passphrase)
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


job()