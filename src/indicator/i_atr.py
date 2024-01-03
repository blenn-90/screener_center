import pandas_ta as ta
import pandas as pd

#ema calculator used in the strategies
def i_atr(data, length):
    atr = ta.atr(data.High.s, data.Low.s, data.Close.s, length=length)
    return atr.to_numpy().T

def i_atr_v2(data, lenght):
    atr = ta.atr(data.High, data.Low, data.Close, length=lenght)
    if atr is not None:
        return pd.DataFrame({'Date':atr.index, 'ATR':atr.values})
    return  pd.DataFrame()

def get_atr_by_date(atr_df, date):
    return atr_df.loc[date]