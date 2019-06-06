#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup
import csv
import os
cwd = os.path.dirname(os.path.realpath(__file__))

while True:
    ticker = raw_input("Please enter the ticker name: ")
    print("Acquring data... This may take up to 20 seconds")
    ticker = ticker.replace(".", "-")
    statisticsurl = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker
    sustainabilityurl = 'https://finance.yahoo.com/quote/' + ticker + '/sustainability?p=' + ticker

    statisticsresponse = requests.get(statisticsurl)
    sustainabilityresponse = requests.get(sustainabilityurl)

    statisticssoup = BeautifulSoup(statisticsresponse.text, 'html.parser')
    sustainabilitysoup = BeautifulSoup(sustainabilityresponse.text, "html.parser")

    usefulSustain = sustainabilitysoup.find("div", {"class": "smartphone_Mt(20px)", "data-reactid": "14"})
    usefulStats = sustainabilitysoup.find('section', attrs={'data-test': 'qsp-sustainability'})

    statistcs_name_box = statisticssoup.find('section', attrs={'data-test': 'qsp-statistics'})
    sustainability_name_box = sustainabilitysoup.find('section', {'data-test': 'qsp-sustainability'})

    if statistcs_name_box == None or statisticsresponse.status_code != 200:
        print("We cannot search up the symbol you have entered. Please try a different one")
    else:
        break


def findValueWithID(soup, type, id):
    s = soup.find(type, {"data-reactid": str(id)})
    print(s)
    return s.getText()

def findIDFromFinanceSoup(id):
    return findValueWithID(statisticssoup, "td", id)

def findIDFromSustainabilitySoup(type, id):
    return findValueWithID(usefulSustain, type, id)


# s = sustainabilitysoup.find("div", {"class": "smartphone_Mt(20px)", "data-reactid": "14"})
# l = s.find("div", {"data-reactid": 20})
attributesTuple = ("Ticker", "Market Capitalization", "Trailing PE", "Forward PE", "PEG Ratio (5 yr expected)", "Price/Sales (ttm)", "Price/Book (mrq)", "Enterprise Value/Revenue", "Enterprise Value/EBITDA", "Profit Margin", "ROA (ttm)", "ROE (ttm)", "Quarterly Revenue Growth (yoy)", "EBITDA", "Quarterly Earnings Growth (yoy)")

valueDictionary = {"Ticker": ticker}
valueDictionary["Market Capitalization"] = findIDFromFinanceSoup(19)
valueDictionary["Trailing PE"] = findIDFromFinanceSoup(33)
valueDictionary["Forward PE"] = findIDFromFinanceSoup(40)
valueDictionary["PEG Ratio (5 yr expected)"] = findIDFromFinanceSoup(47)
valueDictionary["Price/Sales (ttm)"] = findIDFromFinanceSoup(54)
valueDictionary["Price/Book (mrq)"] = findIDFromFinanceSoup(61)
valueDictionary["Enterprise Value/Revenue"] = findIDFromFinanceSoup(68)
valueDictionary["Enterprise Value/EBITDA"] = findIDFromFinanceSoup(75)
valueDictionary["Profit Margin"] = findIDFromFinanceSoup(112)
valueDictionary["ROA (ttm)"] = findIDFromFinanceSoup(131)
valueDictionary["ROE (ttm)"] = findIDFromFinanceSoup(138)
valueDictionary["Quarterly Revenue Growth (yoy)"] = findIDFromFinanceSoup(164)
valueDictionary["EBITDA"] = findIDFromFinanceSoup(178)
valueDictionary["Quarterly Earnings Growth (yoy)"] = findIDFromFinanceSoup(199)

if sustainability_name_box == None or sustainabilityresponse.status_code != 200:
    valueDictionary["ESG Data"] = "Unavailable"
    attributesTuple += ("ESG Data",)
else:
    attributesTuple += ("Total ESG Score", "Total ESG Percentile", "Environment Score", "Environment Percentile", "Social Score", "Social Percentile", "Governmental Score", "Governmental Percentile")
    valueDictionary["Total ESG Score"] = findIDFromSustainabilitySoup("div", 20)
    valueDictionary["Total ESG Percentile"] = findIDFromSustainabilitySoup("span", 23)

    valueDictionary["Environment Score"] = findIDFromSustainabilitySoup("div", 35)
    valueDictionary["Environment Percentile"] = findIDFromSustainabilitySoup("span", 38)

    valueDictionary["Social Score"] = findIDFromSustainabilitySoup("div", 45)
    valueDictionary["Social Percentile"] = findIDFromSustainabilitySoup("span", 48)

    valueDictionary["Governmental Score"] = findIDFromSustainabilitySoup("div", 55)
    valueDictionary["Governmental Percentile"] = findIDFromSustainabilitySoup("span", 58)

with open(cwd + "/" + ticker + ' Data.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for key in attributesTuple:
        filewriter.writerow([key, valueDictionary[key]])


print("All Done")