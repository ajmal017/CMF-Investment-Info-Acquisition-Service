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
from scraps import findProxies
seed(1)
maxToleranceForProxy = 20

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

proxiesDatabase = ['-1', '-1', '46.101.16.157:3128', '103.206.246.178:8080', '195.211.101.163:443', '91.192.4.26:8080', '93.152.176.222:50470', '103.84.36.130:8080', '170.210.236.1:38828', '195.69.221.198:38701', '103.73.224.5:37854', '103.84.36.130:8080', '43.252.73.98:53557', '89.109.14.179:48045', '217.12.222.210:53281', '116.212.150.7:38132', '36.67.27.189:59513', '195.191.183.169:47238', '188.187.200.36:38778', '46.101.16.157:3128', '103.206.246.178:8080', '195.211.101.163:443', '91.192.4.26:8080', '93.152.176.222:50470', '103.84.36.130:8080', '170.210.236.1:38828', '195.69.221.198:38701', '103.73.224.5:37854', '103.84.36.130:8080', '43.252.73.98:53557', '89.109.14.179:48045', '217.12.222.210:53281', '116.212.150.7:38132', '36.67.27.189:59513', '195.191.183.169:47238', '188.187.200.36:38778', '46.101.16.157:3128', '103.206.246.178:8080', '89.109.14.179:48045', '46.101.16.157:3128', '103.206.246.178:8080', '195.211.101.163:443', '91.192.4.26:8080', '93.152.176.222:50470', '103.84.36.130:8080', '170.210.236.1:38828', '195.69.221.198:38701', '103.73.224.5:37854', '103.84.36.130:8080', '43.252.73.98:53557', '89.109.14.179:48045', '217.12.222.210:53281', '116.212.150.7:38132', '36.67.27.189:59513', '195.191.183.169:47238', '188.187.200.36:38778', '46.101.16.157:3128', '103.206.246.178:8080', '89.109.14.179:48045', '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1']

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
            # proxyPenalty(proxy)
            return getETF(ETFName, unsearchable, researched, weights, retry=True, proxy=random.choice(proxiesDatabase), queue=queue)
    except eventlet.timeout.Timeout:
        # proxyPenalty(proxy)
        return getETF(ETFName, unsearchable, researched, weights, retry=True, proxy=random.choice(proxiesDatabase), queue=queue)
    except:
        # proxyPenalty(proxy)
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


def acquireProxies(b):
    global proxiesDatabase
    proxiesDatabase = findProxies()

thread1 = threading.Thread(target=acquireProxies, args=(1,))
thread1.start()

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
start = time.time()
j = 0
sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))

# Split into 50 partitions
numberOfPetitions = 30
fractionofLen = int(nOfETFs / numberOfPetitions)
petitions = []
for i in range(numberOfPetitions):
    petitions.append(listOfETFs[i*fractionofLen:(i+1)*fractionofLen])

def searching(partition, tn):
    global listOfUnsearchableTickers
    global weightingUnprocessed
    global researchedETFs
    proxy = proxiesDatabase[0]
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