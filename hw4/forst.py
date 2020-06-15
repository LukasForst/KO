#!/usr/bin/env python3
import sys
from itertools import product

import gurobipy as g
import numpy as np
from gurobipy import GRB


def non_overlapping_iter(n):
    return non_overlapping(range(n))


def non_overlapping(iterable):
    return [(i, j) for i, j in product(iterable, repeat=2) if i != j]


def compute_costs(s, n) -> dict:
    c = {}
    # compute costs for existing nodes
    for i, j in non_overlapping_iter(n):
        c[(i, j)] = np.absolute(s[i][:, -1, :] - s[j][:, 0, :]).sum()

    # introduce dummy nodes
    for i in range(n):
        c[(i, n)], c[(n, i)] = 0, 0

    return c


def find_cycle(graph, vertex):
    cycle = [vertex]
    cur = graph[vertex]
    while cur != vertex:
        cycle.append(cur)
        cur = graph[cur]
    return cycle


def find_shortest_cycle(graph):
    shortest = None
    visited = set()
    for vertex in graph:
        if vertex not in visited:
            cycle = find_cycle(graph, vertex)
            visited = visited.union(cycle)

            if not shortest or len(cycle) < len(shortest):
                shortest = cycle
                
    return shortest, len(shortest)


# noinspection PyArgumentList
def tsp(c, n):
    subset_length = n + 1
    iterations = non_overlapping_iter(subset_length)

    # create model
    m = g.Model()
    m.Params.lazyConstraints = 1

    x = {
        (i, j): m.addVar(vtype=g.GRB.BINARY, obj=c[i, j]) for i, j in iterations
    }

    # rows
    m.addConstrs(
        g.quicksum(x[i, j] for j in range(subset_length) if i != j) == 1
        for i in range(subset_length)
    )
    # columns
    m.addConstrs(
        g.quicksum(x[j, i] for j in range(subset_length) if i != j) == 1
        for i in range(subset_length)
    )

    def callback(m, where):
        if where == GRB.Callback.MIPSOL:
            # build graph
            graph = {i: j for (i, j) in iterations if m.cbGetSolution(x[i, j])}
            # get cycle
            cycle, length = find_shortest_cycle(graph)
            if length != subset_length:
                # append additional constraints
                m.cbLazy(g.quicksum([x[i, j] for i, j in non_overlapping(cycle)]) <= length - 1)

    m.optimize(callback)

    return {v[0]: v[1] for v, k in x.items() if k.x}


def run(in_path, out_path):
    with open(in_path, "r") as f:
        n, w, h = map(int, f.readline().split())
        stripe_shape = (h, w, 3)

        s = np.empty((n, *stripe_shape))
        for i, line in enumerate(f.readlines()):
            s[i] = np.fromiter(line.split(), dtype=np.int64).reshape(stripe_shape)

    # prepare costs
    c = compute_costs(s, n)
    # compute tsp
    graph = tsp(c, n)

    # backtrack graph
    current, solution = graph[n], []
    while current != n:
        solution.append(current)
        current = graph[current]

    with open(out_path, "w") as file:
        # write and shift
        file.write(' '.join([str(x + 1) for x in solution]))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run(sys.argv[1], sys.argv[2])
    else:
        run('instances/example-1.txt', 'out.txt')
