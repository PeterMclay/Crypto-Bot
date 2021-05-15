import ccxt
import config
import ta
import pandas as pd
from ta.volatility import BollingerBands, AverageTrueRange

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.SECRET_KEY,
})

def tr(df):
    df['previous close'] = df['close'].shift(1)
    df['high-low'] = df['high'] - df['low']
    df['abs high-close'] = abs(df['high'] - df['previous close'])
    df['abs low-close'] = abs(df['low'] - df['previous close'])
    true_range = df[['high-low', 'abs high-close', 'abs low-close']].max(axis=1)
    return true_range

def atr(df):
    df['tr'] = tr(df)
    _atr = df['tr'].rolling(14).mean()
    df['atr'] = _atr

bars = exchange.fetch_ohlcv('ETH/USDT', timeframe = '15m', limit=30)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

atr(df)
print(df)




# BASIC UPPERBAND = (high + low)/2 + multiplier * ATR
# BASIC LOWERBAND = (high - low)/2 + multiplier * ATR

# FINAL UPPERBAND = if ((current basic upperband < previous FINAL upperband) && (previous close < previous FINAL Lowerband)) {CURRENT basic lowerband}
#                   else {PREVIOUS FINAL lowerband}

# FINAL UPPERBAND = if ((current basic lowerband < previous FINAL lowerband) && (previous close < previous FINAL Lowerband)) {CURRENT basic lowerband}
#                   else {PREVIOUS FINAL lowerband}

# SUPERTREND = if (CURRENT close <= CURRENT FINAL UPPERBAND) {CURRENT FINAL upperband}
#              else {CURRENT FINAL lowerband}


