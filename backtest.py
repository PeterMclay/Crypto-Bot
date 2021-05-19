import ccxt
import config
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
from ta.volatility import BollingerBands, AverageTrueRange
import warnings
warnings.filterwarnings('ignore')
import schedule
import time
import pandas_ta as ta

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.SECRET_KEY,
})

in_position = False
starting_cash = 1000.00
cash = 1000.00
coin_amount = 0.0
ledger = open('ledger.txt', 'w')
ledger.write(f"Starting Cash = {starting_cash}\n")
counter = 5

def tr(df):
    df['previous_close'] = df['close'].shift(1)
    df['high-low'] = df['high'] - df['low']
    df['abs high-close'] = abs(df['high'] - df['previous_close'])
    df['abs low-close'] = abs(df['low'] - df['previous_close'])
    true_range = df[['high-low', 'abs high-close', 'abs low-close']].max(axis=1)
    return true_range

def atr(df, period=14):
    df['tr'] = tr(df)
    _atr = df['tr'].rolling(period).mean()
    return _atr

def ma(df, period=30):
    _ma = df['close'].rolling(window=period).mean()
    return(_ma)

def supertrend(df, period=7, multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['moving_average'] = ma(df)
    df['upperband'] = hl2 + (multiplier * df['atr'])
    df['lowerband'] = hl2 - (multiplier * df['atr'])
    df['in_uptrend'] = 1

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = 1
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = -1
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
    
    return df

def back_test(df):
    print(df)
    buy_list = []
    sell_list = []
    buy_time = []
    sell_time = []
    in_position = False
    for current in range (1, len(df.index)):
        previous =  current - 1
        if df['in_uptrend'][previous] == -1 and df['in_uptrend'][current] == 1 and not in_position:
            #Buy
            in_position = True
            buy_list.append(df['close'][current])
            buy_time.append(df['timestamp'][current])
        if df['in_uptrend'][previous] == 1 and df['in_uptrend'][current] == -1 and in_position:
            #Sell
            in_position = False
            sell_list.append(df['close'][current])
            sell_time.append(df['timestamp'][current])

    if in_position:
        del buy_list[-1]
        del buy_time[-1]

    print('\n-------------------------- Trades --------------------------\n')
    win_rate = 0
    p_l_sum = 0
    trades = len(buy_list)
    biggest_win = 0
    biggest_loss = 0
    for index in range(len(buy_list)):
        p_l_percent = ((sell_list[index] - buy_list[index]) / sell_list[index]) * 100
        p_l_sum += p_l_percent

        if p_l_percent > biggest_win:
            biggest_win = p_l_percent
        if p_l_percent < biggest_loss:
            biggest_loss = p_l_percent

        print('Buy Price: '+str(buy_list[index])+' at '+str(buy_time[index]))
        print('Sell Price: '+str(sell_list[index])+' at '+str(sell_time[index]))
        print('P&L = '+str(p_l_percent)+'%')
        if p_l_percent > 0:
            win_rate += 1
            print("WIN\n")
        else:
            print("LOSS\n")

    print('-------------------------- SUMMARY --------------------------\n')
    print('Trades made: '+str(trades))
    print('Win rate: '+str((win_rate/trades)*100)+'%')
    print('Total P&L: '+str(p_l_sum)+'%')
    print('Biggest Win: '+str(biggest_win)+'%')
    print('Biggest Loss: '+str(biggest_loss)+'%')
    print('\n-------------------------------------------------------------\n')
        
def run_supertrend(period=7, multiplier=3):
    print("Fetching Data")
    bars = exchange.fetch_ohlcv('ETH/USDT', timeframe ='15m', limit=1000)  
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', )
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.tz_localize(None)
    super_trend = supertrend(df)
    print(super_trend)
    #back_test(super_trend)

# My Calculations
#run_supertrend()

#TA Calculations
bars = exchange.fetch_ohlcv('DOGE/USDT', timeframe ='5m', limit=144)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', )
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.tz_localize(None)
super_trend = ta.supertrend(df['high'], df['low'], df['close'])
print('+_+_+_+_+_+_+_+_+_+_+_+_+ TA Data +_+_+_+_+_+_+_+_+_+_+_+_+')
super_trend.rename(columns={'SUPERTd_7_3.0': 'in_uptrend'}, inplace=True)
super_trend['close'] = df['close']
super_trend['timestamp'] = df['timestamp']
back_test(super_trend)




# super_trend['close'] = df['close']
# #df[df.high, df.low].plot(color=['green', 'red'], grid=true)
# x = df['timestamp']
# y1 = df['high']
# y2 = df['close']
# df[['high', 'low']].plot()
# #plt.plot(x, y1)
# #plt.plot(x, y2)
# #super_trend.plot[['close']]
# # super_trend[super_trend.columns[-3:]].plot(color=["green", "red", "black"], grid=True)
# plt.show()






