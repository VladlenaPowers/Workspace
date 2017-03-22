#!C:/Python27/

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

    length =  [[1,4,1,1,4],[2,3,2,2,2],[3,3,3,2]]
    T = 10
    K = 5


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
            idle = pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name=varName)
            zSum.addTerms(1.0, idle)
            zRow.append(idle)
        z.append(zRow)

    x = []
    for m in range(M):
        n = len(length[m])
        jobStartTimes = []
        for j in range(n):
            thisJobStarts = []
            for t in range(T+sumOfLengthServerJobs[m]+1):
                thisJobStarts.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='X_m{0}_j{1}_t{2}'.format(m, j, t)))
            jobStartTimes.append(thisJobStarts)
        x.append(jobStartTimes)

    y = []
    for t in range(T+1):
        y.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='Y_t{0}'.format(t)))

    x1 = []
    for m in range(M):
        n = len(length[m])
        jobStartTimes = []
        for j in range(n):
            thisJobStarts = []
            for t in range(T):
                thisJobStarts.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='X1_m{0}_j{1}_t{2}'.format(m, j, t)))
            jobStartTimes.append(thisJobStarts)
        x1.append(jobStartTimes)
    x2 = []
    for m in range(M):
        n = len(length[m])
        jobStartTimes = []
        for j in range(n):
            thisJobStarts = []
            for t in range(T):
                thisJobStarts.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='X2_m{0}_j{1}_t{2}'.format(m, j, t)))
            jobStartTimes.append(thisJobStarts)
        x2.append(jobStartTimes)
    x3 = []
    for m in range(M):
        n = len(length[m])
        jobStartTimes = []
        for j in range(n):
            thisJobStarts = []
            for t in range(T):
                thisJobStarts.append(pladdLPM.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='X3_m{0}_j{1}_t{2}'.format(m, j, t)))
            jobStartTimes.append(thisJobStarts)
        x3.append(jobStartTimes)


    pladdLPM.update()
    pladdLPM.setObjective(zSum, GRB.MINIMIZE)

    for m in range(M):
        n = len(length[m])
        for j in range(n):
            pladdLPM.addConstr(quicksum(x[m][j]) == 1.0, 'C: every job scheduled for server {0}'.format(m))

    # For a job j, jobs with a greater index much start after j ends
    for m in range(M):
        n = len(length[m])
        for i in range(n):
            for j in range(n):
                if (i > j):
                    for t in range(T+sumOfLengthServerJobs[m]+1):
                        ub = t+length[m][j] - 1 + 1
                        ub = min(ub, T+sumOfLengthServerJobs[m]+1)
                        pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][:ub]) <= 1.0, 'C: jobs after job{0} must start after job{1} ends for server{2}'.format(j, j, m))

    # Jobs with an index less than j must end before j starts
    for m in range(M):
        n = len(length[m])
        for i in range(n):
            for j in range(n):
                if (i < j):
                    for t in range(T+sumOfLengthServerJobs[m]+1):
                        lb = t-length[m][i]+1
                        lb = max(lb, 0)
                        pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][lb:]) <= 1.0, 'C: jobs before job{0} must end before job{1} starts for server{2}'.format(j, j, m))






    # for m in range(M):
        # n = len(length[m])
        # for i in range(n-1):
        #     for t in range(T+1):
        #         pladdLPM.addConstr(quicksum(x[m][i][t:t+1]) <= quicksum(x[m][i+1][t+length[m][i]:T+1]), 'constraints {0}'.format(i))


    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n-2):
    #         for t in range(T+1):
    #             pladdLPM.addConstr(quicksum(x[m][i][t:t+length[m][i]+1]) + quicksum(x[m][i+1][t:t+length[m][i]+1]) + quicksum(x[m][i+2][t:t+length[m][i]+1]) <= quicksum(x[m][i][t:t+length[m][i]+1]), 'constraints {0}'.format(i))


    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n-1):
    #         for t in range(T):
    #             startOfPreviousJob = t+1-length[m][i]
    #             earliestPossibleStart = max(startOfPreviousJob, 0)
    #             pladdLPM.addConstr(x[m][i+1][t+1] <= x[m][i][earliestPossibleStart] + z[m][t], 'constraints {0}'.format(i))


    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n-1):
    #         for t in range(T):
    #             startOfPreviousJob = t+1-length[m][i]
    #             earliestPossibleStart = max(startOfPreviousJob, 0)
    #             print('x1_m_i_t {0}{1}{2}'.format(m,i,t))
    #             pladdLPM.addConstr(x1[m][i][t] >= x2[m][i][t] + x3[m][i][t])
    #             pladdLPM.addConstr(x1[m][i][t] <= x[m][i+1][t+1])
    #             pladdLPM.addConstr(x1[m][i][t] >= 2*x[m][i+1][t+1]-1)
    #             pladdLPM.addConstr(x2[m][i][t] <= x[m][i+1][t+1])
    #             pladdLPM.addConstr(x2[m][i][t] <= x[m][i][earliestPossibleStart])
    #             pladdLPM.addConstr(x2[m][i][t] >= x[m][i+1][t+1] + x[m][i][earliestPossibleStart] - 1)
    #             pladdLPM.addConstr(x3[m][i][t] <= x[m][i+1][t+1])
    #             pladdLPM.addConstr(x3[m][i][t] <= z[m][t])
    #             pladdLPM.addConstr(x3[m][i][t] >= x[m][i+1][t+1] + z[m][t] - 1)



    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n-1):
    #         for t in range(T):
    #             startOfPreviousJob = t+1-length[m][i]
    #             earliestPossibleStart = max(startOfPreviousJob, 0)
    #             print('x1_m_i_t {0}{1}{2}'.format(m,i,t))
    #             pladdLPM.addConstr(x1[m][i][t] >= x2[m][i][t] + x3[m][i][t])
    #             pladdLPM.addConstr(x1[m][i][t] <= x[m][i+1][t+1])
    #             pladdLPM.addConstr(x1[m][i][t] >= 2*x[m][i+1][t+1]-1)
    #             pladdLPM.addConstr(x2[m][i][t] <= x[m][i+1][t+1])
    #             pladdLPM.addConstr(x2[m][i][t] <= quicksum(x[m][i][earliestPossibleStart:t+1]) + z[m][t])
    #             pladdLPM.addConstr(x2[m][i][t] >= x[m][i+1][t+1] + quicksum(x[m][i][earliestPossibleStart:t+1])  + z[m][t] - 1)




    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n):
    #         for t in range(T-1):
    #             startOfPreviousJob = t+1-length[m][i]
    #             earliestPossibleStart = max(startOfPreviousJob, 0)
    #             print('x1_m_i_t {0}{1}{2}'.format(m,i,t))
    #             pladdLPM.addConstr(x[m][i][t+1] >= x2[m][i][t+1])
    #             pladdLPM.addConstr(x1[m][i][t+1] <= x[m][i][t+1])
    #             pladdLPM.addConstr(x1[m][i][t+1] >= 2*x[m][i][t+1]-1)
    #             pladdLPM.addConstr(x2[m][i][t+1] <= quicksum(x[m][i][earliestPossibleStart:t+2])+z[m][t])
    #             pladdLPM.addConstr(x2[m][i][t+1] <= x[m][i][t+1])
    #             pladdLPM.addConstr(x2[m][i][t+1] >= x[m][i][t+1]+z[m][t] + x[m][i][t] - 1)








    for m in range(M):
        n = len(length[m])
        for i in range(n-1):
            for t in range(T):
                if (i != 1):
                    startOfPreviousJob = t+1-length[m][i]
                    earliestPossibleStart = max(startOfPreviousJob, 0)
                    pladdLPM.addConstr(sum(row[t+1] for row in x[m][:]) - x[m][i][t+1] + z[m][t+1] >= x[m][i][earliestPossibleStart] + z[m][t], 'C: new constraints {0} and {1}'.format(m, i))

    # pladdLPM.addConstr(x[0][1][1] >= x[0][0][0]+z[0][0], 'C: new constraints {0} and {1}'.format(0, 1))

    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n-1):
    #         for t in range(T):
    #             largestEnd = t+length[m][i]-1
    #             latestPossibleEnd = max(T+1, largestEnd)
    #             pladdLPM.addConstr(quicksum(x[m][i][t:t+length[m][i]-1]) + quicksum(z[m][t:latestPossibleEnd]) <= 1, 'constraints {0}'.format(i))





    # # For a job j, jobs with a greater index much start after j ends
    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n):
    #         for j in range(n):
    #             if (i == j + 1):
    #                 for t in range(T+sumOfLengthServerJobs[m]+1):
    #                     ub = t+length[m][j] - 1 + 1
    #                     ub = min(ub, T+sumOfLengthServerJobs[m]+1)
    #                     pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][:ub]) <= 1.0, 'C: jobs after job{0} must start after job{1} ends for server{2}'.format(j, j, m))
    #
    # # Jobs with an index less than j must end before j starts
    # for m in range(M):
    #     n = len(length[m])
    #     for i in range(n):
    #         for j in range(n):
    #             if (i + 1 == j):
    #                 for t in range(T+sumOfLengthServerJobs[m]+1):
    #                     lb = t-length[m][i]+1
    #                     lb = max(lb, 0)
    #                     pladdLPM.addConstr(x[m][j][t] + quicksum(x[m][i][lb:]) <= 1.0, 'C: jobs before job{0} must end before job{1} starts for server{2}'.format(j, j, m))









    # Calculate idle time
    for m in range(M):
        n = len(length[m])
        for t in range(T+1):
            expr = LinExpr(0.0)
            expr.addTerms(1.0, z[m][t])
            for j in range(n):
                lb = t - length[m][j] + 1
                ub = t+1
                lb = max(lb, 0)
                expr.add(quicksum(x[m][j][lb:ub]))
            pladdLPM.addConstr(expr >= 1.0, 'C: idle time constaint for m{0}, t{1}'.format(m, t))


    # Jobs may only start at the takes, which are budgeted
    for m in range(M):
        n = len(length[m])
        for t in range(T+1):
            expr = LinExpr(0.0)
            for j in range(n):
                expr.addTerms(1.0, x[m][j][t])
            pladdLPM.addConstr(expr <= y[t], 'C: jobs can only start at take{0} for server {1}'.format(t, m))

    pladdLPM.addConstr(quicksum(y) <= (K+1), 'C: sum(y) <= k')

    pladdLPM.addConstr(y[0] == 1, 'First jobs on all servers start at time 0')

    for m in range(M):
        pladdLPM.addConstr(x[m][0][0] == 1, 'First job starts at time 0 on server {0}'.format(m))

    pladdLPM.optimize()



    print('z')
    for m in range(M):
        print(''.join(['['+str(z[m][i].x)+']' for i in range(T+1)]))


    for m in range(M):
        print('x_m{0}'.format(m))
        for j in range(len(length[m])):
            print(''.join(['[{:.1f}]'.format(x[m][j][i].x) for i in range(T+sumOfLengthServerJobs[m]+1)]))

    print('y')
    for t in range(T+1):
        print('[' + str(y[t].x) +']')

    for m in range(M):
        print('x1_m{0}'.format(m))
        for j in range(len(length[m])-1):
            print(''.join(['[{:.1f}]'.format(x1[m][j][i].x) for i in range(T)]))
    for m in range(M):
        print('x2_m{0}'.format(m))
        for j in range(len(length[m])-1):
            print(''.join(['[{:.1f}]'.format(x2[m][j][i].x) for i in range(T)]))
    for m in range(M):
        print('x3_m{0}'.format(m))
        for j in range(len(length[m])-1):
            print(''.join(['[{:.1f}]'.format(x3[m][j][i].x) for i in range(T)]))

except GurobiError as err:
    print('Gurobi ERROR({0}): {1}'.format(err.errno, err.message))

except AttributeError as err:
    print('Encountered an attribute error: {0}'.format(err))
