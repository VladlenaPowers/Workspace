#!C:/Python34/

# Copyright 2016, Gurobi Optimization, Inc.

from gurobipy import *

def printvar(name, value):
    print('{0} = {1}'.format(name, value))
    return

def preprocessing(T,K,length):

    return
try:


    length = [[1, 2, 3], [1, 1]]
    T = 2;
    K = 3;
    M = len(length)
    N = len(length[0])
    print(T)
    print('T = {0}'.format(T))
    print('K = {0}'.format(K))
    print('M = {0}'.format(M))
    print('N = {0}\n'.format(N))
    printvar('T',T)
    printvar('K',K)
    printvar('M',M)
    printvar('N',N)

    # # Create a new model
    # m = Model("model0")
    #
    #

    # # Create variables
    # x = m.addVar(vtype=GRB.CONTINUOUS, name="x")
    # y = m.addVar(vtype=GRB.CONTINUOUS, name="y")
    #
    # # Integrate new variables
    # m.update()
    #
    # # Set objective
    # # m.setObjective(x + y, GRB.MINIMIZE)
    #
    # # Add constraint: x + 2 y + 3 z <= 4
    # # m.addConstr(2 * x + 3 * y == 5, "c0")
    # # m.addRange(x + 0, 0.0, 1.0, "c1")
    #
    # m.optimize()
    #
    # for v in m.getVars():
    #     print('%s %g' % (v.varName, v.x))
    #
    # print('Obj: %g' % m.objVal)

except GurobiError as err:
    print('Encountered a Gurobi ERROR: {0}'.format(err))

except AttributeError as err:
    print('Encountered an attribute error: {0}'.format(err))
