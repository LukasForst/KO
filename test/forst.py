#!/usr/bin/env python3
from itertools import product

from gurobipy import *


def run(in_file, out_file):
    M, N = 13, 4
    with open(in_file, 'r') as f:
        C = int(f.readline())
        C24 = int(f.readline())

        e = [int(i) for i in f.readline().split()]
        t = [int(i) for i in f.readline().split()]

        cs = {}
        for i in range(N):
            cs[i] = {}
            line = map(int, f.readline().split())
            for j, c in enumerate(line):
                cs[i][j] = c
        ps = {}
        for i in range(N):
            ps[i] = {}
            line = map(int, f.readline().split())
            for j, p in enumerate(line):
                ps[i][j] = p

    m = Model()
    xs = m.addVars(N, M, lb=0, vtype=GRB.INTEGER)

    # a
    m.addConstr(sum(xs[i, j] * cs[i][j] for i, j in product(range(N), range(M))) <= C)

    # b
    for j in range(M):
        m.addConstr(sum(xs[i, j] for i in range(N)) >= t[j])

    # c
    ks = m.addVars(M, lb=0, vtype=GRB.INTEGER)
    m.addConstrs(xs[3, j] == 6 * ks[j] for j in range(M))

    # d
    m.addConstr(sum(xs[1, j] * cs[1][j] for j in range(M)) + sum(xs[3, j] * cs[3][j] for j in range(M)) <= C24)

    # e
    m.addConstrs(sum(xs[i, j] for j in range(M)) <= e[i] for i in range(N))

    # f
    z = m.addVar(vtype=GRB.INTEGER, name='z', lb=0)

    sum_0 = sum(xs[0, j] * ps[0][j] for j in range(M))
    sum_3 = sum(xs[3, j] * ps[3][j] for j in range(M))

    m.addConstr(sum_0 - sum_3 <= z)
    m.addConstr(sum_3 - sum_0 <= z)

    # objective
    m.setObjective(z, sense=GRB.MINIMIZE)
    m.optimize()
    if m.status != GRB.OPTIMAL:
        with open(out_file, 'w') as f:
            f.write('-1\n')
    else:
        with open(out_file, 'w') as f:
            f.write(f'{int(m.objVal)}\n')
            for i in range(N):
                row = []
                for j in range(M):
                    row.append(int(xs[i, j].x))
                f.write(' '.join(map(str, row)))

                f.write('\n')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        (input_file, output) = (sys.argv[1], sys.argv[2])
    else:
        (input_file, output) = ('instances/rand_5.txt', 'output.txt')

    run(input_file, output)
