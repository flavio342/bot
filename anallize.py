import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import time

from strategies.bollinger import bollinger_strategy
from strategies.keltner import keltner_strategy
from strategies.x13 import x13_strategy
from strategies.combine import combine_strategies_wait, combine_strategies_first
from strategies.helper import format_statistics

from plot import plot_results


def merge_data(data):

    merged = {}

    for atribute in data[0]:
        if atribute == 'statistics':
            if atribute not in merged:
                merged[atribute] = {}

            for d in data:
                for inner_atribute in d[atribute]:
                    if inner_atribute not in merged[atribute]:
                        merged[atribute][inner_atribute] = d[atribute][inner_atribute]
                    else:
                        merged[atribute][inner_atribute] += d[atribute][inner_atribute]
        else:
            for d in data:
                if atribute not in merged:
                    merged[atribute] = d[atribute]
                else:
                    merged[atribute] += d[atribute]

    merged['statistics']['%_trades_gain'] = (
        merged['statistics']['trades_gain'] / merged['statistics']['trades']) * 100

    if merged['statistics']['trades_gain'] > 0:
        merged['statistics']['average_gain'] = merged['statistics']['total_gain'] / \
            merged['statistics']['trades_gain']

    if merged['statistics']['trades_loss']:
        merged['statistics']['average_loss'] = merged['statistics']['total_loss'] / \
            merged['statistics']['trades_loss']

    return merged


def plot_comparission(xs, ys, title, x_title, y_title):

    plt.plot(xs, ys, color='#add8e6', linestyle='dashed', linewidth=1,
             marker='o', markerfacecolor='blue', markersize=5)
    plt.title(title)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()


max_wait = 100
analized_files = ['./data/1.csv', './data/2.csv',
                  './data/3.csv', './data/4.csv']
strategies = ['bollinger', 'keltner', 'x13']


now = datetime.now().strftime("%b %d %Y %H:%M:%S")
f = open("./results/" + str(now) + ".txt", "w")
f.write(now + "\n")


strategies_data = {}
combined_wait_strategies = {}
combined_first_strategies = {}
for analized_file_i, analized_file in enumerate(analized_files):

    f.write(analized_file + "\n")

    data = pd.read_csv(analized_file)

    for s in strategies:

        s_data = None
        if s == 'bollinger':
            s_data = bollinger_strategy(data)
        elif s == 'keltner':
            s_data = keltner_strategy(data)
        elif s == 'x13':
            s_data = x13_strategy(data)

        if s not in strategies_data:
            strategies_data[s] = [s_data]
        else:
            strategies_data[s].append(s_data)

    for s_1 in strategies:
        for s_2 in strategies:
            if s_1 != s_2:
                xs = []
                ys = []

                for i in range(max_wait):
                    xs.append(i)
                    res = combine_strategies_wait(
                        [strategies_data[s_1][analized_file_i], strategies_data[s_2][analized_file_i]], 2, i)

                    res['title'] = s_1 + "_" + s_2 + "_wait"

                    ys.append(res['statistics']['5_mc'])

                    if s_1 + "_" + s_2 + "_wait" not in combined_wait_strategies:
                        combined_wait_strategies[s_1 +
                                                 "_" + s_2 + "_wait"] = {}
                        combined_wait_strategies[s_1 +
                                                 "_" + s_2 + "_wait"][i] = [res]
                    else:
                        if i not in combined_wait_strategies[s_1 +
                                                             "_" + s_2 + "_wait"]:
                            combined_wait_strategies[s_1 +
                                                     "_" + s_2 + "_wait"][i] = [res]
                        else:
                            combined_wait_strategies[s_1 +
                                                     "_" + s_2 + "_wait"][i].append(res)

    for s_1 in strategies:
        for s_2 in strategies:
            if s_1 != s_2:

                res = combine_strategies_first(
                    [strategies_data[s_1][analized_file_i], strategies_data[s_2][analized_file_i]])

                res['title'] = s_1 + "_" + s_2 + "_first"
                if s_1 + "_" + s_2 + "_first" not in combined_first_strategies:
                    combined_first_strategies[s_1 +
                                              "_" + s_2 + "_first"] = [res]
                else:
                    combined_first_strategies[s_1 +
                                              "_" + s_2 + "_first"].append(res)

f.write("\n")
for strategie in strategies_data:
    f.write("|{:^30}".format("strategy"))

    for atribute in strategies_data[strategie][0]['statistics']:
        f.write("|{:^15}".format(atribute))
    f.write("\n")
    break

for strategie in strategies_data:
    f.write("\n|{:^30}".format(strategie))

    merged = format_statistics(merge_data(
        strategies_data[strategie])['statistics'])

    for atribute in merged:
        f.write("|{:^15}".format(
            str(merged[atribute])))


filtered_combined_wait_strategies = {}
for s in combined_wait_strategies:

    max_5c = -1000000000000
    max_wait = None
    max_data = None
    for i in combined_wait_strategies[s]:

        sum_5c = 0
        for j in range(len(combined_wait_strategies[s][i])):
            sum_5c += combined_wait_strategies[s][i][j]['statistics']['5_mc']

        if sum_5c > max_5c:
            max_5c = sum_5c
            max_wait = i
            max_data = combined_wait_strategies[s][i]

    filtered_combined_wait_strategies[s + "_" + str(max_wait)] = max_data

f.write("\n")
for strategie in filtered_combined_wait_strategies:
    f.write("\n|{:^30}".format(strategie))

    merged = format_statistics(merge_data(
        filtered_combined_wait_strategies[strategie])['statistics'])

    for atribute in merged:
        f.write("|{:^15}".format(
            str(merged[atribute])))

f.write("\n")
for strategie in combined_first_strategies:
    f.write("\n|{:^30}".format(strategie))

    merged = format_statistics(merge_data(
        combined_first_strategies[strategie])['statistics'])

    for atribute in merged:
        f.write("|{:^15}".format(
            str(merged[atribute])))

"""for strategie in strategies_data:
    plot_results(data, strategies_data[strategie])"""

"""for strategie in combined_wait_strategies:
    plot_results(data, combined_wait_strategies[strategie])"""

"""for strategie in combined_first_strategies:
    plot_results(data, combined_first_strategies[strategie])"""
