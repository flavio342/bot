from os import path
import os
from datetime import datetime
import pandas as pd

from strategies.bollinger import bollinger_strategy
from strategies.keltner import keltner_strategy
from strategies.x13 import x13_strategy
from strategies.combine import combine_strategies_wait, combine_strategies_first
from strategies.helper import format_statistics

from plot import plot_results

INIT_STOP = 50
MAX_STOP = 52

def append_files_data(files_data, file_data):

    if not files_data:
        files_data = {
            'date_time': [],
            'open': [], 
            'close': [],
            'high': [],
            'low': []
        }

    for atribute in file_data:
        if atribute in files_data:
            for i in range(len(file_data[atribute])):
                files_data[atribute].append(file_data[atribute][i])

    return files_data

def plot_data(appended_files_data, merged_results):

    try:

        choosen_plots = []
        possible_plots = []

        for strategie in merged_results:
            possible_plots.append(strategie)

        print("\nPossible plots:")
        for i, p_p in enumerate(possible_plots):

            print(i, "-", p_p)

        input_plots = input("\nPlots: ")

        if input_plots != "":

            input_plots_arr = input_plots.split(" ")
            for i in input_plots_arr:
                choosen_plots.append(possible_plots[int(i)])

            for p in choosen_plots:
                plot_results(appended_files_data, merged_results[p])

            print("\nPlots choosen:")
            print(choosen_plots)

    except:

        print("Plot error.")
        exit()


def merge_strategies_results(results):

    merged = {}

    for strategie in results:

        if strategie not in merged:
            merged[strategie] = {}

        for result in results[strategie]:

            for atribute in result:

                if atribute == 'statistics':

                    if atribute not in merged[strategie]:
                        merged[strategie][atribute] = {}

                    for inner_atribute in result[atribute]:
                        if inner_atribute not in merged[strategie][atribute]:
                            merged[strategie][atribute][inner_atribute] = result[atribute][inner_atribute]
                        else:
                            merged[strategie][atribute][inner_atribute] += result[atribute][inner_atribute]
                else:
                   
                    if atribute not in merged[strategie]:
                        merged[strategie][atribute] = result[atribute]
                    else:
                        merged[strategie][atribute] += result[atribute]

        if merged[strategie]['statistics']['trades'] > 0:
            merged[strategie]['statistics']['%_trades_gain'] = (merged[strategie]['statistics']['trades_gain'] / merged[strategie]['statistics']['trades']) * 100

        if merged[strategie]['statistics']['trades_gain'] > 0:
            merged[strategie]['statistics']['average_gain'] = merged[strategie]['statistics']['total_gain'] / merged[strategie]['statistics']['trades_gain']

        if merged[strategie]['statistics']['trades_loss']:
            merged[strategie]['statistics']['average_loss'] = merged[strategie]['statistics']['total_loss'] / merged[strategie]['statistics']['trades_loss']

    return merged

def write_results(f, merged_results):

    f.write("\n")
    for strategie in merged_results:
        f.write("\n|{:^30}".format(strategie))

        formatted = format_statistics(merged_results[strategie]['statistics'])

        for atribute in formatted:
            f.write("|{:^15}".format(str(formatted[atribute])))

def write_columns(f, merged_results):

    global INIT_STOP

    f.write("\n")
    for strategie in merged_results:
        f.write("|{:^30}".format("strategy"))
        for atribute in merged_results[strategie][INIT_STOP][0]['statistics']:
            f.write("|{:^15}".format(atribute))
        f.write("\n")
        break
    

def filter_strategies_results(strategies_results, filtered_strategies_results):

    for strategie in strategies_results:

        max_5_mc = -1000000000000
        max_sub_title = None
        max_results = None
        for sub_title in strategies_results[strategie]:

            sum_5_mc = 0
            for i in range(len(strategies_results[strategie][sub_title])):
                sum_5_mc += strategies_results[strategie][sub_title][i]['statistics']['5_mc']

            if sum_5_mc > max_5_mc:
                max_5_mc = sum_5_mc
                max_sub_title = sub_title
                max_results = strategies_results[strategie][sub_title]

        filtered_strategies_results[strategie + "_" + str(max_sub_title)] = max_results


