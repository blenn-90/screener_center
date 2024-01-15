import src.indicator.i_atr as indicator_atr
import src.indicator.i_ema as indicator_ema
import src.screener.sources as sources
import src.utilities.sources as utlities_sources
import src.utilities.noshare_static_data as get_noshare_data 
import src.utilities.get_data.exchange_data as kucoin_data
import src.classes.position as position
import pandas as pd
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
            'price_distance': utlities_sources.fun_format_1decimal( (value.iloc[-1]['Close']-position.get_last_cross(value)[0]) / position.get_last_cross(value)[0] * 100),
            'last_update_at': str(value.iloc[-1]['Date']), 
            'ema_distance': utlities_sources.fun_format_1decimal((value.iloc[-1]['Fast-Ema'] - value.iloc[-1]['Slow-Ema']) / value.iloc[-1]['Slow-Ema'] * 100),
            'fast_ema': utlities_sources.fun_format_4decimal(value.iloc[-1]['Fast-Ema']),
            'slow_ema': utlities_sources.fun_format_4decimal(value.iloc[-1]['Slow-Ema']),
            'special_exit': utlities_sources.fun_format_4decimal(value.iloc[-1]['Slow-Ema'] * sources.special_exit)
            }
        
        positions.append(position_json)
    print("end reading positions")
    #get last update   
    return sorted(positions, key=lambda d: d['ema_cross_date'],reverse=True)

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
                    'typecolor': position.get_update_type_color(cross_type),
                    'value': utlities_sources.fun_format_4decimal(value.iloc[i]['Close']),
                    'date': str(value.iloc[i]['Date']), 
                    'fast_ema': utlities_sources.fun_format_4decimal(value.iloc[i]['Fast-Ema']),
                    'slow_ema': utlities_sources.fun_format_4decimal(value.iloc[i]['Slow-Ema']),
                    'atr': utlities_sources.fun_format_1decimal((value.iloc[i]['atr'] / value.iloc[i]['Close']) * 100),
                    'hardstop': utlities_sources.fun_format_4decimal(value.iloc[i]['Close'] - (value.iloc[i]['atr'] * 4)) 
                }   
                updates.append(update_json)
               
            i = i - 1
    print("end reading positions")
    return sorted(updates, key=lambda d: d['date'],reverse=True) 
        

