#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import ExcelWriter
import time
import sys
import numpy as np
import threading
import random
import eventlet
eventlet.monkey_patch()
from random import seed
from random import randint
seed(1)
maxToleranceForProxy = 20
start = time.time()
listOfUnsearchableTickers = []
researchedETFs = {
    'Ticker': [],
    'POverall': [],
    'Risk200': [],
    'Risk50': [],
    'Beta': [],
    'ROverall': [],
    'ESG': [],
    'ER': [],
    'Score': []
}


ip = "-1"
proxiesDatabase = ['-1', '165.22.57.60:8888', '46.101.16.157:3128', '165.22.57.60:8888', '165.22.57.60:8888', '-2', '103.206.246.178:8080', '125.26.109.114:61005', '103.73.224.5:37854', '142.93.92.215:3128', '-3', '46.101.21.11:3128', '165.227.33.185:3128', '134.209.21.13:3128', '217.12.222.210:53281', '-4', '1.20.100.93:34926', '77.77.17.48:58528', '79.106.224.231:51254', '134.209.21.13:3128', '-5', '165.22.57.60:8888', '89.109.14.179:48045', '165.22.57.60:8888', '165.22.57.60:8888', '-6', '46.101.16.157:3128', '103.206.246.178:8080', '91.192.4.26:8080', '142.93.92.215:3128', '202.84.77.78:60322', '-7', '165.227.33.185:3128', '217.12.222.210:53281', '103.17.37.85:8080', '182.52.74.76:34084', '-8', '43.252.73.98:53557', '182.52.74.76:34084', '46.254.217.54:53281']


proxiesDatabase += ['91.192.4.26:8080',
           '1.20.100.93:34926',
           '176.241.94.210:33391',
           '103.84.36.130:8080', # bangladesh
           '46.101.21.11:3128', # UK
           '134.209.190.141:3128',
            '-1',
           '103.206.246.178:8080', # Indonesia
           '142.93.92.215:3128',
           '134.209.21.13:3128', # UK
           '165.22.57.60:8888', #CA
           '103.17.37.85:8080',
           "79.106.224.231:51254",
            '-1',
           "170.210.236.1:38828",
           "103.17.37.85:8080",
           "144.48.109.161:8080",
           "103.84.36.130:8080",
           "103.204.82.13:60830",
           "103.239.254.70:61967",
           "103.73.224.5:37854",
           '-1',
            "181.188.187.141:39755",
           "177.23.104.38:60359",
           "177.91.127.32:60523",
           "187.111.90.89:53281",
           "45.4.183.88:53281",
           "187.111.192.146:42592",
           '-1',
            "186.227.67.143:42813",
           "143.107.44.122:80",
           "93.152.176.222:50470",
           "77.77.17.48:58528",
           "116.212.152.192:39377",
           '-1',
            "103.216.48.81:8080",
           "202.84.77.78:60322",
           "116.212.150.7:38132",
           "142.93.148.232:3128",
           "165.227.33.185:3128",
           "200.35.56.89:33310",
           "46.183.56.107:49725",
           "217.30.73.152:38039",
           '-1',
            "95.47.116.128:54904",
           "103.53.110.55:44164",
           "45.116.114.30:31658",
           "123.63.54.229:55207",
           "36.66.43.27:8080",
           "36.67.27.189:59513",
           "202.159.118.210:53873",
           '-1',
            "36.90.150.85:8080",
           "101.255.124.5:47105",
           "202.162.222.154:60990",
           "43.252.73.98:53557",
           "187.155.246.224:3128",
           "103.235.199.93:47374",
           "110.34.39.58:8080",
           '-1',
            "85.28.142.142:41950",
           "188.187.200.36:38778",
           "195.211.101.163:443",
           "46.254.217.54:53281",
           "195.191.183.169:47238",
           "89.109.14.179:48045",
           "62.76.5.157:30683",
           '-1',
            "194.114.129.131:60614",
           "95.181.37.114:43384",
           "91.219.25.173:44899",
           "68.183.236.254:3128",
           "165.22.57.60:8888",
           "1.20.100.93:34926",
           "182.52.74.76:34084",
           '-1',
            "125.26.109.114:61005",
           "217.12.222.210:53281",
           "195.182.22.178:49253",
           "195.69.221.198:38701",
           '-1',
            "176.37.50.238:50650",
           "134.209.21.13:3128",
           "46.101.16.157:3128",
           "104.236.54.196:8080",
           "155.138.234.101:8080"
           ]

