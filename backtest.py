import ccxt
import config
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
import warnings
warnings.filterwarnings('ignore')
import pandas_ta as ta

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.SECRET_KEY,
})

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
    print('Win rate: '+ str((win_rate/trades)*100)+'%' if trades != 0 else 'no trades made'+'%')
    print('Total P&L: '+str(p_l_sum)+'%')
    print('Biggest Win: '+str(biggest_win)+'%')
    print('Biggest Loss: '+str(biggest_loss)+'%')
    print('\n-------------------------------------------------------------\n')
        
bars = exchange.fetch_ohlcv('ETH/USDT', timeframe ='5m', limit=1000)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', )
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern').dt.tz_localize(None)

df.ta.supertrend(length=7, multiplier=3, append=True)
df.rename(columns={'SUPERT_7_3.0': 'trend'}, inplace=True)
df.rename(columns={'SUPERTd_7_3.0': 'in_uptrend'}, inplace=True)
df.rename(columns={'SUPERTl_7_3.0': 'long'}, inplace=True)
df.rename(columns={'SUPERTs_7_3.0': 'short'}, inplace=True)

back_test(df)

df.plot(x='timestamp', y= ['trend','long', 'short', 'close'], grid = True, color=['grey', 'green', 'red', 'black'])
plt.show()








