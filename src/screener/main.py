import src.indicator.i_atr as indicator_atr
import src.indicator.i_ema as indicator_ema
import src.utilities.static_data as static_data
import src.utilities.formatting as utlities_sources
import src.utilities.static_data_unsharable as static_data_unsharable 
import src.utilities.get_data.exchange_data as kucoin_data
import src.classes.position as position
import pandas as pd
from os import listdir
from os.path import isfile, join
import sys
from pathlib import Path
import math

#read all excel and calculate dataframes
def get_data():
    print("---CALCULATE DATA | START---")

    # retrive all out_of_sample files
    timeframe = "kucoin_4h"
    if static_data_unsharable.project_is_live==1: 
        path = static_data_unsharable.project_sys_path_live
    else: 
        path = sys.path[static_data_unsharable.project_sys_path_position] + static_data_unsharable.project_separator_path + "data"
    
    data_file_set = [f for f in listdir(path + static_data_unsharable.project_separator_path + timeframe) if isfile(join(path + static_data_unsharable.project_separator_path + timeframe, f))]
    final_dataset = {}
    #iterate every fille and add it to the final list of dataframes, calculating atr and emas
    for data_file in data_file_set:
        #retrive data for the current pair
        data = kucoin_data.read_csv_data(path, timeframe, data_file)
        #filter time range
        filter_data = data[ (data.index > "2023-07-01") & (data.index < "2024-02-01")]
        #calculate atr and emas
        atr_df = indicator_atr.i_atr_v2(filter_data, static_data.atr_length)
        ema_fast_df = indicator_ema.i_ema_fast_v2(filter_data, static_data.fast_ema)
        ema_slow_df = indicator_ema.i_ema_slow_v2(filter_data, static_data.slow_ema) 
        #merge all the data in 1 dataframe
        if not atr_df.empty and not ema_fast_df.empty and not ema_slow_df.empty:
            temp_df = atr_df.merge(ema_fast_df, how='left', on='Date')
            temp2_df = temp_df.merge(filter_data, how='left', on='Date')
            final_df = temp2_df.merge(ema_slow_df, how='left', on='Date')
            
            final_dataset[data_file] = final_df
    print("---CALCULATE DATA | END---")
    return final_dataset

#get all positions
def get_positions(final_dataset):
    print("---CALCULATE POSITIONS | START---")

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
            'special_exit': utlities_sources.fun_format_4decimal(value.iloc[-1]['Slow-Ema'] * static_data.special_exit)
            }
        
        positions.append(position_json)
    print("---CALCULATE POSITIONS | END---")
    #get last update   
    return sorted(positions, key=lambda d: d['ema_cross_date'],reverse=True)

def get_updates(final_dataset):
    print("---CALCULATE LAST UPDATES | START---")
    if static_data_unsharable.project_is_live==1: 
        path = static_data_unsharable.project_sys_path_live
    else: 
        path = sys.path[static_data_unsharable.project_sys_path_position] + static_data_unsharable.project_separator_path + "data"
    
    #read cycles data file
    cycle_data_df = pd.read_csv(
            path + static_data_unsharable.project_separator_path +  "cycles_data" + static_data_unsharable.project_separator_path + "cycles_data.csv",
            usecols=[0,1],
            names=["pair",'born_at_cycle'],
            skiprows=[0]
        )
    #get updates
    updates = []
    for key, value in final_dataset.items():
        #analyze 1 week of data on any pair
        
        #setting cycle data, if no data found set it as new coin
        if cycle_data_df[cycle_data_df.pair==Path(key).stem].empty: 
            cycle = 4
        else:
            cycle = cycle_data_df[cycle_data_df.pair==Path(key).stem].born_at_cycle.item()

        if math.isnan(cycle):
            cycle_text = ""
        else:
            cycle_text = int(cycle)

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
                    'hardstop': utlities_sources.fun_format_4decimal(value.iloc[i]['Close'] - (value.iloc[i]['atr'] * 4)) ,
                    'cycle' : cycle_text
                }   
                updates.append(update_json)
               
            i = i - 1
    print("---CALCULATE LAST UPDATES | END---")
    return sorted(updates, key=lambda d: d['date'],reverse=True) 
        

def get_dashboard_data(final_dataset, positions):
    print("---CALCULATE DASHBOARD| START---")
    #market breath data istance
    counter_bullish_pair_1_week_ago = 0
    counter_bullish_pair_2_week_ago = 0
    counter_bullish_pair_3_week_ago = 0
    counter_bullish_pair_4_week_ago = 0
    counter_bullish_pair_5_week_ago = 0
    counter_bullish_pair_6_week_ago = 0
    #ema distance data istance
    sum_ema_distance = 0
    sum_ema_distance_1_week_ago = 0
    sum_ema_distance_2_week_ago = 0
    sum_ema_distance_3_week_ago = 0
    sum_ema_distance_4_week_ago = 0
    sum_ema_distance_5_week_ago = 0
    sum_ema_distance_6_week_ago = 0

    #market breath data
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

    #market breath data
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
    
    print("---CALCULATE DASHBOARD| END---")
    return dashboard_json