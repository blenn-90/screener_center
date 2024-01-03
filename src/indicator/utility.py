import src.indicator.i_atr as indicator_atr
import src.indicator.i_ema as indicator_ema
import src.screener.sources as sources
import src.utilities.noshare_static_data as get_noshare_data 
import src.utilities.get_data.kucoin_data as kucoin_data
import src.classes.position as position
from os import listdir
from os.path import isfile, join
import sys

#building data
def calculate_dataset():
    # retrive all out_of_sample files
    timeframe = "kucoin_4h"
    print("retrive data from {timeframe} folder".format( timeframe = timeframe ))
    print(get_noshare_data.project_sys_path_position)
    path = sys.path[get_noshare_data.project_sys_path_position] + "\\data"
    print(path)
    data_file_set = [f for f in listdir(path + "\\" + timeframe) if isfile(join(path + "\\" + timeframe, f))]
    print("found {number} pairs".format( number = data_file_set.count ))
    final_dataset = {}

    for data_file in data_file_set:
        print("-------------------------reading "+data_file)
        data = kucoin_data.read_csv_data(path, timeframe, data_file)
        #running backtesting
        filter_data = data[ (data.index > "2022-11-01") & (data.index < "2024-02-01")]
        atr_df = indicator_atr.i_atr_v2(filter_data, sources.atr_length)
        ema_fast_df = indicator_ema.i_ema_fast_v2(filter_data, sources.fast_ema)
        ema_slow_df = indicator_ema.i_ema_slow_v2(filter_data, sources.slow_ema)

        if not atr_df.empty and not ema_fast_df.empty and not ema_slow_df.empty:
            temp_df = atr_df.merge(ema_fast_df, how='left', on='Date')
            final_df = temp_df.merge(ema_slow_df, how='left', on='Date')

            #for index, row in final_df[::-1].iterrows():
            #    roll = final_df.index[index]
            
            final_dataset[data_file] = position.create_pair_data(data_file, final_df, position.get_status(final_df), position.get_last_cross_date(final_df), position.get_last_cross_date(final_df))

    return final_dataset