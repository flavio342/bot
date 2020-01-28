
from finta import TA
import pandas as pd
import plotly.graph_objs as go


def candle_closed_above_indicator(candle, indicator):
    if candle['close'] > indicator:
        return True
    else:
        return False


def candle_closed_bellow_indicator(candle, indicator):
    if candle['close'] < indicator:
        return True
    else:
        return False


def candle_opened_above_indicator(candle, indicator):
    if candle['open'] > indicator:
        return True
    else:
        return False


def candle_opened_bellow_indicator(candle, indicator):
    if candle['open'] < indicator:
        return True
    else:
        return False


def candle_passed_through_indicator(candle, indicator):
    if candle['low'] < indicator and indicator < candle['high']:
        return True
    else:
        return False


def candle_is_positive(candle):
    if candle['close'] > candle['open']:
        return True
    else:
        return False


def candle_is_negative(candle):
    if candle['close'] < candle['open']:
        return True
    else:
        return False


def format_statistics(statistic):

    statistic['%_trades_gain'] = str(
        "{0:.2f}".format(statistic['%_trades_gain'])) + "%"

    for i in range(1, 6, 1):
        statistic[str(i) + "_mc"] = "R$ " + \
            str("{0:.2f}".format(statistic[str(i) + "_mc"]))

    statistic['total_gain'] = str(
        "{0:.2f}".format(statistic['total_gain'])) + " pts"
    statistic['total_loss'] = str(
        "{0:.2f}".format(statistic['total_loss'])) + " pts"
    statistic['balance'] = str("{0:.2f}".format(statistic['balance'])) + " pts"
    statistic['average_gain'] = str(
        "{0:.2f}".format(statistic['average_gain'])) + " pts"
    statistic['average_loss'] = str(
        "{0:.2f}".format(statistic['average_loss'])) + " pts"

    if 'current_pts' in statistic:
        if statistic['current_pts'] != "":
            statistic['current_pts'] = str(
            "{0:.2f}".format(statistic['current_pts'])) + " pts"

    if 'current_entry' in statistic:
        if statistic['current_entry'] != "":
            statistic['current_entry'] = "R$ " + \
                str("{0:.2f}".format(statistic['current_entry']))

    if 'price' in statistic:
        statistic['price'] = "R$ " + \
            str("{0:.2f}".format(statistic['price']))

    return statistic


def get_statistics(data):

    statistic = {
        'trades': 0,
        'trades_loss': 0,
        'trades_gain': 0,
        '%_trades_gain': 0,
        'total_gain': 0,
        'total_loss': 0,
        'average_gain': 0,
        'average_loss': 0,
        'balance': 0,
        '1_mc': 0,
        '2_mc': 0,
        '3_mc': 0,
        '4_mc': 0,
        '5_mc': 0,
    }

    current_operation = None
    current_entry = None
    for i, _ in enumerate(data['buy'], 0):

        if data['buy'][i]:
            current_operation = 'buy'
            current_entry = data['buy'][i]

        if data['sell'][i]:
            current_operation = 'sell'
            current_entry = data['sell'][i]

        if data['end'][i]:

            variation = data['end'][i] - current_entry

            if (current_operation == 'buy' and variation > 0) or (current_operation == 'sell' and variation < 0):
                statistic['total_gain'] += abs(variation)
                statistic['trades_gain'] += 1
            elif (current_operation == 'buy' and variation < 0) or (current_operation == 'sell' and variation > 0):
                statistic['total_loss'] += abs(variation)
                statistic['trades_loss'] += 1

    statistic['trades'] = statistic['trades_gain'] + statistic['trades_loss']

    if statistic['trades'] > 0:
        statistic['%_trades_gain'] = (
            statistic['trades_gain'] / statistic['trades']) * 100

    statistic['balance'] = statistic['total_gain'] - statistic['total_loss']

    if statistic['trades_gain'] > 0:
        statistic['average_gain'] = statistic['total_gain'] / \
            statistic['trades_gain']

    if statistic['trades_loss']:
        statistic['average_loss'] = statistic['total_loss'] / \
            statistic['trades_loss']

    for i in range(1, 6, 1):
        statistic[str(i) + "_mc"] = statistic['balance'] * 0.2 * i

    return statistic
