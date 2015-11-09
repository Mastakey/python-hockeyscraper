#C:\local\python\27\venv\Scripts\python.exe C:\local\python\27\hockeyscraper\main.py
from lib.HockeyRefSchedule import HockeyRefSchParser
from lib.SQ3Reader import SQ3Reader
import pdb
import time
myCityDict = {
"Dallas Stars":"DAL",
"San Jose Sharks":"SJS",
"New Jersey Devils":"NJD",
"Colorado Avalanche":"COL",
"Boston Bruins":"BOS",
"St. Louis Blues":"STL",
"New York Rangers":"NYR",
"Carolina Hurricanes":"CAR",
"Los Angeles Kings":"LAK",
"Ottawa Senators":"OTT",
"Calgary Flames":"CGY",
"Winnipeg Jets":"WPG",
"Columbus Blue Jackets":"CBJ",
"Chicago Blackhawks":"CHI",
"Florida Panthers":"FLA",
"Anaheim Ducks":"ANA",
"Buffalo Sabres":"BUF",
"Montreal Canadiens":"MTL",
"Edmonton Oilers":"EDM",
"Pittsburgh Penguins":"PIT",
"New York Islanders":"NYI",
"Nashville Predators":"NSH",
"Washington Capitals":"WSH",
"Tampa Bay Lightning":"TBL",
"Vancouver Canucks":"VAN",
"Detroit Red Wings":"DET",
"Philadelphia Flyers":"PHI",
"Arizona Coyotes":"ARI",
"Toronto Maple Leafs":"TOR",
"Minnesota Wild":"MIN"
}

def getDateDict(str):
    myDict = {}
    myDict['year']=str[:4]
    myDict['month']=str[4:6]
    myDict['day']=str[6:8]
    return myDict

def insertSQLBoxscore(sq3, gamedate, hteam, vteam, link, season):
    sq3.executeQuery("INSERT INTO boxscore (gamedate, hteamstr, vteamstr, link, isparsed, season) VALUES ('"+gamedate+"', '"+hteam+"', '"+vteam+"', '"+link+"', 'no', '"+season+"')")

def updateSQLBoxscore(sq3, link, myId):
    sq3.executeQuery("UPDATE boxscore SET link='"+link+"', isparsed='no' WHERE id="+str(myId))

def insertBoxscores(schedule, season):
    sq3 = SQ3Reader('db/boxscores.db', {'logging':'on'})
    insertcount = 0
    updatecount = 0
    for s in schedule:
        vteam = myCityDict.get(s['vteam'], "none")
        hteam = myCityDict.get(s['hteam'], "none")
        htmlFile = ''
        link = ''
        if s['link'] != '':
            htmlFile = s['link'].split("/")[2]
            link = "http://www.hockey-reference.com/boxscores/"+htmlFile
        myDateStr = s['date']
        results = sq3.executeQueryDict("SELECT id, link from boxscore WHERE gamedate='"+myDateStr+"' AND hteamstr='"+hteam+"' AND vteamstr='"+vteam+"'")
        if len(results) > 0:
            #game already exists
            myId = results[0]['id']
            myLink = results[0]['link']
            if myLink != link:
                updateSQLBoxscore(sq3, link, myId)
                updatecount += 1
        else:
            #game doesn't exist
            insertSQLBoxscore(sq3, myDateStr, hteam, vteam, link, season)
            insertcount += 1

    print "Added: "+str(insertcount)+" rows"
    print "Updated: "+str(updatecount)+" rows"

#------------------------- MAIN ----------------------------------
myHRParser = HockeyRefSchParser('http://www.hockey-reference.com/leagues/NHL_2016_games.html', {'logging':'on'})
schedule = myHRParser.getSchedule()
insertBoxscores(schedule, '2016')
#vTeam = myCityDict.get(schedule[1]['vteam'], "none")
#hTeam = myCityDict.get(schedule[1]['hteam'], "none")
#gameLink = schedule[1]['link']
#print hTeam
#print vTeam
#print gameLink
#htmlFile = gameLink.split("/")[2]
#print htmlFile
#for s in schedule:
#    vTeam = myCityDict.get(s['vteam'], "none")
    #print vTeam

#myDateDict = getDateDict(htmlFile)
#year = myDateDict['year']
#month = myDateDict['month']
#day = myDateDict['day']
#myDateStr = year+"-"+month+"-"+day
#print year+"-"+month+"-"+day
#myHRParser = HockeyRefBoxParser(htmlFile, vTeam, hTeam, {'logging':'on'})

#data dict :
#Rk=1
#Player=Mikael Backlund
#G=0
#A=0
#PTS=0
#+/-=-3
#PIM=2
#EV=0
#PP=0
#SH=0
#GW=0
#EV=0
#PP=0
#SH=0
#S=3
#S%=0.0
#SHFT=27
#TOI=17:46

#hteamData = myHRParser.getData("home")
#vteamData = myHRParser.getData("visitor")
#pdb.set_trace()
#print vteamData[1]['Player']

#link = "http://www.hockey-reference.com/boxscores/"+htmlFile
#conn = sqlite3.connect('db/boxscores.db')
#c = conn.cursor()
#c.execute("INSERT INTO boxscore (gamedate, hteamstr, vteamstr, link) VALUES ('"+myDateStr+"', '"+vTeam+"', '"+hTeam+"', '"+link+"')")
#conn.commit()
#conn.close()
