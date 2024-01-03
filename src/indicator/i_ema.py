import pandas_ta as ta
import pandas as pd

#ema calculator used in the strategies
def i_ema(data, ema_period):
    ema =  ta.ema(close = data.Close.s, length = ema_period)
    return ema.to_numpy().T

#ema calculator used in the strategies
def i_ema_slow_v2(data, ema_period):
    ema =  ta.ema(close = data.Close, length = ema_period)
    if ema is not None:
        return pd.DataFrame({'Date':ema.index, 'Slow-Ema':ema.values})
    
    return  pd.DataFrame()

#ema calculator used in the strategies
def i_ema_fast_v2(data, ema_period):
    ema =  ta.ema(close = data.Close, length = ema_period)
    if ema is not None:
        return pd.DataFrame({'Date':ema.index, 'Fast-Ema':ema.values})
    
    return  pd.DataFrame()


