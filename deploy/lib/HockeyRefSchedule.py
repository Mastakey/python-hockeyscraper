#>C:\local\python\27\venv\Scripts\python.exe C:\local\python\27\hockeyscraper\connectHockeyRef.py
from lxml import html, etree
from pprint import pprint
from bs4 import BeautifulSoup
import pdb
import requests

class HockeyRefSchParser(object):
    def __init__(self, url, configDict):
        self.url = url
        #self.htmlFile = htmlFile
        self.configDict = configDict
        self.config_logging = configDict['logging'] #on/off
        self.rawData = self.getRawData(self.url)
        self.prettyData = self.getPrettyData(self.rawData)
        self.logToFile("Schedule", "2015", self.prettyData, "w")
        self.schedule = self.parseSchedule(self.prettyData)
        #hteam

    def getSchedule(self):
        return self.schedule

    def logToFile(self, fileName, name, str, method):
        if self.config_logging == "on":
            f = open("out/"+name+"_"+fileName, method)
            f.write(str.encode('utf8'))

    def getRawData(self, url):
        page = requests.get(url)
        tree = html.fromstring(page.text)
        #print page.text.encode('ascii', 'ignore')
        myTable = tree.xpath('//*[@id="games"]')
        #pdb.set_trace()
        myTable_str = html.tostring(myTable[0])
        return myTable_str

    def getPrettyData(self, rawData):
        mySoup = BeautifulSoup(rawData, 'html.parser')
        mySoupPretty = mySoup.prettify()
        return mySoupPretty

    def parseSchedule(self, prettyData):
        #returns a list of schedules
        schedules = []#list of dict
        table = etree.XML(prettyData)
        tbody_rows = table.xpath("tbody")[0].findall("tr")
        #self.logToFile("Schedule", "Data", "", "w") #Clear file
        for row in tbody_rows:
            sch_dict = {}
            count = 0
            #self.logToFile(str(count), "Game ", html.tostring(row), "a")
            tbody_values = row.xpath("td")
            for value in tbody_values:
                myValue = ""
                myLink = ""
                #//*[@id="games"]/tbody/tr[121]/td[1]
                if value.text.strip() == "":
                    if value.xpath("a"):
                        myValue = value.xpath("a")[0].text.strip()
                        myLink = value.xpath("a")[0].attrib['href']#/boxscores/yyyyxxx.html
                        #pdb.set_trace()
                else:
                    myValue = value.text.strip()
                #print myValue
                if count == 0:
                    sch_dict['link']=myLink
                    sch_dict['date']=myValue
                elif count == 1:
                    sch_dict['vteam']=myValue
                elif count == 3:
                    sch_dict['hteam']=myValue
                count = count + 1
                #pdb.set_trace()
            #end for
            schedules.append(sch_dict)
        return schedules

def testParseSchedule():
    myHRParser = HockeyRefSchParser({'logging':'on'})
    schedule = myHRParser.getSchedule()
    #pdb.set_trace()
    mySet = set()
    for sch in schedule:
        print sch['vteam']
        print sch['hteam']
        print sch['link']
        mySet = mySet | {sch['vteam']}

    for s in mySet:
        print s


    #for sch in schedule:
    #    print sch['link']
    #player_stats = myHRParser.parseTable(team_table_pretty)
    #myHRParser.printPlayerStats(player_stats)

#testParseSchedule()
