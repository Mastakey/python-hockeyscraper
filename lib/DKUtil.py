class DKUtil(object):
    def __init__(self, players, salarydata, config):
        self.players = players
        self.salarydata = salarydata



#STATIC METHODS:
    @staticmethod
    def getPlayerSalary(player, dkdata):
        for data in dkdata:
            if player == data['player']:
                return data['salary']
    @staticmethod
    def getPlayerPosition(player, dkdata):
        for data in dkdata:
            if player == data['player']:
                return data['position']
    @staticmethod
    def getSeconds(myStr):
        minutes = int(myStr.split(':')[0])
        seconds = int(myStr.split(':')[1])
        return minutes*60+seconds
    @staticmethod
    def getTimeStr(seconds):
        myMin = int(seconds/60)
        mySec = seconds % 60
        return str(myMin)+':'+str(mySec)
