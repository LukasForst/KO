#!/usr/bin/env python3

from gurobipy import *
import sys


def optimize(q):
    hours = 24

    m = Model()
    z = m.addVars(hours, vtype=GRB.INTEGER, lb=0, obj=1.0, name="z")
    x = m.addVars(hours, vtype=GRB.INTEGER, lb=0, name="x")
    y = [sum([x[j % hours] for j in range(i - 7, i + 1)]) for i in range(hours)]

    for i in range(0, hours):
        m.addConstr(q[i] - y[i] <= z[i])
        m.addConstr(y[i] - q[i] <= z[i])

    m.optimize()

    objectiveValue = int(m.objVal)
    xs = [int(x[i].x) for i in range(0, hours)]

    return objectiveValue, xs


if __name__ == '__main__':
    input, output = sys.argv[1], sys.argv[2]

    with open(input, 'r') as f:
        q = [int(x) for x in f.read().split()]

    objectiveValue, xs = optimize(q)

    with open(output, 'w') as f:
        f.write(f"{str(objectiveValue)}\n")
        f.write(" ".join(map(str, xs)))
