import src.indicator.utility as indicator_utility
import sys
from os import listdir
from os.path import isfile, join


print("----- START OUT_OF_SAMPLE BACKTESTING -----")
final_dataset = indicator_utility.calculate_dataset()

for key, value in final_dataset.items():
    print(key+", " + str(value.status) + ", " + str(value.last_emacross_price))
  

#def bullish_cross(data_df):
#    for index, row in data_df.iterrows():
#        print(index, row['Date'], row['Fast-Ema'], row['Slow-Ema'])

