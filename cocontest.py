#!/usr/bin/env python3
from itertools import product

import numpy as np
from gurobipy import *

if __name__ == '__main__':
    input_file, output_file = sys.argv[1], sys.argv[2]

    with open(input_file, 'r') as f:
        cb = f.readline().split()
        C, B = int(cb[0]), int(cb[1])

        worker_orders = []  # worker_orders[client] = [w1,w2]
        d = []  # d[client][worker] = time spent
        M = 0
        for c in range(C):
            client_data = [int(value) for value in f.readline().split()]
            worker_orders.append(client_data[0::2])

            obj = {}
            for k, t in zip(client_data[0::2], client_data[1::2]):
                obj[k] = t
                M += t
            d.append(obj)

    model = Model()

    s = model.addVars(C, B, vtype=GRB.INTEGER)
    z = model.addVar(lb=0, obj=1.0, vtype=GRB.INTEGER)

    # z is last worker exited
    for c in range(C):
        last_worker = worker_orders[c][-1]
        model.addConstr(s[c, last_worker] + d[c][last_worker] <= z)

    # for all workers there cant be overlap
    for k in range(B):
        # create product for client pairs (top triangle) only if they have same buro worker
        cartesian = [(i, j) for i, j in product(range(C), range(C))
                     if i < j and (d[i].get(k) and d[j].get(k))]
        # overlap between two clients
        for i, j in cartesian:
            y = model.addVar(vtype=GRB.BINARY)
            # sooner / later job
            model.addConstr(s[i, k] + d[i][k] <= s[j, k] + M * y)
            model.addConstr(s[j, k] + d[j][k] <= s[i, k] + M * (1 - y))

    # orders of orders
    for c in range(C):
        orders = worker_orders[c]
        for i in range(len(orders)):
            w1 = orders[i]
            if i + 1 < len(orders):
                w2 = orders[i + 1]
                model.addConstr(s[c, w1] + d[c][w1] <= s[c, w2])

    model.optimize()

    worker = []
    for k in range(B):
        start_times = [int(s[i, k].x) for i in range(C)]
        worker.append(' '.join([str(order) for order in np.argsort(start_times) if d[order].get(k)]))

    with open(output_file, 'w') as f:
        f.write(f'{int(z.x)}\n')
        f.write('\n'.join(worker))
