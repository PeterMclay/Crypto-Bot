import ccxt
import config
import ta
import pandas as pd
from ta.volatility import BollingerBands, AverageTrueRange

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.SECRET_KEY,
})

bars = exchange.fetch_ohlcv('ETH/USDT', limit=20)
df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

bb_indicator = BollingerBands(df['Close'], window=20, window_dev=2, fillna = True)

df['lower_band'] = bb_indicator.bollinger_lband()
df['upper_band'] = bb_indicator.bollinger_hband()
df['moving_average'] = bb_indicator.bollinger_mavg()

atr_indicator = AverageTrueRange(df['High'], df['Low'], df['Close'], fillna= True)
df['ATR'] = atr_indicator.average_true_range()
print(df)



