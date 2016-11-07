#!C:/Python34/

# Copyright 2016, Gurobi Optimization, Inc.

from gurobipy import *

def printvar(name, value):
    print('{0} = {1}'.format(name, value))
    return

def preprocessing(T,K,serverjobs):
    T = T + 1
    if len(serverjobs) > (K+1):
        serverjobs = serverjobs[:K+1]
    if len(serverjobs) <= K and sum(serverjobs) < T:
        return 'Not enought jobs on this server'
    if serverjobs[0] > T:
        serverjobs[0] = T
        serverjobs = serverjobs[:1]
        K = 0
    totallength = serverjobs[0]
    K = len(serverjobs) - 1
    for i in range (1, K+1):
        if totallength + serverjobs[i] > T:
            serverjobs[i] = T - totallength
            serverjobs = serverjobs[:i+1]
            if serverjobs[i] == 0:
                serverjobs = serverjobs[:i]
            break
        totallength = totallength + serverjobs[i]
    return serverjobs

try:
    length = [[1,90,10,11,23,132,1], [200,1,3,2,3,4,5,3,4],[1,1,1]]
    T = 3
    K = 2
    M = len(length)
    for i in range (M):
        print('{3}{0}{1} = {2}'.format('server ', i, length[i],"Before preprocessing  "))
    for i in range (M):
        length[i] = preprocessing(T,K,length[i])
    for i in range (M):
        print('{3}{0}{1} = {2}'.format('server ', i, length[i],"After preprocessing  "))
    printvar('T',T)
    printvar('K',K)
    sumOfLengthServerJobs = []
    for i in range (M):
        sumOfLengths = sum(length[i])
        sumOfLengthServerJobs.append(sumOfLengths)
        print('{0}{1} = {2}'.format('length of jobs on server', i, sumOfLengths))

    # Create a new model
    pladdLPM = Model("model0")

    z = []
    zSum = LinExpr(0.0)
    for m in range(M):
        zRow = []
        for t in range(T+1):
            varName = 'Z_m{0}_t{1}'.format(m, t)
            idle = pladdLPM.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name=varName)
            zSum.addTerms(1.0, idle)
            zRow.append(idle)
        z.append(zRow)

    x = []
    for m in range(M):
        jobStartTimes = []
        for j in range(len(length[m])):
            thisJobStarts = []
            for t in range(T+1):
                thisJobStarts.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='X_m{0}_j{1}_t{2}'.format(m, j, t)))
            jobStartTimes.append(thisJobStarts)
        x.append(jobStartTimes)

    pladdLPM.update()
    pladdLPM.setObjective(zSum, GRB.MINIMIZE)


    # For a job j, jobs with a greater index much start after j ends
    for m in range(M):
        n = len(length[m])
        for i in range(n):
            for j in range(n):
                if (i > j):
                    for t in range(T+1):
                        ub = t+length[m][j] - 1
                        ub = min(ub, T+sumOfLengthServerJobs[m])
                        pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][:ub]) <= 1.0, 'C: jobs after job{0} must start after job{1} ends for server{2}'.format(j, j, m))

    # Jobs with an index less than j must end before j starts
    for m in range(M):
        n = len(length[m])
        for i in range(n):
            for j in range(n):
                if (i < j):
                    for t in range(T+1):
                        lb = t-length[m][j]+1
                        lb = max(lb, 0)
                        pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][lb:]) <= 1.0, 'C: jobs before job{0} must end before job{1} starts for server{2}'.format(j, j, m))

    # Calculate idle time
    for m in range(M):
        n = len(length[m])
        for t in range(T+1):
            expr = LinExpr(0.0)
            expr.addTerms(1.0, z[m][t])
            for i in range(n):
                expr.addTerms(1.0, quicksum(x[m][i][lb:ub]))
                lb = t - length[m][i] + 1
                ub = t
                lb = max(lb, 0)
            pladdLPM.addConstr(expr >= 1.0, 'C: idle time constaint for m{0}, t{1}'.format(m, t))


    # Jobs may only start at the takes, which are budgeted
    for m in range(M):
        n = len(length[m])
        for t in range(T+1):
            expr = LinExpr(0.0)
            for j in range(n):
                expr.addTerms(1.0, x[m][j][t])
            pladdLPM.addConstr(expr <= y[t], 'C: jobs can only start at take{0} for server {1}'.format(t, m))

    pladdLPM.addConstr(quicksum(y) <= K, 'C: sum(y) <= k')

    # # Set objective
    # # m.setObjective(x + y, GRB.MINIMIZE)
    #
    # # Add constraint: x + 2 y + 3 z <= 4
    # # m.addConstr(2 * x + 3 * y == 5, "c0")
    # # m.addRange(x + 0, 0.0, 1.0, "c1")

    pladdLPM.optimize()

    # for v in m.getVars():
    #     print('%s %g' % (v.varName, v.x))
    #
    # print('Obj: %g' % m.objVal)

except GurobiError as err:
    print('Encountered a Gurobi ERROR: {0}'.format(err))

except AttributeError as err:
    print('Encountered an attribute error: {0}'.format(err))