proxiesLibrary = {}
for proxy in proxiesDatabase:
    proxiesLibrary[proxy] = 0

def get_random_ua():
    random_ua = ''
    ua_file = 'ua_file.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

def format(s):
    return s.replace("\n", "").replace("\t", "").replace("%", "").replace(",", "").strip()

def findFromSoup(soup, tag, attribute, val, index=0, formatted=True):
    v = soup.find_all(tag, {attribute: val})
    if len(v) == 0:
        return None
    else:
        v = v[index].getText()
        if formatted:
            v = format(v)

        return v

def proxyPenalty(proxy):
    if len(proxiesDatabase) <= 25:
        return

    if proxy not in proxiesDatabase:
        if proxy not in proxiesLibrary.keys():
            pass
        else:
            proxiesLibrary.pop(proxy)
        return

    if proxy not in proxiesLibrary.keys():
        while proxy in proxiesDatabase:
            proxiesDatabase.pop(proxiesDatabase.index(proxy))


    global maxToleranceForProxy

    proxiesLibrary[proxy] += 1
    if proxiesLibrary[proxy] > maxToleranceForProxy:
        print(f"Max tolernace reached for {proxy}")
        proxiesLibrary.pop(proxy)
        while proxy in proxiesDatabase:
            proxiesDatabase.pop(proxiesDatabase.index(proxy))

def proxyReward(proxy):
    if len(proxiesDatabase) <= 25:
        return

    if proxy not in proxiesLibrary.keys():
        proxiesLibrary[proxy] = maxToleranceForProxy / 2
    else:
        proxiesLibrary[proxy] -= 5

    if proxiesDatabase.count(proxy) > 5:
        return

    proxiesDatabase.append(proxy)



