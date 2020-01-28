import requests
import random
from lxml import html
import time

import pandas

import random

from datetime import datetime

CANDLE_TIME_S = 60
ADVFN_ID = "quoteElementPiece23"

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]


def get_request(url):

    try:
        headers = {
            'User-Agent': random.choice(user_agent_list),
            'cookie': '__cfduid=dc624d786bbf2c173920b79dd4cc8a2db1573479180; ADVFNUID=ec16820956c1ce53318d33092f9e8b59273de8d; username=flavio342; AFNTZ=America%2FSao_Paulo; recent_stocks=BOV%5EPETR4%2CBOV%5EWEGE3%2CBMF%5EWINZ19%2CBOV%5EMGLU3%2CFT%5EWINZL; ref=223; SID=12e76c13023ffba8dc747176fa31f70e; __zlcmid=vDig8MMtErXzEZ; MKTA_THEOASISID=5df76c68ca135'
        }
        page = requests.get(url, headers=headers, timeout=5)
        return page
    except Exception as e:
        return None


def craw_page(url, paths):

    page = get_request(url)
    #print(page.content)
    if not page:
        return None

    doc = html.fromstring(page.content)

    results = {}
    for key in paths:

        XPATH = paths[key]
        RAW = []
        if XPATH:
            RAW = doc.xpath(XPATH)
        results[key] = RAW

    return results


def reset_candle():

    return {
        "date_time": None,
        "open": None,
        "high": 0,
        "low": 100000000000,
        "close": None,
    }


def craw_advfn():

    paths = {
        'price': '//span[contains(@id,"' + ADVFN_ID + '")]//text()'
    }

    data = {
        "date_time": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
    }

    oldtime = time.time()

    now = datetime.now()
    old_minute = str(now).split(" ")[1].split(":")[1].split(".")[0]

    candle = reset_candle()

    price_f = open("current_price", "w")
    price_f.close()

    while True:
        results = craw_page(
            "https://br.advfn.com/bolsa-de-valores/bmf/WING20/cotacao", paths)

        try:
            print(float(results['price'][0].split(",")[0]) * 1000)
            price = float(results['price'][0].split(",")[0]) * 1000
        except:
            print("Ops")
            continue

        price_f = open("current_price", "a")
        price_f.write(str(price) + "\n")
        price_f.close()

        if candle['open'] == None:
            candle['open'] = price

        if price > candle['high']:
            candle['high'] = price

        if price < candle['low']:
            candle['low'] = price

        now = datetime.now()
        minute = str(now).split(" ")[1].split(":")[1].split(".")[0]
        current_time = time.time()

        if current_time - oldtime > CANDLE_TIME_S or (int(minute) - int(old_minute)) * CANDLE_TIME_S >= CANDLE_TIME_S:

            old_minute = minute
            oldtime = current_time

            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            candle['date_time'] = dt_string

            candle['close'] = price

            for k in data:
                data[k].append(candle[k])

            candle = reset_candle()

            print(pandas.DataFrame(data))
            pandas.DataFrame(data).to_csv('data.csv', mode='w', header=True)


def prepare_to_craw():
    its_time = False
    while not its_time:
        now = datetime.now()
        seconds = str(now).split(" ")[1].split(":")[2].split(".")[0]
        if int(seconds) == 0:
            its_time = True
            craw_advfn()

prepare_to_craw()
