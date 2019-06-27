from lxml.html import fromstring
import requests
from itertools import cycle
import traceback
import timeout
import socket


# Function to display hostname and
# IP address
from requests import get
import threading
import pandas as pd
import requests
import eventlet
eventlet.monkey_patch()
import random




proxies = ['91.192.4.26:8080',
           '1.20.100.93:34926',
           '176.241.94.210:33391',
           '103.84.36.130:8080', # bangladesh
           '46.101.21.11:3128', # UK
           '134.209.190.141:3128',
           '103.206.246.178:8080', # Indonesia
           '142.93.92.215:3128',
           '134.209.21.13:3128', # UK
           '165.22.57.60:8888', #CA
           '103.17.37.85:8080',
           "79.106.224.231:51254",
           "170.210.236.1:38828",
           "103.17.37.85:8080",
           "144.48.109.161:8080",
           "103.84.36.130:8080",
           "103.204.82.13:60830",
           "103.239.254.70:61967",
           "103.73.224.5:37854",
           "181.188.187.141:39755",
           "177.23.104.38:60359",
           "177.91.127.32:60523",
           "187.111.90.89:53281",
           "45.4.183.88:53281",
           "187.111.192.146:42592",
           "186.227.67.143:42813",
           "143.107.44.122:80",
           "93.152.176.222:50470",
           "77.77.17.48:58528",
           "116.212.152.192:39377",
           "103.216.48.81:8080",
           "202.84.77.78:60322",
           "116.212.150.7:38132",
           "142.93.148.232:3128",
           "165.227.33.185:3128",
           "200.35.56.89:33310",
           "46.183.56.107:49725",
           "217.30.73.152:38039",
           "95.47.116.128:54904",
           "103.53.110.55:44164",
           "45.116.114.30:31658",
           "123.63.54.229:55207",
           "36.66.43.27:8080",
           "36.67.27.189:59513",
           "202.159.118.210:53873",
           "36.90.150.85:8080",
           "101.255.124.5:47105",
           "202.162.222.154:60990",
           "43.252.73.98:53557",
           "187.155.246.224:3128",
           "103.235.199.93:47374",
           "110.34.39.58:8080",
           "85.28.142.142:41950",
           "188.187.200.36:38778",
           "195.211.101.163:443",
           "46.254.217.54:53281",
           "195.191.183.169:47238",
           "89.109.14.179:48045",
           "62.76.5.157:30683",
           "194.114.129.131:60614",
           "95.181.37.114:43384",
           "91.219.25.173:44899",
           "68.183.236.254:3128",
           "165.22.57.60:8888",
           "1.20.100.93:34926",
           "182.52.74.76:34084",
           "125.26.109.114:61005",
           "217.12.222.210:53281",
           "195.182.22.178:49253",
           "195.69.221.198:38701",
           "176.37.50.238:50650",
           "134.209.21.13:3128",
           "46.101.16.157:3128",
           "104.236.54.196:8080",
           "155.138.234.101:8080"
           ]

bestPerformingProxies = []
uselessProxies = []


numberOfPetitions = 25
fractionofLen = 3
listOfETFs = pd.read_csv("ETFList.csv", index_col="Symbol").index.values
nOfETFs = len(listOfETFs)
url = 'https://etfdb.com/etf/'
petitions = []
for i in range(numberOfPetitions):
    petitions.append(proxies[i*fractionofLen:(i+1)*fractionofLen])

def checkProxy(proxy):
    if len(bestPerformingProxies) >= 20:
        uselessProxies.append(proxy)

    try:
        with eventlet.Timeout(10):
            newURL = url + random.choice(listOfETFs)
            requests.get(newURL, proxies={"http": proxy, "https": proxy})
            bestPerformingProxies.append(proxy)
    except eventlet.timeout.Timeout as e1:
        uselessProxies.append(proxy)
        return
    except Exception as e:
        uselessProxies.append(proxy)
        return


def assessingProxy(mPets):
    global bestPerformingProxies
    global uselessProxies
    for proxy in mPets:
        checkProxy(proxy)

def findProxies():
    global proxies
    returningProxies = []
    # creating thread
    for j in range(0, 3):
        threads = []
        random.shuffle(proxies)
        for index, petition in enumerate(petitions):
             threads.append(threading.Thread(target=assessingProxy, args=(petition, )))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        returningProxies += bestPerformingProxies[:20]

    for l in range(0, int(len(returningProxies) / 6)):
        returningProxies.append('-1')

    return returningProxies
