#C:\local\python\27\venv\Scripts\python.exe C:\local\python\27\hockeyscraper\main.py
from lib.HockeyRefBoxscore import HockeyRefBoxParser
from lib.SQ3Reader import SQ3Reader
import pdb
import time

def getColumnStr(fieldList):
    mycolumns = ""
    mylen = len(fieldList)
    for field in fieldList[:-1]:
        mycolumns = mycolumns + field + ","
    mycolumns = mycolumns + fieldList[mylen-1]
    return mycolumns

def insertPlayerStat(sq3reader, team, boxscore, playerData, columnnstr, valuestr):
    #print "Inserting data..."
    myQuery = """INSERT INTO boxscore_data
    (%(columns)s)
    VALUES
    (%(vals)s)""" % {
    'columns':'boxscore,team,'+columnnstr,
    'vals':unicode(boxscore['id'])+",'"+team+"',"+valuestr
    }
    sq3reader.executeQuery(myQuery)
    #print "Done."

def insertStats(sq3reader, team, teamData, myfields):
    print "Inserting stats with player count:"+unicode(len(teamData))+"..."
    for playerData in teamData:
        myvalues = ""
        mylen = len(myfields)
        for field in myfields[:-1]:
            fieldValue = unicode(playerData[field])
            if field == "player" or field == "shot_pct":
                myvalues = myvalues + "'" + fieldValue.replace('\'', '\'\'') + "',"
            else:
                myvalues = myvalues + fieldValue + ","
        fieldValue = unicode(playerData[myfields[mylen-1]])
        myvalues = myvalues + "'" + fieldValue + "'" #last value is time_on_ice
        insertPlayerStat(sq3reader, team, boxscore, playerData, mycolumns, unicode(myvalues))
    print "Done."

def updateGameFlag(sq3reader, id):
    myQuery = "UPDATE boxscore SET isparsed='yes' WHERE id="+unicode(id)
    sq3reader.executeQuery(myQuery)

#------------------------- MAIN ----------------------------------
myfields = ['ranker','player','goals','assists','points','plus_minus','pen_min','goals_ev','goals_pp','goals_sh','goals_gw','assists_ev','assists_pp','assists_sh','shots','shot_pct','shifts','time_on_ice']
mycolumns = getColumnStr(myfields)
sq3reader = SQ3Reader('db/boxscores.db', {'logging':'on'})
print "Find all games not parsed..."
boxscores = sq3reader.executeQueryDict("SELECT * FROM boxscore WHERE isparsed='no' AND link!=''")
print "Found "+unicode(len(boxscores))+" games"
for boxscore in boxscores:
    team1 = boxscore['hteamstr']
    team2 = boxscore['vteamstr']
    htmlFile = boxscore['link'].split('/')[4]
    print "Adding game: "+team2+" at "+team1+" "+htmlFile+"..."
    #print htmlFile
    myHRParser = HockeyRefBoxParser(htmlFile, team1, team2, {'logging':'on'})
    #print myHRParser
    hData = myHRParser.getData("home")
    vData = myHRParser.getData("visit")
    print "Adding home team..."
    insertStats(sq3reader, team1, hData, myfields)
    print "Adding visitor team..."
    insertStats(sq3reader, team2, vData, myfields)
    print "Update parsed flag..."
    updateGameFlag(sq3reader, boxscore['id'])
    #print "Done. Sleep for 10 sec"
    #time.sleep(10)
sq3reader.close()
