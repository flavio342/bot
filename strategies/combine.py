from finta import TA
import pandas as pd
import plotly.graph_objs as go

from strategies.helper import *


def combine_strategies_wait(strategies_data, n_confirm, n_wait):

    buy = []
    sell = []
    stop = []
    end = []
    gain = []
    loss = []

    buy_orders = 0
    buy_first_order_i = 0

    sell_orders = 0
    sell_first_order_i = 0

    current_operation = None
    current_entry = None
    current_entry_i = None
    current_strategy_j = None

    for i, _ in enumerate(strategies_data[0]['buy'], 0):

        gain.append(None)
        loss.append(None)

        for j in range(len(strategies_data)):

            if not current_operation:

                if strategies_data[j]['buy'][i]:

                    if (buy_orders == 0) or (i - buy_first_order_i > n_wait):
                        buy_orders = 1
                        buy_first_order_i = i
                    else:
                        buy_orders += 1

                    if buy_orders >= n_confirm:
                        current_operation = 'buy'
                        current_entry = strategies_data[j]['buy'][i]
                        current_entry_i = i
                        current_strategy_j = j
                        buy.append(strategies_data[j]['buy'][i])

                if strategies_data[j]['sell'][i]:

                    if (sell_orders == 0) or (i - sell_first_order_i > n_wait):
                        sell_orders = 1
                        sell_first_order_i = i
                    else:
                        sell_orders += 1

                    if sell_orders >= n_confirm:
                        current_operation = 'sell'
                        current_entry = strategies_data[j]['sell'][i]
                        current_entry_i = i
                        current_strategy_j = j
                        sell.append(strategies_data[j]['sell'][i])

            if current_operation and current_strategy_j == j:

                if strategies_data[j]['end'][i]:

                    end.append(strategies_data[j]['end'][i])

                    variation = strategies_data[j]['end'][i] - current_entry

                    if (current_operation == 'buy' and variation > 0) or (current_operation == 'sell' and variation < 0):

                        if i - current_entry_i > 0:
                            for j in range(current_entry_i, i + 1, 1):
                                gain[j] = current_entry + \
                                    (variation / (i - current_entry_i)) * \
                                    (j - current_entry_i)

                    elif (current_operation == 'buy' and variation < 0) or (current_operation == 'sell' and variation > 0):

                        if i - current_entry_i > 0:
                            for j in range(current_entry_i, i + 1, 1):
                                loss[j] = current_entry + \
                                    (variation / (i - current_entry_i)) * \
                                    (j - current_entry_i)

                    current_operation = None
                    current_entry_i = None
                    current_entry = None
                    current_strategy_j = None
                    buy_orders = 0
                    buy_first_order_i = 0
                    sell_orders = 0
                    sell_first_order_i = 0

        if len(buy) < i + 1:
            buy.append(None)

        if len(sell) < i + 1:
            sell.append(None)

        if len(end) < i + 1:
            end.append(None)

        stop.append(None)

    title = ""
    for j in range(len(strategies_data)):
        title += strategies_data[j]['title'] + "_"

    title += "wait"

    results = {
        'title': title,
        'buy': buy,
        'sell': sell,
        'stop': stop,
        'end': end,
        'gain': gain,
        'loss': loss,
        'plot': []
    }

    results['statistics'] = get_statistics(results)

    return results


