import src.indicator.i_atr as indicator_atr
import src.indicator.i_ema as indicator_ema
import src.screener.sources as sources
import src.utilities.sources as utlities_sources
import src.utilities.noshare_static_data as get_noshare_data 
import src.utilities.get_data.kucoin_data as kucoin_data
import src.classes.position as position
from os import listdir
from os.path import isfile, join
import sys

def get_data():
    # retrive all out_of_sample files
    timeframe = "kucoin_4h"
    print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
    path = sys.path[get_noshare_data.project_sys_path_position] + "\\data"
    data_file_set = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
   
    final_dataset = {}

    for data_file in data_file_set:
        data = kucoin_data.read_csv_data(path, timeframe, data_file)
        #running backtesting
        filter_data = data[ (data.index > "2023-07-01") & (data.index < "2024-02-01")]
        atr_df = indicator_atr.i_atr_v2(filter_data, sources.atr_length)
        ema_fast_df = indicator_ema.i_ema_fast_v2(filter_data, sources.fast_ema)
        ema_slow_df = indicator_ema.i_ema_slow_v2(filter_data, sources.slow_ema)

        if not atr_df.empty and not ema_fast_df.empty and not ema_slow_df.empty:
            temp_df = atr_df.merge(ema_fast_df, how='left', on='Date')
            temp2_df = temp_df.merge(filter_data, how='left', on='Date')
            final_df = temp2_df.merge(ema_slow_df, how='left', on='Date')
            
            final_dataset[data_file] = final_df
    
    print("dataset is ready")
    return final_dataset

#building data
def get_positions(final_dataset):
    print("start reading positions")
    #open positions
    positions = []
    for key, value in final_dataset.items():
        status = position.get_status(value)
        if status != 1:
            continue

        position_json = {'pair': key.split("-")[0], 
            'status': position.get_status_lable(status), 
            'ema_cross_price': utlities_sources.fun_format_4decimal(position.get_last_cross(value)[0]) ,
            'ema_cross_date': str(position.get_last_cross(value)[1]), 
            'current': utlities_sources.fun_format_4decimal(value.iloc[-1]['Close']),
            'last_update_at': str(value.iloc[-1]['Date']), 
            'ema_distance': utlities_sources.fun_format_2decimal((value.iloc[-1]['Fast-Ema'] - value.iloc[-1]['Slow-Ema']) / value.iloc[-1]['Slow-Ema'] * 100),
            'fast_ema': utlities_sources.fun_format_4decimal(value.iloc[-1]['Fast-Ema']),
            'slow_ema': utlities_sources.fun_format_4decimal(value.iloc[-1]['Slow-Ema']),
            'special_exit': utlities_sources.fun_format_4decimal(value.iloc[-1]['Slow-Ema'] * sources.special_exit)
            }
        
        positions.append(position_json)
    print("end reading positions")
    #get last update   
    return positions

def get_updates(final_dataset):
    print("start reading updates")
    #get updates
    updates = []
    for key, value in final_dataset.items():

        #analyze 1 week of data on any pair
        number_of_candle_4h_tba = -6*14
        i = -1
        while i > number_of_candle_4h_tba:
            cross_type = position.check_cross_by_candle(value, i)
            if cross_type != 0 :
                update_json = {
                    'pair': key.split("-")[0], 
                    'type': position.get_update_type(cross_type), 
                    'value': utlities_sources.fun_format_4decimal(value.iloc[i]['Close']),
                    'date': str(value.iloc[i]['Date']), 
                    'fast_ema': utlities_sources.fun_format_4decimal(value.iloc[i]['Fast-Ema']),
                    'slow_ema': utlities_sources.fun_format_4decimal(value.iloc[i]['Slow-Ema']),
                    'atr': utlities_sources.fun_format_4decimal(value.iloc[i]['atr'])}     
                updates.append(update_json)
               
            i = i - 1
    print("end reading positions")
    return sorted(updates, key=lambda d: d['date'],reverse=True) 
        

