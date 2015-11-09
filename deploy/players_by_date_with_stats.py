from __future__ import division
from operator import itemgetter
from lib.SQ3Reader import SQ3Reader
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('tmpl', ''))
template = env.get_template('body/players_by_date_with_stats.html')

import pdb
import time
import os
import math

def getDkdata(csv):
    f = open(csv,  'r')
    dk_lines = f.readlines()
    count = 0
    dkdata = []
    #print len(salary_lines)
    for line in dk_lines:
        #ignore header line
        if count > 0:
            mydict = {}
            mycsvlist = line.split(',')
            mydict['position'] = mycsvlist[0].replace("\"", "")
            mydict['player']  = mycsvlist[1].replace("\"", "")
            mydict['salary']  = mycsvlist[2].replace("\"", "")
            #print position
            dkdata.append(mydict)
        count += 1
    return dkdata

def getPlayerSalary(player, dkdata):
    for data in dkdata:
        if player == data['player']:
            return data['salary']

def getPlayerPosition(player, dkdata):
    for data in dkdata:
        if player == data['player']:
            return data['position']

def getSeconds(myStr):
    minutes = int(myStr.split(':')[0])
    seconds = int(myStr.split(':')[1])
    return minutes*60+seconds

def getTimeStr(seconds):
    myMin = int(seconds/60)
    mySec = seconds % 60
    return str(myMin)+':'+str(mySec)

def getPlayerSummaryStats(player, team, player_data):
    player_stats = {}
    GP = 0
    goals = 0
    assists = 0
    points = 0
    shots = 0
    time_on_ice_s = 0
    blocks = 0
    shp = 0
    so_goals = 0
    dk_points = 0
    dk_points_per_min = 0
    dk_sd_sum = 0
    dk_sd = 0
    for data in player_data:
        GP += 1
        goals += data['goals']
        assists += data['assists']
        points += data['points']
        shots += data['shots']
        time_on_ice_s += getSeconds(data['time_on_ice'])
        temp_dk_points = getDkpoints(data['goals'], data['assists'], data['shots'], 0, 0)
        dk_points += temp_dk_points
        dk_sd_sum += temp_dk_points**2

    #player_stats['player'] = player_data['player']
    #player_stats['team'] = player_data['team']
    dk_sd = math.sqrt(dk_sd_sum/GP)
    time_on_ice_s = int(time_on_ice_s/GP)
    fppg = dk_points/GP
    player_stats['player'] = player
    player_stats['team'] = team
    player_stats['GP'] = GP
    player_stats['goals'] = goals
    player_stats['assists'] = assists
    player_stats['points'] = points
    player_stats['shots'] = shots
    player_stats['time_on_ice'] = getTimeStr(time_on_ice_s)
    player_stats['time_on_ice_s'] = time_on_ice_s
    player_stats['blocks'] = blocks
    player_stats['shp'] = shp
    player_stats['so_goals'] = so_goals
    player_stats['dk_points'] = dk_points
    player_stats['fppg'] = fppg
    player_stats['variance'] = dk_sd
    return player_stats

def getPlayersFromTeam(player_list, teamstr):
    team_player_list = []
    for player in player_list:
        if player['team'] == teamstr:
            team_player_list.append({'player':player['player'],'team':player['team']})
    return team_player_list

def getDkpoints(goals, assists, shots, blocks, shp):
    dk_points = 0
    dk_points += goals * 3.0
    dk_points += assists * 2
    dk_points += shots * 0.5
    dk_points += blocks * 0.5
    dk_points += shp * 0.2
    if goals > 2:
        dk_points += 1.2
    return dk_points

def outputToTemplate(mylist, myFile):
    f = open(myFile, "w")
    f.write(template.render(player_stats=mylist))

myYear = '2016' #2015-2016 season
myDate = '2015-10-27' #current date
#GET All players for the year
myPlayers = []
sq3reader = SQ3Reader('db/boxscores.db', {'logging':'on'})
player_list = sq3reader.executeQueryDict("""SELECT distinct d.player, d.team
from boxscore_data d, boxscore b WHERE d.boxscore = b.id
AND b.season='"""+myYear+"""'
""")
#print len(player_list)
boxscores = sq3reader.executeQueryDict("""SELECT id, vteamstr, hteamstr
from boxscore where gamedate='"""+myDate+"""'
""")
#print len(boxscores)
todays_players = []
for boxscore in boxscores:
    #print boxscore['vteamstr']+" VS "+boxscore['hteamstr']
    vteam_players = getPlayersFromTeam(player_list, boxscore['vteamstr'])
    hteam_players = getPlayersFromTeam(player_list, boxscore['hteamstr'])
    #print len(vteam_players)
    todays_players.extend(vteam_players)
    todays_players.extend(hteam_players)
#print len(todays_players)
player_stats = []
center_stats = []
wing_stats = []
defence_stats = []

#DK data
dkdata = getDkdata('input/10272015_DKSalaries.csv')

for p in todays_players:
    player = {}
    playerName = p['player'].replace('\'', '\'\'')
    salary = getPlayerSalary(p['player'], dkdata)
    position = getPlayerPosition(p['player'], dkdata)
    player_data = sq3reader.executeQueryDict("""SELECT d.id, d.boxscore,
    d.team, d.player, d.shots, d.goals, d.assists, d.points,
     d.time_on_ice FROM boxscore_data d, boxscore b
     WHERE d.player='"""+playerName+"""' AND
      b.id=d.boxscore AND b.season='2016';
    """)
    data = getPlayerSummaryStats(p['player'], p['team'], player_data)
    data['position'] = position
    data['salary'] = salary
    #print type(salary)
    if type(salary) == str:
        data['fppgsal'] = (data['fppg']*1000)/float(salary)
    else:
        data['fppgsal'] = data['fppg']
    if salary != None:
        player_stats.append(data)
        if position == "LW" or position == "RW":
            wing_stats.append(data)
        elif position == "C":
            center_stats.append(data)
        elif position == "D":
            defence_stats.append(data)
player_stats_sorted = sorted(player_stats, key=itemgetter('time_on_ice_s'), reverse=True)
center_stats_sorted = sorted(center_stats, key=itemgetter('time_on_ice_s'), reverse=True)
wing_stats_sorted = sorted(wing_stats, key=itemgetter('time_on_ice_s'), reverse=True)
defence_stats_sorted = sorted(defence_stats, key=itemgetter('time_on_ice_s'), reverse=True)

outputToTemplate(center_stats_sorted, 'out/10272015_center.html')
outputToTemplate(wing_stats_sorted, 'out/10272015_wing.html')
outputToTemplate(defence_stats_sorted, 'out/10272015_defence.html')

print template.render(player_stats=player_stats_sorted)