def get_dashboard_data(final_dataset, positions):
    print("start reading dashboard")
    #get updates
    
    counter_bullish_pair_1_week_ago = 0
    counter_bullish_pair_2_week_ago = 0
    counter_bullish_pair_3_week_ago = 0
    counter_bullish_pair_4_week_ago = 0
    counter_bullish_pair_5_week_ago = 0
    counter_bullish_pair_6_week_ago = 0

    sum_ema_distance = 0
    sum_ema_distance_1_week_ago = 0
    sum_ema_distance_2_week_ago = 0
    sum_ema_distance_3_week_ago = 0
    sum_ema_distance_4_week_ago = 0
    sum_ema_distance_5_week_ago = 0
    sum_ema_distance_6_week_ago = 0

    for key, value in final_dataset.items():
        status_1_week_ago = position.get_status_by_day(value, -8)
        status_2_week_ago = position.get_status_by_day(value, -15)
        status_3_week_ago = position.get_status_by_day(value, -22)
        status_4_week_ago = position.get_status_by_day(value, -29)
        status_5_week_ago = position.get_status_by_day(value, -36)
        status_6_week_ago = position.get_status_by_day(value, -43)

        if status_1_week_ago == 1:
            counter_bullish_pair_1_week_ago = counter_bullish_pair_1_week_ago + 1 
        
        if status_2_week_ago == 1:
            counter_bullish_pair_2_week_ago = counter_bullish_pair_2_week_ago + 1 
        
        if status_3_week_ago == 1:
            counter_bullish_pair_3_week_ago = counter_bullish_pair_3_week_ago + 1

        if status_4_week_ago == 1:
            counter_bullish_pair_4_week_ago = counter_bullish_pair_4_week_ago + 1 
        
        if status_5_week_ago == 1:
            counter_bullish_pair_5_week_ago = counter_bullish_pair_5_week_ago + 1

        if status_6_week_ago == 1:
            counter_bullish_pair_6_week_ago = counter_bullish_pair_6_week_ago + 1 

        if not pd.isna(value.iloc[-1]['Slow-Ema']):
            ema_distance = (value.iloc[-1]['Fast-Ema'] - value.iloc[-1]['Slow-Ema']) / value.iloc[-1]['Slow-Ema'] * 100
            sum_ema_distance = sum_ema_distance + ema_distance
        if not pd.isna(value.iloc[-8]['Slow-Ema']):
            ema_distance_1_week_ago = (value.iloc[-8]['Fast-Ema'] - value.iloc[-8]['Slow-Ema']) / value.iloc[-8]['Slow-Ema'] * 100
            sum_ema_distance_1_week_ago = sum_ema_distance_1_week_ago + ema_distance_1_week_ago
        if not pd.isna(value.iloc[-15]['Slow-Ema']):
            ema_distance_2_week_ago = (value.iloc[-15]['Fast-Ema'] - value.iloc[-15]['Slow-Ema']) / value.iloc[-15]['Slow-Ema'] * 100
            sum_ema_distance_2_week_ago = sum_ema_distance_2_week_ago + ema_distance_2_week_ago
        if not pd.isna(value.iloc[-22]['Slow-Ema']):
            ema_distance_3_week_ago = (value.iloc[-22]['Fast-Ema'] - value.iloc[-22]['Slow-Ema']) / value.iloc[-22]['Slow-Ema'] * 100
            sum_ema_distance_3_week_ago = sum_ema_distance_3_week_ago + ema_distance_3_week_ago
        if not pd.isna(value.iloc[-29]['Slow-Ema']):
            ema_distance_4_week_ago = (value.iloc[-29]['Fast-Ema'] - value.iloc[-29]['Slow-Ema']) / value.iloc[-29]['Slow-Ema'] * 100
            sum_ema_distance_4_week_ago = sum_ema_distance_4_week_ago + ema_distance_4_week_ago
        if not pd.isna(value.iloc[-36]['Slow-Ema']):
            ema_distance_5_week_ago = (value.iloc[-36]['Fast-Ema'] - value.iloc[-36]['Slow-Ema']) / value.iloc[-36]['Slow-Ema'] * 100
            sum_ema_distance_5_week_ago = sum_ema_distance_5_week_ago + ema_distance_5_week_ago
        if not pd.isna(value.iloc[-43]['Slow-Ema']):
            ema_distance_6_week_ago = (value.iloc[-43]['Fast-Ema'] - value.iloc[-43]['Slow-Ema']) / value.iloc[-43]['Slow-Ema'] * 100
            sum_ema_distance_6_week_ago = sum_ema_distance_6_week_ago + ema_distance_6_week_ago

    avg_ema_distance  = sum_ema_distance/len(final_dataset)
    avg_ema_distance_1_week_ago = sum_ema_distance_1_week_ago / len(final_dataset)
    avg_ema_distance_2_week_ago = sum_ema_distance_2_week_ago / len(final_dataset)
    avg_ema_distance_3_week_ago = sum_ema_distance_3_week_ago / len(final_dataset)
    avg_ema_distance_4_week_ago = sum_ema_distance_4_week_ago / len(final_dataset)
    avg_ema_distance_5_week_ago = sum_ema_distance_5_week_ago / len(final_dataset)
    avg_ema_distance_6_week_ago = sum_ema_distance_6_week_ago / len(final_dataset)

    counter_bullish_pair = len(positions)
    counter_total_pair = len(final_dataset)

    dashboard_json = {'avg_ema_distance':utlities_sources.fun_format_2decimal(avg_ema_distance), 
                      'counter_bullish_pair': counter_bullish_pair, 
                      'counter_total_pair':counter_total_pair,
                      'list_bullish_pair_by_week': [counter_bullish_pair_6_week_ago, 
                                                    counter_bullish_pair_5_week_ago, 
                                                    counter_bullish_pair_4_week_ago, 
                                                    counter_bullish_pair_3_week_ago, 
                                                    counter_bullish_pair_2_week_ago, 
                                                    counter_bullish_pair_1_week_ago, 
                                                    counter_bullish_pair
                                                    ],
                      'list_avg_ema_distance_by_week': [avg_ema_distance_6_week_ago, 
                                                    avg_ema_distance_5_week_ago, 
                                                    avg_ema_distance_4_week_ago, 
                                                    avg_ema_distance_3_week_ago, 
                                                    avg_ema_distance_2_week_ago, 
                                                    avg_ema_distance_1_week_ago,
                                                    avg_ema_distance
                                                    ]
                      }
    
    print("end reading dashboard")
    return dashboard_json