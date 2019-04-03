#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup
import csv
import os
cwd = os.path.dirname(os.path.realpath(__file__))


ticker = raw_input("Please enter the ticker name: ")
print("Acquring data... This may take up to 20 seconds")

statisticsurl = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker
sustainabilityurl = 'https://finance.yahoo.com/quote/' + ticker + '/sustainability?p=' + ticker

statisticsresponse = requests.get(statisticsurl)
sustainabilityresponse = requests.get(sustainabilityurl)

statisticssoup = BeautifulSoup(statisticsresponse.text, 'html.parser')
sustainabilitysoup = BeautifulSoup(sustainabilityresponse.text, "html.parser")

statistcs_name_box = statisticssoup.find('section', attrs={'data-test': 'qsp-statistics'})
sustainability_name_box = sustainabilitysoup.find('section', attrs={'data-test': 'qsp-sustainability'})


data = statistcs_name_box.text.strip()

index = 0
def getStringInBetween(beforeString, afterString):
    return re.search(beforeString + '(.*)' + afterString, data)


def find_str(s, char):
    global index

    if char in s:
        c = char[0]
        for ch in s[index:]:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index + len(char)

            index += 1

    return -1


def getNumberAfterThisIndex(index, originalString, includesOneLetterAfter = False):
    i = index
    while i - index < 10:
        if originalString[i].isalpha() and originalString[i] != "." and originalString[i] != " " or originalString[i] == "%":
            if not includesOneLetterAfter:
                break
            else:
                includesOneLetterAfter = False
        i += 1

    resultString = originalString[index:i].replace(" ", "")
    # print("Before data is " + data[:5])
    return resultString

def getValueFor(key, includesOneLetterAfter = False, hasSuperScript = False):
    # print(len(strm))
    global index
    index = find_str(data, key)
    if hasSuperScript:
        index += 2
    return getNumberAfterThisIndex(index, data, includesOneLetterAfter=includesOneLetterAfter)

valueDictionary = {"Ticker": ticker}
valueDictionary["Market Capitalization"] = getValueFor("Market Cap (intraday)", includesOneLetterAfter=True, hasSuperScript=True)
valueDictionary["Trailing PE"] = getValueFor("Trailing P/E")
valueDictionary["Forward PE"] = getValueFor("Forward P/E", hasSuperScript=True)
valueDictionary["PEG Ratio (5 yr expected)"] = getValueFor("PEG Ratio (5 yr expected)", hasSuperScript=True)
valueDictionary["Price/Sales (ttm)"] = getValueFor("Price/Sales (ttm)")
valueDictionary["Price/Book (mrq)"] = getValueFor("Price/Book (mrq)")
valueDictionary["Enterprise Value/Revenue"] = getValueFor("Enterprise Value/Revenue", hasSuperScript=True)
valueDictionary["Enterprise Value/EBITDA"] = getValueFor("Enterprise Value/EBITDA", hasSuperScript=True)
valueDictionary["Profit Margin"] = getValueFor("Profit Margin", includesOneLetterAfter=True)
valueDictionary["ROA (ttm)"] = getValueFor("Return on Assets (ttm)", includesOneLetterAfter=True)
valueDictionary["ROE (ttm)"] = getValueFor("Return on Equity (ttm)", includesOneLetterAfter=True)
valueDictionary["Quarterly Revenue Growth (yoy)"] = getValueFor("Quarterly Revenue Growth (yoy)", includesOneLetterAfter=True)
valueDictionary["EBITDA"] = getValueFor("EBITDA", includesOneLetterAfter=True)

if sustainability_name_box == None:
    valueDictionary["ESG Data"] = "Unavailable"
else:
    data = sustainability_name_box.text.strip()


    index = 0
    TotalScore = getValueFor("Total ESG score")[:2]
    valueDictionary["Total ESG Score"] = TotalScore
    index = 0
    TotalPercentile = getValueFor("Total ESG score" + TotalScore) + " percentile"
    valueDictionary["Total ESG Percentile"] = TotalPercentile

    EnvScore = getValueFor("PerformerEnvironment")[:2]
    index = 0
    valueDictionary["Environment Score"] = EnvScore
    EnvPercentile = getValueFor("PerformerEnvironment" + EnvScore) + " percentile"
    valueDictionary["Environment Percentile"] = EnvPercentile

    SocialScore = getValueFor("percentileSocial")[:2]
    index = 0
    valueDictionary["Social Score"] = SocialScore
    SocialPercentile = getValueFor("percentileSocial" + SocialScore) + " percentile"
    valueDictionary["Social Percentile"] = SocialPercentile

    GovScore = getValueFor("percentileGovernance")[:2]
    index = 0
    valueDictionary["Governmental Score"] = GovScore
    GovPercentile = getValueFor("percentileGovernance" + GovScore) + " percentile"
    valueDictionary["Governmental Percentile"] = GovPercentile

with open(cwd + "/" + ticker + ' Data.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for key in valueDictionary:
        filewriter.writerow([key, valueDictionary[key]])


print("All Done")