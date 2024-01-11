import schedule
import time as tm
from datetime import time, datetime, timedelta
import src.utilities.noshare_static_data as noshare_static_data
import src.utilities.get_data.kucoin_data as kucoin_data

from kucoin.client import Client
import sys
import pandas as pd

def job():
    print("start update")
    usdt_tickers = kucoin_data.get_pairs()
    for pair in usdt_tickers:
        client = Client(noshare_static_data.kc_apikey, noshare_static_data.kc_secret, noshare_static_data.kc_passphrase)
        interval = '4hour'

        timeframe = "kucoin_4h"
        print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
        path = sys.path[noshare_static_data.project_sys_path_position] + "\\data"
        data = kucoin_data.read_csv_data(path, timeframe, pair+".csv")
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
            print(pair + " no data between " +  str(datetime.fromtimestamp(last_data)) +" and " + str(datetime.fromtimestamp(ts)))
        else:
            print(pair + " found data between " +  str(datetime.fromtimestamp(last_data)) +" and " + str(datetime.fromtimestamp(ts)))
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
            temp_df.to_csv(sys.path[noshare_static_data.project_sys_path_position]+ "\\data\\kucoin_4h\\"+pair+".csv")
        else:
            final_hist_df.to_csv(sys.path[noshare_static_data.project_sys_path_position]+ "\\data\\kucoin_4h\\"+pair+".csv") 

job()