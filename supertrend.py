import ccxt
import config
import ta
import pandas as pd
pd.set_option('display.max_rows', None)
from ta.volatility import BollingerBands, AverageTrueRange
import warnings
warnings.filterwarnings('ignore')
import schedule
import time

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

def supertrend(df, period=7, multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (multiplier * df['atr'])
    df['lowerband'] = hl2 - (multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
    
    return df

def check_buy_sell(df):
    global in_position
    global cash
    global coin_amount
    global ledger
    print(df.tail(2))
    current = len(df.index) -1
    previous = current - 1
    if not df['in_uptrend'][previous] and df['in_uptrend'][current] and not in_position:
        in_position = True
        coin_amount = cash / df['close'][current]
        print('Executing Buy')
        ledger.write("Executing buy at "+str(df['timestamp'][current])+'. Current cash = '+str(cash)+'. Amount bought = '+str(coin_amount)+'. Price: '+str(df['close'][current])+'\n')
    
    if df['in_uptrend'][previous] and not df['in_uptrend'][current] and in_position:
        in_position = False
        cash = coin_amount * df['close'][current]
        coin_amount = 0
        print('Sell')
        ledger.write("Executing sell at "+df['timestamp']+'. Current Cash = '+str(cash)+'. Amount Sold = '+str(coin_amount)+'. Price: '+str(df['close'])+'\n')

def run_supertrend():
    print("Fetching Data")
    bars = exchange.fetch_ohlcv('ETH/USDT', timeframe ='1m', limit=100)  
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', )
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.tz_localize(None)
    super_trend = supertrend(df)
    print(super_trend)
    check_buy_sell(super_trend)

schedule.every(5).seconds.do(run_supertrend)

while True:
    schedule.run_pending()
    time.sleep(1)









