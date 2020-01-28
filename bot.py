import pandas as pd
from datetime import datetime
import time

from strategies.bollinger import rt_bollinger_strategy
from strategies.keltner import rt_keltner_strategy
from strategies.combine import rt_combine_strategies_wait

from strategies.helper import format_statistics

STOP_LOSS = 50

INIT_DAILY_STOP_LOSS = - STOP_LOSS * 2
DAILY_STOP_LOSS = 0

current_entry = None
current_pts = None
accumulated_pts = 0
trades = 0
trades_gain = 0
trades_loss = 0
percent_trades_gain = 0
total_gain = 0
total_loss = 0
average_gain = 0
average_loss = 0

def get_statistics(price, time, combine_action, combine_meta_data):

    global current_entry
    global current_pts
    global accumulated_pts
    global trades
    global trades_gain
    global trades_loss
    global percent_trades_gain
    global total_gain
    global total_loss
    global average_gain
    global average_loss

    if combine_meta_data['current_operation'] == 'sell':
        if current_entry:
            current_pts = current_entry - price
        else:
            current_pts = 0

    elif combine_meta_data['current_operation'] == 'buy':
        if current_entry:
            current_pts = price - current_entry
        else:
            current_pts = 0

    else:
        if combine_action == 'sell':
            current_pts = price - current_entry
        elif combine_action == 'buy':
            current_pts = current_entry - price
        else:
            current_pts = None

    if combine_action != None:
        if current_entry != None:

            trades += 1
            if current_pts >= 0:
                trades_gain += 1
                total_gain += current_pts
            else:
                trades_loss += 1
                total_loss += current_pts

            percent_trades_gain = trades_gain / trades * 100

            current_entry = None
            if current_pts:
                accumulated_pts += current_pts
        else:
            current_entry = price

    now = datetime.now().strftime("%H:%M:%S")

    if trades_gain > 0:
        average_gain = total_gain / trades_gain
    if trades_loss > 0:
        average_loss = total_loss / trades_loss

    row = {
        'time': time,
        'action': combine_action if combine_action != None else "",
        'current_operation': combine_meta_data['current_operation'] if combine_meta_data['current_operation'] != None else "",
        'price': price,
        'current_entry': current_entry if current_entry != None else "",
        'current_pts': current_pts if current_pts != None else "",
        'balance': accumulated_pts,
        'trades': trades,
        'trades_loss': trades_loss,
        'trades_gain': trades_gain,
        '%_trades_gain': percent_trades_gain,
        'total_gain':  total_gain,
        'total_loss': total_loss,
        'average_gain': average_gain,
        'average_loss': average_loss
    }

    for i in range(1, 6, 1):
        row[str(i) + "_mc"] = row['balance'] * 0.2 * i

    row = format_statistics(row)

    write_statistics(row)

def write_header_and_columns():

    f = open("./rt_results.txt", "w")

    now = datetime.now().strftime("%b %d %Y")
    f.write(now + "\n")

    f.write("\n")

    row = blank_statistics()
    for atribute in row:
        f.write("|{:^15}".format(atribute))
    f.write("\n")

    f.close()

def write_statistics(row):

    f = open("./rt_results.txt", "a")

    f.write("\n")

    for atribute in row:
        f.write("|{:^15}".format(str(row[atribute])))

    f.close()

def blank_statistics():

    return {
        'time': None,
        'action': None,
        'current_op': None,
        'price': None,
        'current_entry': None,
        'current_pts': None,
        'balance': None,
        'trades': None,
        'trades_loss': None,
        'trades_gain': None,
        '%_trades_gain': None,
        'total_gain': None,
        'total_loss': None,
        'average_gain': None,
        'average_loss': None,
        '1_mc': None,
        '2_mc': None,
        '3_mc': None, 
        '4_mc': None,
        '5_mc': None      
    }


def stop_all_operations(combine_meta_data, strategies_meta_data):

    print("STOP")

    combine_meta_data['current_operation'] = None
    combine_meta_data['current_stop'] = None
    combine_meta_data['current_strategy_j'] = None
    combine_meta_data['buy_orders'] = 0
    combine_meta_data['buy_first_order_i'] = 0
    combine_meta_data['sell_orders'] = 0
    combine_meta_data['sell_first_order_i'] = 0

    for i in range(len(strategies_meta_data)):

        strategies_meta_data[i]['current_operation']  = None
        strategies_meta_data[i]['current_stop'] = None
        strategies_meta_data[i]['come_back_conditions_passed'] = False

def run():

    global STOP_LOSS

    write_header_and_columns()

    strategies = {
        '1': {
            'function': rt_bollinger_strategy,
            'data': None,
            'meta_data': None
        },
        '2': {
            'function': rt_keltner_strategy,
            'data': None,
            'meta_data': None
        }
    }

    combine_meta_data = None

    current_n_candles = 0
    current_n_prices = 0
    price = None
    prices = None

    while True:

        try:
            data = pd.read_csv('copy_data.csv')
            
            """price_f = open("current_price", "r")
            prices = price_f.readlines()
            price_f.close()"""
        except:
            continue

        if prices:
            n_prices = len(prices)-1
            if n_prices > current_n_prices:
                current_n_prices = n_prices
                price = float(prices[n_prices-1])
            else:
                price = None
        else:
            price = None

        if combine_meta_data and combine_meta_data['current_operation'] == 'sell':

            if price and price >= combine_meta_data['current_stop']:
                
                stop_all_operations(combine_meta_data, [ strategies['1']['meta_data'], strategies['2']['meta_data'] ] )

                get_statistics(price, data, 'buy', combine_meta_data)

        elif combine_meta_data and combine_meta_data['current_operation'] == 'buy':

            if price and price <= combine_meta_data['current_stop']:

                stop_all_operations(combine_meta_data, [ strategies['1']['meta_data'], strategies['2']['meta_data'] ])

                get_statistics(price, data, 'sell', combine_meta_data)

        n_candles = len(data['close'])
        if n_candles > current_n_candles:
            
            current_n_candles = n_candles

            strategies['1']['data'], strategies['1']['meta_data'] = strategies['1']['function'](data, strategies['1']['meta_data'], STOP_LOSS)
            strategies['2']['data'], strategies['2']['meta_data'] = strategies['2']['function'](data, strategies['2']['meta_data'], STOP_LOSS)

            combine_action, combine_meta_data = rt_combine_strategies_wait([ strategies['1']['data'], strategies['2']['data'] ], [ strategies['1']['meta_data'], strategies['2']['meta_data'] ], 2, 44, combine_meta_data)

            price = data['close'][n_candles-1]
            time = data['date_time'][n_candles-1].split(" ")[1]

            get_statistics(price, time, combine_action, combine_meta_data)


run()