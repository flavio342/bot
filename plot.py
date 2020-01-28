#import plotly.graph_objects as go
import plotly.graph_objs as go


def plot_results(data, results):

    general_plot = [
        go.Candlestick(
            x=data['date_time'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="Cotacao"
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['gain'],
            mode="lines",
            name="Gain",
            line=dict(
                color='green',
                width=2,
            )
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['loss'],
            mode="lines",
            name="Loss",
            line=dict(
                color='red',
                width=2,
            )
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['stop'],
            mode="lines",
            name="Stop Loss",
            line=dict(
                color='black',
                width=1,
            )
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['buy'],
            mode="markers",
            name="Buy",
            line=dict(
                color='blue',
                width=4,
            )
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['sell'],
            mode="markers",
            name="Sell",
            line=dict(
                color='purple',
                width=4,
            )
        ),
        go.Scatter(
            x=data['date_time'],
            y=results['end'],
            mode="markers",
            name="end",
            line=dict(
                color='gold',
                width=4,
            )
        )
    ]

    for i in general_plot:
        results['plot'].append(i)

    fig = go.Figure(data=results['plot'])

    min_day = 100000000
    max_day = 0

    for i, _ in enumerate(data['close'], 0):

        candle = {
            'open': data['open'][i],
            'close': data['close'][i],
            'high': data['high'][i],
            'low': data['low'][i]
        }

        if candle['high'] > max_day:
            max_day = candle['high']

        if candle['low'] < min_day:
            min_day = candle['low']

    gap = (max_day - min_day) * 0.1

    fig.update_yaxes(range=[min_day - gap, max_day + gap])

    fig.update_layout(
        title=results['title']
    )

    fig.show()


def plot_data(data):


    general_plot = [
        go.Candlestick(
            x=data['date_time'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="Cotacao"
        )
    ]

    fig = go.Figure(data=general_plot)

    min_day = 100000000
    max_day = 0

    for i, _ in enumerate(data['close'], 0):

        candle = {
            'open': data['open'][i],
            'close': data['close'][i],
            'high': data['high'][i],
            'low': data['low'][i]
        }

        if candle['high'] > max_day:
            max_day = candle['high']

        if candle['low'] < min_day:
            min_day = candle['low']

    gap = (max_day - min_day) * 0.1

    fig.update_yaxes(range=[min_day - gap, max_day + gap])

    fig.show()