def getETF(ETFName, unsearchable, researched, weights, retry=False, proxy=proxiesDatabase[0], queue=0):
    global start
    try:
        user_agent = get_random_ua()
        referer = "https://google.com"
        headers = {
            'user-agent': user_agent,
            'referrer': referer,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Pragma': 'no-cache',
        }

        etfdburl = 'http://etfdb.com/etf/' + ETFName + '/'
        with eventlet.Timeout(10):
            if proxy in (str(f) for f in [-1, -2, -3, -4, -5, -6, -7, -8]):
                etfdbresponse = requests.get(etfdburl, headers=headers)
            else:
                etfdbresponse = requests.get(etfdburl, headers=headers, proxies={"http": proxy, "https": proxy})

        etfdbsoup = BeautifulSoup(etfdbresponse.text, 'html.parser')
        if etfdbresponse.status_code != 200 or etfdbsoup.find("title").getText().find("Page Not Found") != -1:
            proxyPenalty(proxy)
            return getETF(ETFName, unsearchable, researched, weights, retry=True, proxy=random.choice(proxiesDatabase), queue=queue)
    except eventlet.timeout.Timeout:
        proxyPenalty(proxy)
        return getETF(ETFName, unsearchable, researched, weights, retry=True, proxy=random.choice(proxiesDatabase), queue=queue)
    except:
        proxyPenalty(proxy)
        return getETF(ETFName, unsearchable, researched, weights, retry=True, proxy=random.choice(proxiesDatabase), queue=queue)

    try:

        # ESG
        esgScore = float(findFromSoup(etfdbsoup, "div", "class", "score-container", index=1))
        researched['ESG'].append(esgScore)

    except:
        unsearchable.append(ETFName)
        return proxy



    try:
        performanceSection = etfdbsoup.find("div", {"id": "performance"})
        eachValClasses = performanceSection.find_all("div", {"class": "col-md-6"})[1:]
        indices = ('4WR', '13WR', '26WR', 'YTDR', '1YrR', '3YrR', '5YrR')
        totalRScore = 0
        performanceWeightsDict = {k: weights[k] for k in indices if k in weights}
        totalWeight = sum(performanceWeightsDict.values())

        for index, eachValClass in enumerate(eachValClasses):
            curR = indices[index]
            if eachValClass.find("span", {"class": "relative-metric-bubble-name"}) != None:
                totalWeight -= performanceWeightsDict.pop(curR)
            else:
                xtraScore = float(findFromSoup(eachValClass, "span", "class", "relative-metric-bubble-data", index=0)) * \
                            performanceWeightsDict[curR]
                totalRScore += xtraScore

        if totalWeight == 0:
            compositePerformanceScore = 0
        else:
            compositePerformanceScore = totalRScore / totalWeight

        # Risk

        riskSection = etfdbsoup.find("div", {"id": "technicals-collapse"})
        riskInfos = riskSection.find_all("div", {"class": "col-md-6"})
        riskWeight = weights["Risk200"] + weights["Risk50"]
        # Risk 50
        totalRiskScore = 0
        risk50Sec = findFromSoup(riskInfos[2], "span", "class", "relative-metric-bubble-data")
        if risk50Sec == None:
            risk50Sec = 0
            riskWeight -= weights["Risk50"]
        else:
            risk50Sec = float(risk50Sec)
            totalRiskScore += risk50Sec * weights["Risk50"]

        risk200Sec = findFromSoup(riskInfos[3], "span", "class", "relative-metric-bubble-data")
        if risk200Sec == None:
            risk200Sec = 0
            riskWeight -= weights["Risk200"]
        else:
            risk200Sec = float(risk200Sec)
            totalRiskScore += risk200Sec * weights["Risk200"]

        beta = findFromSoup(riskInfos[4], "span", "class", "relative-metric-bubble-data")
        if beta == None:
            beta = 0
        else:
            beta = float(beta)
        if riskWeight == 0:
            compositeRScore = 0
        else:
            compositeRScore = totalRiskScore / riskWeight

        # Expense Ratio

        profileSection = etfdbsoup.find("div", {"class": "col-md-8"})
        vitalsSection = profileSection.find("div", {"class": "col-sm-6"})
        expenseRatioIndex = (vitalsSection.find_all("span"))
        titles = []
        for eachTag in expenseRatioIndex:
            titles.append(eachTag.getText())

        expenseRatioIndex = (titles.index("Expense Ratio:")) / 2
        expenseRatio = float(findFromSoup(vitalsSection, "span", "class", "pull-right", index=int(expenseRatioIndex)))
        # Liquidity
        sec = etfdbsoup.find_all("div", {"class": "panel-body"})[1]
        tradingDataSec = sec.find_all("div", {"class": "col-sm-6"})[1] # Liquidity Data
        # Store data in df
        researched['Ticker'].append(ETFName)
        researched['POverall'].append(compositePerformanceScore)
        researched['Risk200'].append(float(risk200Sec))
        researched['Risk50'].append(float(risk50Sec))
        researched['ROverall'].append(compositeRScore)

        researched['ER'].append(expenseRatio)
        researched['Beta'].append(beta)
        researched['Score'].append(0)




    except Exception as e:
        print(f"Error here {ETFName} with message {e}")
        unsearchable.append(ETFName)

    return proxy


print("Welcome to investment recommender. Ensure that ETFList.csv and weighting.csv are in the same directory as this program.")
input("If you've already done so, press ENTER to begin the ranking of those ETFs: ")

weightingRawConfig = pd.read_csv("weighting.csv", index_col="Index")
weightingUnprocessed = weightingRawConfig["Weight (from 0 to 100)"].to_dict()
preferableCondition = weightingRawConfig["Preferable Condition"].to_dict()
indices = ('4WR', '13WR', '26WR', 'YTDR', '1YrR', '3YrR', '5YrR', 'Risk200', 'Risk50')

weightingProcessed = dict(weightingUnprocessed)
for eachIndex in indices:
    weightingProcessed.pop(eachIndex)
    preferableCondition.pop(eachIndex)

