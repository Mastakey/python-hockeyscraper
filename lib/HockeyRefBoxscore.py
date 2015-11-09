from lxml import html, etree
from pprint import pprint
from bs4 import BeautifulSoup
import os
import pdb
import requests

class HockeyRefBoxParser(object):
    def __init__(self, htmlFile, hteam, vteam, configDict):
        self.url = 'http://www.hockey-reference.com/boxscores/'+htmlFile
        self.gameStr = htmlFile.split(".")[0]
        self.htmlFile = htmlFile
        self.configDict = configDict
        self.config_logging = configDict['logging'] #on/off
        #hteam
        self.hteam_data_raw = self.getRawData(hteam, self.url)
        self.hteam_data_pretty = self.getPrettyData(self.hteam_data_raw)
        self.hteam_headers = self.getTeamHeader(hteam, self.hteam_data_pretty)
        self.hteam_data = self.getTeamData(hteam, self.hteam_data_pretty, self.hteam_headers)
        #vteam
        self.vteam_data_raw = self.getRawData(vteam, self.url)
        self.vteam_data_pretty = self.getPrettyData(self.vteam_data_raw)
        self.vteam_headers = self.getTeamHeader(vteam, self.vteam_data_pretty)
        self.vteam_data = self.getTeamData(vteam, self.vteam_data_pretty, self.vteam_headers)

    def getData(self, team):
        if (team == "home"):
            return self.hteam_data
        else:
            return self.vteam_data

    def logToFile(self, fileName, name, str, method):
        if self.config_logging == "on":
            if not os.path.exists("out/"+self.gameStr):
                os.makedirs("out/"+self.gameStr)
            if not os.path.exists("out/"+self.gameStr+"/"+name):
                os.makedirs("out/"+self.gameStr+"/"+name)
            f = open("out/"+self.gameStr+"/"+name+"/"+fileName, method)
            f.write(str.encode('utf8'))

    def getRawData(self, team, url):
        page = requests.get(url)
        tree = html.fromstring(page.text)
        #print page.text.encode('ascii', 'ignore')
        team = tree.xpath('//*[@id="'+team+'_skaters"]')
        #pdb.set_trace()
        team_table = html.tostring(team[0])
        return team_table

    def getPrettyData(self, rawData):
        team_table_soup = BeautifulSoup(rawData, 'html.parser')
        team_table_pretty = team_table_soup.prettify()
        return team_table_pretty

    def getTeamHeader(self, team, tableHtml):
        table = etree.XML(tableHtml)
        #find thead rows
        thead_rows = table.xpath("thead")[0].findall("tr")
        count = 0
        #print type(thead_rows)
        stats_list = [] #list
        for row in thead_rows:
            #we only care about the second tr row
            if count == 1:
                self.logToFile("HTML_DATA_Headers.data", team, html.tostring(row), "w")
                thead_values = row.xpath("th")
                for value in thead_values:
                    stat_fullname = value.attrib['data-stat'] #attrib is a dict
                    stat_name = value.text.strip()
                    #stats_list.append(stat_name)
                    stats_list.append(stat_fullname)
            count = count + 1
        return stats_list

    def getTeamData(self, team, tableHtml, stats_list):
        #find tbody rows
        player_stat_list = [] #list of dict
        table = etree.XML(tableHtml)
        tbody_rows = table.xpath("tbody")[0].findall("tr")
        self.logToFile("HTML_Data_Players.data", team, "", "w") #Clear file
        self.logToFile("Players.out", team, "", "w") #Clear file
        for row in tbody_rows:
            player_dict = {}
            self.logToFile("HTML_Data_Players.data", team, html.tostring(row), "a")
            tbody_values = row.xpath("td")
            count = 0
            for value in tbody_values:
                myValue = ""
                if value.text.strip() == "":
                    if value.xpath("a"):
                        myValue = value.xpath("a")[0].text.strip()
                else:
                    myValue = value.text.strip()
                #end if
                player_dict[stats_list[count]] = myValue
                self.logToFile("Players.out", team, stats_list[count]+"="+myValue+"\n" , "a")
                count = count + 1
            #end for
            player_stat_list.append(player_dict)
        #end for
        return player_stat_list

    def printPlayerStats(self, playerStats):
        for player in playerStats:
            print player['Player']

def testParseTable():
    htmlFile = "201510190NYR.html"
    team1 = "SJS"
    team2 = "NYR"
    myHRParser = HockeyRefBoxParser(htmlFile, team1, team2, {'logging':'on'})
    #player_stats = myHRParser.parseTable(team_table_pretty)
    #myHRParser.printPlayerStats(player_stats)

#testParseTable()
