import time

def copy_data(seconds):

    copy_f = open("copy_data.csv", "w")
    copy_f.close()

    data_f = open("./data/15.csv", "r")

    line = data_f.readline()

    while line != '':
        print(line)
        copy_f = open("copy_data.csv", "a")
        copy_f.write(line)
        copy_f.close()
        time.sleep(seconds)
        line = data_f.readline()

copy_data(1)