weightingProcessed = {k: weightingUnprocessed[k] for k in indices if k in weightingUnprocessed}
performanceWeightsDict = {k: weightingUnprocessed[k] for k in indices if k in weightingUnprocessed}
totalWeight = sum(np.array(list(performanceWeightsDict.values())) ** 7)
calculatedWeight = dict(weightingUnprocessed)
for eachIndex in indices:
    calculatedWeight.pop(eachIndex)

# Get Data
listOfETFs = pd.read_csv("ETFList.csv", index_col="Symbol").index.values
nOfETFs = len(listOfETFs)

print("Initialization Completed. Downloading Data.")

j = 0
sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))

# Split into 50 partitions
numberOfPetitions = 25
fractionofLen = int(nOfETFs / numberOfPetitions)
petitions = []
for i in range(numberOfPetitions):
    petitions.append(listOfETFs[i*fractionofLen:(i+1)*fractionofLen])

def searching(partition, tn):
    global listOfUnsearchableTickers
    global weightingUnprocessed
    global researchedETFs
    proxy = random.choice(proxiesDatabase)
    for index, item in enumerate(partition):
        proxy = getETF(item, listOfUnsearchableTickers, researchedETFs, weightingUnprocessed, queue=tn, proxy=proxy)
        time.sleep(randint(1, 3))
        i = len(researchedETFs["Ticker"]) + len(listOfUnsearchableTickers) - 1
        sys.stdout.write('\r')
        # the exact output you're looking for:
        avgSpeed = 0
        if i != -1:
            avgSpeed = (time.time() - start) / (i+1)

        j = (i + 1) / nOfETFs
        # the exact output you're looking for:
        sys.stdout.write(f"[%-20s] %d%% | {i + 1}/{nOfETFs} | Currently on {listOfETFs[i]} | Average Speed: %.2fs/ETF | Estimated Time Remaining: %.2fs | Unresearchable Count: {len(listOfUnsearchableTickers)} | Proxies Len: {len(proxiesDatabase)}" % ('=' * int(20 * j), 100 * j, avgSpeed, avgSpeed * (nOfETFs - 1 - i)))

        sys.stdout.flush()

if __name__ == "__main__":
    # creating thread
    # print("Creating thread")
    threads = []
    for index, petition in enumerate(petitions):
         threads.append(threading.Thread(target=searching, args=(petition, index)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # both threads completely executed
    j = 1
    i = len(researchedETFs["Ticker"]) + len(listOfUnsearchableTickers) - 1
    avgSpeed = (time.time() - start) / (i + 1)
    # the exact output you're looking for:
    sys.stdout.write('\r')
    sys.stdout.write(f"[%-20s] %d%% | {i + 1}/{nOfETFs} | Currently on {listOfETFs[i]} | Average Speed: %.2fs/ETF | Estimated Time Remaining: %.2fs | Unresearchable Count: {len(listOfUnsearchableTickers)}" % ('=' * int(20 * j), 100 * j, avgSpeed, avgSpeed * (nOfETFs - 1 - i)))

    sys.stdout.flush()
    print()
    print("Done!")







print("\n\n")

df = pd.DataFrame(researchedETFs)
mdf = pd.DataFrame({"Ticker": listOfUnsearchableTickers})
print(df.info())
# Rank and Assign Score
for key, value in calculatedWeight.items():
    higherBetter = (preferableCondition[key] == "HIGH")
    df = df.sort_values(key, ascending=higherBetter).reset_index(drop=True)
    df["Score"] += df.index * value


df = df.sort_values("Score", ascending=False).reset_index(drop=True)
df.columns = ['Ticker', 'Composite Performance Score', '200 Days Volatility', '50 Days Volatility', 'Beta', 'Volatility Composite Score', 'ESG Global Percentile', 'Expense Ratio', 'Score']
df = df.set_index('Ticker')
writer = ExcelWriter('ETF Ranking.xlsx')
df.to_excel(writer,'Researched and Ranked')
mdf = mdf.set_index('Ticker')
print("The following ETFs could not be researched and ranked because they do not have ESG data")
print(mdf.index.values)
mdf.to_excel(writer,'Unresearchable')
writer.save()

print("File saved as 'ETF Ranking.xlsx' in your current directory")
end = time.time()
print(f"Total time taken: %.2fs" % (end - start))
print("Success")