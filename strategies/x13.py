from strategies.helper import *


def x13_strategy(data, stop_loss):

    stop_gain = 100

    ema13 = TA.EMA(data, 13)
    ema34 = TA.EMA(data, 34)

    buy = []
    sell = []
    stop = []
    end = []
    gain = []
    loss = []

    current_stop = None
    current_goal = None
    current_entry = None
    current_entry_i = None
    current_operation = None

    initial_conditions_passed = False

    for i, _ in enumerate(data['close'], 0):

        if i > 34:
            initial_conditions_passed = True

        candle = {
            'open': data['open'][i],
            'close': data['close'][i],
            'high': data['high'][i],
            'low': data['low'][i]
        }

        indicators = {
            'ema13': ema13[i],
            'ema34': ema34[i],
        }

        gain.append(None)
        loss.append(None)

        if initial_conditions_passed:

            if candle_passed_through_indicator(candle, indicators['ema13']) and candle_opened_bellow_indicator(candle, indicators['ema13']) and candle_is_positive(candle) and indicators['ema13'] > indicators['ema34']:
                if not current_operation:
                    current_operation = 'buy'
                    current_entry = indicators['ema13']
                    current_entry_i = i
                    current_stop = indicators['ema13'] - stop_loss
                    current_goal = indicators['ema13'] + stop_gain
                    buy.append(indicators['ema13'])
                else:
                    buy.append(None)
            else:
                buy.append(None)

            if candle_passed_through_indicator(candle, indicators['ema13']) and candle_opened_above_indicator(candle, indicators['ema13']) and candle_is_negative(candle) and indicators['ema13'] < indicators['ema34']:
                if not current_operation:
                    current_operation = 'sell'
                    current_entry = indicators['ema13']
                    current_entry_i = i
                    current_stop = indicators['ema13'] + stop_loss
                    current_goal = indicators['ema13'] - stop_gain
                    sell.append(indicators['ema13'])
                else:
                    sell.append(None)
            else:
                sell.append(None)
        else:
            sell.append(None)
            buy.append(None)

        if current_operation:

            if candle_passed_through_indicator(candle, current_stop):

                end.append(current_stop)
                stop.append(current_stop)

                if i - current_entry_i > 0:
                    for j in range(current_entry_i, i + 1, 1):
                        loss[j] = current_entry + ((current_stop - current_entry) / (
                            i - current_entry_i)) * (j - current_entry_i)

                current_operation = None
                current_stop = None
                current_goal = None
                current_entry = None
                current_entry_i = None

            elif candle_passed_through_indicator(candle, current_goal):

                end.append(current_goal)
                stop.append(current_stop)

                if i - current_entry_i > 0:
                    for j in range(current_entry_i, i + 1, 1):
                        gain[j] = current_entry + ((current_goal - current_entry) / (
                            i - current_entry_i)) * (j - current_entry_i)

                current_operation = None
                current_stop = None
                current_goal = None
                current_entry = None
                current_entry_i = None

            else:
                end.append(None)
        else:
            end.append(None)

        if len(stop) < i + 1:
            if current_stop:
                stop.append(current_stop)
            else:
                stop.append(None)

    results = {
        'title': "X13",
        'buy': buy,
        'sell': sell,
        'stop': stop,
        'end': end,
        'gain': gain,
        'loss': loss,
        'plot': [
            go.Scatter(
                x=data['date_time'],
                y=ema13,
                mode="lines",
                name="EMA 13",
                line=dict(
                    color='orange',
                    width=2,
                )
            ),
            go.Scatter(
                x=data['date_time'],
                y=ema34,
                mode="lines",
                name="EMA 34",
                line=dict(
                    color='black',
                    width=2,
                )
            )
        ]
    }

    results['statistics'] = get_statistics(results)

    return results


def rt_x13_strategy(data, meta_data, stop_loss):

    stop_gain = 100

    if meta_data == None:
        meta_data = {
            'current_stop': None,
            'current_goal': None,
            'current_operation':  None,
            'come_back_conditions_passed': None
        }

    last_candle = len(data['close']) - 1

    candle = {
        'open': data['open'][last_candle],
        'close': data['close'][last_candle],
        'high': data['high'][last_candle],
        'low': data['low'][last_candle]
    }

    ema13 = TA.EMA(data, 13)
    ema34 = TA.EMA(data, 34)
    indicators = {
        'ema13': ema13[last_candle],
        'ema34': ema34[last_candle],
    }

    action = None

    if indicators['ema34']:

        if not meta_data['current_operation']:

            if candle_passed_through_indicator(candle, indicators['ema13']) and candle_opened_bellow_indicator(candle, indicators['ema13']) and candle_is_positive(candle) and indicators['ema13'] > indicators['ema34']:
                
                meta_data['current_operation'] = 'buy'
                meta_data['current_stop'] = candle['close'] - stop_loss
                meta_data['current_goal'] = candle['close'] + stop_gain
                
                action = 'buy'

            if candle_passed_through_indicator(candle, indicators['ema13']) and candle_opened_above_indicator(candle, indicators['ema13']) and candle_is_negative(candle) and indicators['ema13'] < indicators['ema34']:
               
                meta_data['current_operation'] = 'sell'
                meta_data['current_stop'] = candle['close'] + stop_loss
                meta_data['current_goal'] = candle['close'] - stop_gain
                
                action = 'sell'

        elif meta_data['current_operation']:

            if candle_passed_through_indicator(candle, current_stop) or candle_passed_through_indicator(candle, current_goal):

                if meta_data['current_operation'] == 'buy':
                    action = 'sell'
                else:
                    action = 'buy'

                meta_data['current_operation'] = None
                meta_data['current_stop'] = None
                meta_data['current_goal'] = None


    return action, meta_data
