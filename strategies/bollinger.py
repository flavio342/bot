from strategies.helper import *


def bollinger_strategy(data, stop_loss):

    bbands = TA.BBANDS(data)

    buy = []
    sell = []
    stop = []
    end = []
    gain = []
    loss = []

    initial_conditions_passed = False
    come_back_conditions_passed = False

    current_stop = None
    current_entry = None
    current_entry_i = None
    current_operation = None

    for i, _ in enumerate(data['close'], 0):

        candle = {
            'open': data['open'][i],
            'close': data['close'][i],
            'high': data['high'][i],
            'low': data['low'][i]
        }

        indicators = {
            'high': bbands['BB_UPPER'][i],
            'middle': bbands['BB_MIDDLE'][i],
            'low': bbands['BB_LOWER'][i]
        }

        gain.append(None)
        loss.append(None)

        if candle_passed_through_indicator(candle, indicators['middle']):

            come_back_conditions_passed = True
            initial_conditions_passed = True

        if initial_conditions_passed:

            if not current_operation and come_back_conditions_passed:

                end.append(None)
            
                if candle_passed_through_indicator(candle, indicators['low']) and candle_opened_bellow_indicator(candle, indicators['low']) and candle_is_positive(candle) and candle_closed_bellow_indicator(candle, indicators['middle']):
                    current_operation = 'buy'
                    current_entry = indicators['low']
                    current_entry_i = i
                    current_stop = indicators['low'] - stop_loss
                    buy.append(indicators['low'])
                else:
                    buy.append(None)

                if candle_passed_through_indicator(candle, indicators['high']) and candle_opened_above_indicator(candle, indicators['high']) and candle_is_negative(candle) and candle_closed_above_indicator(candle, indicators['middle']):
                 
                    current_operation = 'sell'
                    current_entry = indicators['high']
                    current_entry_i = i
                    current_stop = indicators['high'] + stop_loss
                    sell.append(indicators['high'])
                 
                else:
                    sell.append(None)

            elif current_operation:

                buy.append(None)
                sell.append(None)

                if candle_passed_through_indicator(candle, current_stop):

                    end.append(current_stop)
                    stop.append(current_stop)

                    if i - current_entry_i > 0:
                        for j in range(current_entry_i, i + 1, 1):
                            loss[j] = current_entry + ((current_stop - current_entry) / (
                                i - current_entry_i)) * (j - current_entry_i)

                    current_operation = None
                    current_stop = None
                    current_entry = None
                    current_entry_i = None

                    come_back_conditions_passed = False

                elif candle_passed_through_indicator(candle, indicators['middle']):

                    end.append(indicators['middle'])
                    stop.append(current_stop)

                    if i - current_entry_i > 0:
                        for j in range(current_entry_i, i + 1, 1):
                            gain[j] = current_entry + ((indicators['middle'] - current_entry) / (
                                i - current_entry_i)) * (j - current_entry_i)

                    current_operation = None
                    current_stop = None
                    current_entry = None
                    current_entry_i = None

                else:
                    end.append(None)
            else:
                end.append(None)
                buy.append(None)
                sell.append(None)


            if len(stop) < i + 1:
                if current_stop:
                    stop.append(current_stop)
                else:
                    stop.append(None)

        else:
            sell.append(None)
            buy.append(None)
            end.append(None)
            stop.append(None)

    results = {
        'title': "Bollinger",
        'buy': buy,
        'sell': sell,
        'stop': stop,
        'end': end,
        'gain': gain,
        'loss': loss,
        'plot': [
            go.Scatter(
                x=data['date_time'],
                y=bbands['BB_UPPER'],
                mode="lines",
                name="Bollinger Band (Upper)",
                line=dict(
                    color='#add8e6',
                    width=2,
                )
            ),
            go.Scatter(
                x=data['date_time'],
                y=bbands['BB_LOWER'],
                mode="lines",
                name="Bollinger Band (Lower)",
                line=dict(
                    color='#add8e6',
                    width=2,
                )
            ),
            go.Scatter(
                x=data['date_time'],
                y=bbands['BB_MIDDLE'],
                mode="lines",
                name="Bollinger Band (Middle)",
                line=dict(
                    color='#add8e6',
                    width=2,
                )
            )
        ]
    }

    results['statistics'] = get_statistics(results)

    return results


def rt_bollinger_strategy(data, meta_data, stop_loss):

    if meta_data == None:
        meta_data = {
            'initial_conditions_passed': False,
            'come_back_conditions_passed': False,
            'current_stop': None,
            'current_operation': None
        }

    last_candle = len(data['close']) - 1

    candle = {
        'open': data['open'][last_candle],
        'close': data['close'][last_candle],
        'high': data['high'][last_candle],
        'low': data['low'][last_candle]
    }

    bbands = TA.BBANDS(data)
    indicators = {
        'high': bbands['BB_UPPER'][last_candle],
        'middle': bbands['BB_MIDDLE'][last_candle],
        'low': bbands['BB_LOWER'][last_candle]
    }

    action = None

    if indicators['high']:

        if candle_passed_through_indicator(candle, indicators['middle']):

            meta_data['initial_conditions_passed'] = True
            meta_data['come_back_conditions_passed'] = True

        if meta_data['initial_conditions_passed']:

            if not meta_data['current_operation'] and meta_data['come_back_conditions_passed']:

                if candle_passed_through_indicator(candle, indicators['low']) and candle_opened_bellow_indicator(candle, indicators['low']) and candle_is_positive(candle) and candle_closed_bellow_indicator(candle, indicators['middle']):

                        meta_data['current_operation'] = 'buy'
                        meta_data['current_stop'] = candle['close'] - stop_loss
                        
                        action = 'buy'

                        print("bollinger BUY", candle, meta_data['current_stop'])

                if candle_passed_through_indicator(candle, indicators['high']) and candle_opened_above_indicator(candle, indicators['high']) and candle_is_negative(candle) and candle_closed_above_indicator(candle, indicators['middle']):

                        meta_data['current_operation'] = 'sell'
                        meta_data['current_stop'] = candle['close'] + stop_loss
                        
                        action = 'sell'

                        print("bollinger SELL", candle, meta_data['current_stop'])

            elif meta_data['current_operation']:

                if candle_passed_through_indicator(candle, meta_data['current_stop']):

                    if meta_data['current_operation'] == 'buy':
                        action = 'sell'
                    else:
                        action = 'buy'


                    print("bollinger STOP", action, candle, meta_data['current_stop'])

                    meta_data['current_operation']  = None
                    meta_data['current_stop'] = None
                    meta_data['come_back_conditions_passed'] = False


                elif candle_passed_through_indicator(candle, indicators['middle']):

                    if meta_data['current_operation'] == 'buy':
                        action = 'sell'
                    else:
                        action = 'buy'

                    print("bollinger GAIN", action, candle, meta_data['current_stop'])

                    meta_data['current_operation']  = None
                    meta_data['current_stop'] = None

    return action, meta_data