def get_combined_wait_strategies_results(analized_file_i, strategies, strategies_results, combined_wait_strategies_results):

    MAX_WAIT = 100

    global INIT_STOP
    global MAX_STOP

    for s_1 in strategies:
        for s_2 in strategies:
            if s_1 != s_2:

                for stop in range(INIT_STOP, MAX_STOP, 1):
                    for wait in range(MAX_WAIT):
                        
                        print("get combined", s_1, s_2, stop, wait)

                        result = combine_strategies_wait(
                            [
                                strategies_results[s_1][stop][analized_file_i],
                                strategies_results[s_2][stop][analized_file_i]
                            ], 2, wait)

                        stop_wait = str(stop) + "_" + str(wait)

                        if result['title'] not in combined_wait_strategies_results:
                            combined_wait_strategies_results[result['title']] = {}
                            combined_wait_strategies_results[result['title']][stop_wait] = [result]
                        else:
                            if stop_wait not in combined_wait_strategies_results[result['title']]:
                                combined_wait_strategies_results[result['title']][stop_wait] = [result]
                            else:
                                combined_wait_strategies_results[result['title']][stop_wait].append(result)


def get_strategies_results(file_data, strategies, strategies_results):

    global INIT_STOP
    global MAX_STOP

    for s in strategies:

        for stop_loss in range(INIT_STOP, MAX_STOP, 1):

            print("get strategies", s, stop_loss)

            s_data = None
            if s == 'bollinger':
                s_data = bollinger_strategy(file_data, stop_loss)
            elif s == 'keltner':
                s_data = keltner_strategy(file_data, stop_loss)
            elif s == 'x13':
                s_data = x13_strategy(file_data, stop_loss)

            if s not in strategies_results:
                strategies_results[s] = {}
                strategies_results[s][stop_loss] = [s_data]
            else:
                if stop_loss not in strategies_results[s]:
                    strategies_results[s][stop_loss] = [s_data]
                else:
                    strategies_results[s][stop_loss].append(s_data)


def get_files_for_analysis():

    try:

        possible_files = []
        for f in os.listdir("./data"):
            possible_files.append(f)

        possible_files.sort()

        print("\nPossible data files:")
        for p_f in possible_files:

            print(p_f)

        files = []

        input_data_files = input("\nData files: ")

        if path.exists(input_data_files):
            files.append(input_data_files)
        else:
            for i in range(1, int(input_data_files) + 1, 1):
                if path.exists('./data/' + str(i) + '.csv'):
                    files.append('./data/' + str(i) + '.csv')
                else:
                    break

        print("\nFiles choosen:")
        print(files)
        return files

    except:

        print("File not found")
        exit()


def get_strategies():

    try:

        strategies = []
        possible_strategies = ['bollinger', 'keltner', 'x13']

        print("\nPossible strategies:")
        for i, p_s in enumerate(possible_strategies):

            print(i, "-", p_s)

        input_strategies = input("\nStrategies: ")

        input_strategies_arr = input_strategies.split(" ")

        for s in input_strategies_arr:
            strategies.append(possible_strategies[int(s)])

        print("\nStrategies choosen:")
        print(strategies)
        return strategies

    except:

        print("Strategie not found")
        exit()


def write_header(f, files_for_analysis):

    now = datetime.now().strftime("%b %d %Y %H:%M:%S")
    f.write(now + "\n")

    for analized_file_i, analized_file in enumerate(files_for_analysis):
        f.write(analized_file + "\n")


def run_analysis():

    files_for_analysis = get_files_for_analysis()

    strategies = get_strategies()

    f = open("./results.txt", "w")
    write_header(f, files_for_analysis)

    strategies_results = {}
    filtered_strategies_results = {} 
    combined_wait_strategies_results = {}
    filtered_combined_wait_strategies_results = {}

    files_data = None

    for analized_file_i, analized_file in enumerate(files_for_analysis):

        file_data = pd.read_csv(analized_file)
        files_data = append_files_data(files_data, file_data)

        get_strategies_results(file_data, strategies, strategies_results)
        get_combined_wait_strategies_results(analized_file_i, strategies, strategies_results, combined_wait_strategies_results)
        
    filter_strategies_results(combined_wait_strategies_results, filtered_combined_wait_strategies_results)
    filter_strategies_results(strategies_results, filtered_strategies_results)

    merged_filtered_strategies_results = merge_strategies_results(filtered_strategies_results)
    merged_filtered_combined_wait_strategies_results = merge_strategies_results(filtered_combined_wait_strategies_results)
    
    write_columns(f, strategies_results)
    write_results(f, merged_filtered_strategies_results)
    write_results(f, merged_filtered_combined_wait_strategies_results)
    
    plot_data(files_data, merged_filtered_strategies_results)
    plot_data(files_data, merged_filtered_combined_wait_strategies_results)

run_analysis()
