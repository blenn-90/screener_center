import json

class Position:
    #object it represents the result of a strategy backtested  
    def __init__(self, pair, dataset, status, last_emacross_price, last_emacross_date):
        self.pair = pair
        self.dataset = dataset
        self.status = status
        self.last_emacross_price = last_emacross_price
        self.last_emacross_date = last_emacross_date

#create the object
def create_pair_data(pair, dataset, status, last_emacross_price, last_emacross_date):
    return Position(
            pair, 
            dataset,
            status,
            last_emacross_price,
            last_emacross_date)


def get_status(data):

    last_fast_ema = data.iloc[-1]['Fast-Ema']
    last_slow_ema = data.iloc[-1]['Slow-Ema']
    if last_fast_ema > last_slow_ema:
        return 1
    return 0

def get_last_cross(data):
    last_fast_ema = data.iloc[-1]['Fast-Ema']
    last_slow_ema = data.iloc[-1]['Slow-Ema']

    if last_fast_ema > last_slow_ema:
        i = -2
        while data.iloc[i]['Fast-Ema'] > data.iloc[i]['Slow-Ema']:
            i -= 1

    if last_fast_ema < last_slow_ema:
        i = -2
        while data.iloc[i]['Fast-Ema'] < data.iloc[i]['Slow-Ema']:
            i -= 1

    return [data.iloc[i]['Close'], data.iloc[i]['Date']]

def get_status_lable(status):
    if status == 1:
        return 'Long'
    return 'Short'

def check_cross_by_candle(data, i):
    i_fast_ema = data.iloc[i]['Fast-Ema']
    i_slow_ema = data.iloc[i]['Slow-Ema']

    i_previous_fast_ema = data.iloc[i-1]['Fast-Ema']
    i_previous_slow_ema = data.iloc[i-1]['Slow-Ema']

    #bullish cross on this candle
    if i_fast_ema > i_slow_ema and i_previous_fast_ema < i_previous_slow_ema:
        return 1
    
    #bullish cross on this candle
    if i_fast_ema < i_slow_ema and i_previous_fast_ema > i_previous_slow_ema:
        return -1
    
    #no cross
    return 0

def get_update_type(type):
    label = ''
    if type == 1:
        label = 'Bullish Cross'
    elif type == -1:
        label = 'Bearish Cross' 
    
    return label