def rt_combine_strategies_wait(strategies_data, strategies_meta_data, n_confirm, n_wait, meta_data):

    action = None

    if meta_data == None:
        meta_data = {
            'current_i': 0,
            'buy_orders': 0,
            'buy_first_order_i': 0,
            'sell_orders': 0,
            'sell_first_order_i': 0,
            'current_operation': None,
            'current_strategy_j': None
        }

    meta_data['current_i'] += 1

    for j in range(len(strategies_data)):

        if not meta_data['current_operation']:

            if strategies_data[j] == 'buy':

                if (meta_data['buy_orders'] == 0) or (meta_data['current_i'] - meta_data['buy_first_order_i'] > n_wait):
                    meta_data['buy_orders'] = 1
                    meta_data['buy_first_order_i'] = meta_data['current_i']
                
                else:
                    meta_data['buy_orders'] += 1

                if meta_data['buy_orders'] >= n_confirm:
                    meta_data['current_operation'] = 'buy'
                    meta_data['current_stop'] = strategies_meta_data[j]['current_stop']
                    meta_data['current_strategy_j'] = j
                    action = 'buy'

            if strategies_data[j] == 'sell':

                if (meta_data['sell_orders'] == 0) or (meta_data['current_i'] - meta_data['sell_first_order_i'] > n_wait):
                    meta_data['sell_orders'] = 1
                    meta_data['sell_first_order_i'] = meta_data['current_i']
                    
                else:
                    meta_data['sell_orders'] += 1

                if meta_data['sell_orders'] >= n_confirm:
                    meta_data['current_operation'] = 'sell'
                    meta_data['current_stop'] = strategies_meta_data[j]['current_stop']
                    meta_data['current_strategy_j'] = j
                    action = 'sell'
        else:
            if meta_data['current_strategy_j'] == j:

                if strategies_data[j] != None:

                    meta_data['current_operation'] = None
                    meta_data['current_stop'] = None
                    meta_data['current_strategy_j'] = None
                    meta_data['buy_orders'] = 0
                    meta_data['buy_first_order_i'] = 0
                    meta_data['sell_orders'] = 0
                    meta_data['sell_first_order_i'] = 0

                    action = strategies_data[j]

    return action, meta_data


def combine_strategies_first(strategies_data):

    buy = []
    sell = []
    stop = []
    end = []
    gain = []
    loss = []

    current_operation = None
    current_entry = None
    current_entry_i = None
    current_strategy_j = None

    for i, _ in enumerate(strategies_data[0]['buy'], 0):

        gain.append(None)
        loss.append(None)

        for j in range(len(strategies_data)):

            if not current_operation:

                if strategies_data[j]['buy'][i]:

                    current_operation = 'buy'
                    current_entry = strategies_data[j]['buy'][i]
                    current_entry_i = i
                    current_strategy_j = j
                    buy.append(strategies_data[j]['buy'][i])

                if strategies_data[j]['sell'][i]:

                    current_operation = 'sell'
                    current_entry = strategies_data[j]['sell'][i]
                    current_entry_i = i
                    current_strategy_j = j
                    sell.append(strategies_data[j]['sell'][i])

            if current_operation and current_strategy_j == j:

                if strategies_data[j]['end'][i]:

                    end.append(strategies_data[j]['end'][i])

                    variation = strategies_data[j]['end'][i] - current_entry

                    if (current_operation == 'buy' and variation > 0) or (current_operation == 'sell' and variation < 0):

                        if i - current_entry_i > 0:
                            for j in range(current_entry_i, i + 1, 1):
                                gain[j] = current_entry + \
                                    (variation / (i - current_entry_i)) * \
                                    (j - current_entry_i)

                    elif (current_operation == 'buy' and variation < 0) or (current_operation == 'sell' and variation > 0):

                        if i - current_entry_i > 0:
                            for j in range(current_entry_i, i + 1, 1):
                                loss[j] = current_entry + \
                                    (variation / (i - current_entry_i)) * \
                                    (j - current_entry_i)

                    current_operation = None
                    current_entry_i = None
                    current_entry = None
                    current_strategy_j = None

        if len(buy) < i + 1:
            buy.append(None)

        if len(sell) < i + 1:
            sell.append(None)

        if len(end) < i + 1:
            end.append(None)

        stop.append(None)

    title = ""
    for j in range(len(strategies_data)):
        title += strategies_data[j]['title'] + "_"

    title += "first"

    results = {
        'title': title,
        'buy': buy,
        'sell': sell,
        'stop': stop,
        'end': end,
        'gain': gain,
        'loss': loss,
        'plot': []
    }

    results['statistics'] = get_statistics(results)

    return results
