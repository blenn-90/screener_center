import time as tm
from datetime import time, datetime, timedelta
import src.utilities.noshare_static_data as noshare_static_data
import src.utilities.get_data.kucoin_data as kucoin_data
from kucoin.client import Client
import sys
import pandas as pd
import requests

#function used to restart the webapp process
def reload():
    print("---PYTHON ANYWHERE APP RELOAD | START---")
    #api access data
    username = "blenn"
    api_token = "b6f5dc7ab892b97f869b03f63af6717ea060a7b1"
    domain_name = "blenn.pythonanywhere.com"
    #url to reload the webapp
    response = requests.post(
        'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
            username=username, domain_name=domain_name
        ),
        headers={'Authorization': 'Token {token}'.format(token=api_token)}
    )
    #response
    if response.status_code == 200:
        print("---PYTHON ANYWHERE APP RELOAD | RELOADED DONE---")
    else:
        print("---PYTHON ANYWHERE APP RELOAD | Got unexpected status code {}: {!r}".format(response.status_code, response.content) )

#function used to update pair data from kucoin
def job():
    print("---KUCOIN DATA UPDATE | START---")
    #get all pairs tickers
    usdt_tickers = kucoin_data.get_pairs()
    #iterating every pair ticker
    for pair in usdt_tickers:
        #create a connection to kucoin api
        client = Client(noshare_static_data.kc_apikey, noshare_static_data.kc_secret, noshare_static_data.kc_passphrase)
        #path to data folder
        interval = '4hour'
        timeframe = "kucoin_4h"
        path = sys.path[noshare_static_data.project_sys_path_position] + "\\data"
        #get the pair data
        data = kucoin_data.read_csv_data(path, timeframe, pair+".csv")

        #create finals var
        final_hist_df = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low'])
        final_hist_df.set_index("Date", inplace=True)
        numeric_columns = ['Open', 'Close', 'High', 'Low']
        final_hist_df[numeric_columns] = final_hist_df[numeric_columns].apply(pd.to_numeric, axis=1)

        #getting all the data following my last update
        ts = tm.time()
        if not data.empty:
            #adding few minutes to the last update to get from the next candle
            last_data= datetime.timestamp(data.index[-1]) + 14400
        else:
            #get last 6 months of data if there are no data
            last_data = ts - 17280000
        #get data
        historical = client.get_kline_data( pair, kline_type=interval, start=int(last_data) + 14400, end=int(ts))

        if not historical:
            print("---KUCOIN DATA UPDATE |" + pair + " no data between " +  str(datetime.fromtimestamp(last_data)) +" and " + str(datetime.fromtimestamp(ts)) + " ---")
        else:
            print("---KUCOIN DATA UPDATE |" + pair + " found data between " +  str(datetime.fromtimestamp(last_data)) +" and " + str(datetime.fromtimestamp(ts)) + " ---")
            
            #saving data
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
        #merging data is file already exist
        if not data.empty:
            temp_df = pd.concat([data, final_hist_df])
            temp_df.to_csv(sys.path[noshare_static_data.project_sys_path_position]+ "\\data\\kucoin_4h\\"+pair+".csv")
        #creating new file
        else:
            final_hist_df.to_csv(sys.path[noshare_static_data.project_sys_path_position]+ "\\data\\kucoin_4h\\"+pair+".csv") 
