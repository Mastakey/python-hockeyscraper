
def getDksalaries():
    f = open('10272015_DKSalaries.csv', 'r')
    salary_lines = f.readlines()
    count = 0
    salaries = []
    #print len(salary_lines)
    for line in salary_lines:
        #ignore header line
        if count > 0:
            mydict = {}
            mycsvlist = line.split(',')
            mydict['position'] = mycsvlist[0].replace("\"", "")
            mydict['player']  = mycsvlist[1].replace("\"", "")
            mydict['salary']  = mycsvlist[2].replace("\"", "")
            #print position
            salaries.append(mydict)
        count += 1
    return salaries

salaries = getDksalaries()
print salaries
