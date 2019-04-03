
valueDictionary = {}
data = "Environment, Social and Governance (ESG) RatingsTotal ESG score8194th percentileLeaderLeaderEnvironment8693rd percentileSocial8394th percentileGovernance7086th percentileESG Performance vs 32 Peer CompaniesNVDAPeersCategory AverageESG PERFORMANCEEnvironment5292Social5288Governance50830100CONTROVERSY LEVEL2Moderate Controversy level4NoneSevereESG data provided by Sustainalytics, Inc.Last updated on 3/2019"


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
index = 0
TotalScore = getValueFor("Total ESG score")[:2]
valueDictionary["Total ESG Score"] = TotalScore
index = 0
TotalPercentile = getValueFor("Total ESG score" + TotalScore) + " percentile"
valueDictionary["Total ESG Percentile"] = TotalPercentile

EnvScore = getValueFor("Environment")[:2]
index = 0
valueDictionary["Environment Score"] = EnvScore
EnvPercentile = getValueFor("Environment" + EnvScore) + " percentile"
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

print("hello")