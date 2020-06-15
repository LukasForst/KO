#!/usr/bin/env python3

import math
import sys
from itertools import product
from typing import Tuple, List, Dict


def euclidean_dist(a: Tuple, b: Tuple) -> float:
    x1, y1 = a
    x2, y2 = b
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


class Edge:
    def __init__(self, cost: float,
                 lower: int = 0, upper: int = 1, flow: int = 0):
        self.cost = cost
        self.lower, self.upper, self.flow = lower, upper, flow

    def residuals(self) -> Tuple['Edge', 'Edge']:
        a = Edge(cost=self.cost, upper=self.upper - self.flow)
        b = Edge(cost=-self.cost, upper=self.flow - self.lower)
        return a, b


def create_residuals(edges: Dict[Tuple, Edge]) -> Dict[Tuple, Edge]:
    res = {}
    for (v1, v2), edge in edges.items():
        # create residuals
        res[(v1, v2)] = Edge(upper=edge.upper - edge.flow, cost=edge.cost)
        res[(v2, v1)] = Edge(upper=edge.flow - edge.lower, cost=-edge.cost)
    return res


def bellman_ford(residuals: Dict[Tuple, Edge]) -> Tuple[int, List]:
    dist, pred, edges = {}, {}, {}

    # create virtual source node
    source = 'S'
    dist[source] = 0

    # Step 1: initialize graph
    for (v1, v2), edge in residuals.items():
        if edge.upper:
            # set distance to infinity
            dist[v1], dist[v2] = float('inf'), float('inf')
            # create valid residuals
            edges[(v1, v2)] = edge

            # introduce new edges from the start to the all vertices
            edges[(source, v1)] = Edge(cost=0)
            edges[(source, v2)] = Edge(cost=0)

    # Step 2: relax edges repeatedly (maybe -1?
    for _ in range(len(edges.keys()) - 1):
        for (u, v), edge in edges.items():
            if dist[u] + edge.cost < dist[v]:
                dist[v] = dist[u] + edge.cost
                pred[v] = u

    in_cycle = None
    # Step 3: check for negative-weight cycles
    for (u, v), edge in edges.items():
        if dist[u] + edge.cost < dist[v]:
            in_cycle = v
            break

    # backtrack cycle
    if in_cycle:
        cycle = backtrack_cycle(pred, in_cycle)
        return cycle_walk(cycle[0], cycle, residuals)
    return 0, []


def cycle_walk(first: str, cycle: List, residuals: dict):
    capacity, previous = float('inf'), first
    cycle.append(first)

    final = []
    for current in cycle[1:]:
        final.append((previous, current))
        capacity, previous = min(capacity, residuals[(previous, current)].upper), current

    return capacity, final


def backtrack_cycle(pred: dict, start: str) -> List[str]:
    cycle, cur = [start], pred[start]
    while cur not in cycle:
        cycle.append(cur)
        cur = pred[cur]
    cycle_starts_idx = cycle.index(cur)
    return cycle[cycle_starts_idx:][::-1]


def cycle_cancelling(edges: Dict[Tuple, Edge]) -> Dict[Tuple, Edge]:
    residuals = create_residuals(edges)
    while True:
        capacity, cycle = bellman_ford(residuals)
        if capacity:
            for (i, j) in cycle:
                # is forward
                if (i, j) in edges:
                    edges[(i, j)].flow += capacity
                else:
                    edges[(j, i)].flow -= capacity

                residuals[(i, j)].upper -= capacity
                residuals[(j, i)].upper += capacity
        else:
            break
    return edges


def solve(players: int, frames: int, data: dict) -> List[List[int]]:
    projections = []
    # go fow all frames
    for f1_idx in range(frames - 1):
        f2_idx = f1_idx + 1

        f1, f2 = data[f1_idx], data[f2_idx]
        edges = {}
        # connect all players
        for p1, p2 in product(range(players), range(players)):
            # create ids for the vertices -> it must be strings as zeros would fuck that up
            v1, v2 = f'-{p1}', f'{p2}'
            # create edge and randomly connect players -> create initial flow
            edges[(v1, v2)] = Edge(cost=euclidean_dist(f1[p1], f2[p2]), flow=1 if p1 == p2 else 0)

        solution = cycle_cancelling(edges)
        projections.append([int(j) + 1 for (_, j), edge in solution.items() if edge.flow])

    return projections


if __name__ == '__main__':
    in_file, out_file = sys.argv[1], sys.argv[2]
    with open(in_file, "r") as f:
        players, frames = [int(x) for x in f.readline().split()]

        data = {}
        for frame in range(frames):
            data[frame] = {}
            line = [int(x) for x in f.readline().split()]
            for player, (x, y) in enumerate(zip(line[0::2], line[1::2])):
                data[frame][player] = x, y

    projections = solve(players, frames, data)

    with open(out_file, "w") as file:
        for p in projections:
            file.write(' '.join(map(str, p)) + "\n")
