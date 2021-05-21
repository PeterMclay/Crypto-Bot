import pandas as pd
pd.set_option('display.max_rows', None)
import yfinance as yf
import pandas_ta as ta

def back_test(df):
    # print(df)
    buy_list = []
    sell_list = []
    buy_time = []
    sell_time = []
    in_position = False
    stop_loss_price = 0
    for current in range (1, len(df.index)):
        previous =  current - 1
        if df['in_uptrend'][previous] == -1 and df['in_uptrend'][current] == 1 and not in_position:
            #Buy
            in_position = True
            buy_list.append(df['close'][current])
            stop_loss_price = df['close'][current]
            buy_time.append((df.index[current]))

        #Gain Break
        # if in_position and (((df['close'][current] - stop_loss_price)/stop_loss_price)*100 >= 4):
        #     print('Gains met at 4%')
        #     stop_loss_price = 0
        #     sell_list.append(df['close'][current])
        #     sell_time.append((df.index[current]))
        #     in_position = False
        
        #Stop Loss
        if in_position and (((df['close'][current] - stop_loss_price)/stop_loss_price)*100 <= -1.75):
            print('Stop loss of -2% met')
            stop_loss_price = 0
            sell_list.append(df['close'][current])
            sell_time.append((df.index[current]))
            in_position = False
        if df['in_uptrend'][previous] == 1 and df['in_uptrend'][current] == -1 and in_position:
            #Sell
            in_position = False
            sell_list.append(df['close'][current])
            sell_time.append((df.index[current]))

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
        p_l_percent = ((sell_list[index] - buy_list[index]) / buy_list[index]) * 100
        p_l_sum += p_l_percent

        if p_l_percent > biggest_win:
            biggest_win = p_l_percent
        if p_l_percent < biggest_loss:
            biggest_loss = p_l_percent

        print('Buy Price: '+str(buy_list[index])+' at '+str(buy_time[index]))
        print('Sell Price: '+str(sell_list[index])+' at '+str(sell_time[index]))
        print('P&L = '+str(p_l_percent)+'%')
        if ((sell_list[index] - buy_list[index])/buy_list[index])*100 <= -1:
            print('Trade quit from stop loss')

        if p_l_percent > 0:
            win_rate += 1
            print("WIN\n")
        else:
            print("LOSS\n")

    print('-------------------------- SUMMARY --------------------------\n')
    print("Data From : "+str(df.index[0])+" to "+ str(df.index[-1]))
    print('Trades made: '+str(trades))
    print('Win rate: '+ str((win_rate/trades)*100)+'%' if trades != 0 else 'no trades made'+'%')
    print('Total P&L: '+str(p_l_sum)+'%')
    print('Biggest Win: '+str(biggest_win)+'%')
    print('Biggest Loss: '+str(biggest_loss)+'%')
    print('\n-------------------------------------------------------------\n')
 

eth = yf.Ticker('XLM-USD')
data = eth.history(interval='5m', period='1d')
del data['Dividends']
del data['Stock Splits']
data.ta.supertrend(length=7, multiplier=3, append=True)
data.rename(columns={'SUPERT_7_3.0': 'trend', 'SUPERTd_7_3.0': 'in_uptrend', 'SUPERTl_7_3.0': 'long', 'SUPERTs_7_3.0': 'short'}, inplace=True)
back_test(data)
