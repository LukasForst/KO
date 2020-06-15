#!/usr/bin/env python3
import sys
from collections import deque
from copy import deepcopy
from typing import List, Optional, Tuple

MAX_INT = sys.maxsize


class Edge:
    def __init__(self, source, target, lower, upper, flow):
        self.source = source
        self.target = target
        self.lower = lower
        self.upper = upper
        self.flow = flow


class Vertex:
    def __init__(self, incoming=None, outgoing=None):
        self.incoming = incoming if incoming else []
        self.outgoing = outgoing if outgoing else []


class Graph:
    def __init__(self, edges=None, vertices=None):
        self.edges = edges if edges else []
        self.vertices = vertices if vertices else []

    def st(self) -> Tuple[int, int]:
        return 0, self.size() - 1

    def size(self) -> int:
        return len(self.vertices)

    def insert(self, source, target, lower=0, upper=0, flow=0):
        e = Edge(source, target, lower, upper, flow)
        self.edges.append(e)
        self.vertices[source].outgoing.append(e)
        self.vertices[target].incoming.append(e)


def ff_labeling(G: Graph) -> Tuple[int, List[Tuple[Edge, int]]]:
    s, t = G.st()
    path_to = [(0, None, 0, 0)] * G.size()

    visited = {s}
    queue = deque([s])

    min_capacity = MAX_INT
    path = []

    while queue:
        v = G.vertices[queue.popleft()]

        for edge in v.outgoing:
            target = edge.target
            if target not in visited and edge.flow < edge.upper:
                path_to[target] = edge.source, edge, 1, edge.upper - edge.flow
                queue.append(target)
                visited.add(target)

        for edge in v.incoming:
            source = edge.source
            if source not in visited and edge.flow > edge.lower:
                path_to[source] = edge.target, edge, -1, edge.flow - edge.lower
                queue.append(source)
                visited.add(source)

        if t in visited:
            parent, edge, direction, capacity = path_to[t]
            while edge:
                min_capacity = min(min_capacity, capacity)
                path.append((edge, direction))
                parent, edge, direction, capacity = path_to[parent]

            break

    return min_capacity, path


def ff_algorithm(G: Graph) -> Graph:
    bottleneck, augmenting_path = ff_labeling(G)
    while augmenting_path:
        for e, direction in augmenting_path:
            e.flow += direction * bottleneck
        bottleneck, augmenting_path = ff_labeling(G)
    return G


def build_g_dot(G: Graph) -> Graph:
    G_dot = deepcopy(G)
    # add new source and target
    G_dot.vertices = ([Vertex()] + G_dot.vertices + [Vertex()])
    # shift all existing edges
    for e in G_dot.edges:
        # shift indices - new source and target added
        e.target += 1
        e.source += 1
        # normalize bounds
        e.upper -= e.lower
        e.lower, e.flow = 0, 0
    return G_dot


def max_flow(G: Graph) -> Optional[Graph]:
    # build extended graph
    G_dot = build_g_dot(G)
    s, t = G_dot.st()

    G_dot.insert(source=t - 1, target=s + 1, upper=MAX_INT)

    for idx, v in enumerate(G.vertices, start=1):
        balance = sum(e.lower for e in v.incoming) - sum(e.lower for e in v.outgoing)
        if balance >= 0:
            G_dot.insert(source=s, target=idx, upper=balance)
        else:
            G_dot.insert(source=idx, target=t, upper=-balance)

    # sanity check
    G_dot = ff_algorithm(G_dot)
    # is the solution correct?
    banned = [e for e in G_dot.vertices[s].outgoing if e.flow != e.upper]
    if banned:
        return None

    # set flow in the original graph
    for original, extended in zip(G.edges, G_dot.edges):
        original.flow = original.lower + extended.flow

    return ff_algorithm(G)


def run(in_file, out_file):
    with open(in_file, 'r') as file:
        C, P = [int(x) for x in file.readline().split()]

        G = Graph(edges=[], vertices=[Vertex() for _ in range(1 + C + P + 1)])
        s, t = G.st()

        for c in range(1, C + 1):
            lower, upper, *products = [int(x) for x in file.readline().split()]
            # connect customer with source
            G.insert(source=s, target=c, lower=lower, upper=upper)

            for p in products:
                # products indices are behind the customers
                p += C
                # upper 1 because customer can make review just once
                G.insert(source=c, target=p, upper=1)

        demand = [int(x) for x in file.readline().split()]
        for p, demand in enumerate(demand, start=C + 1):
            G.insert(source=p, target=t, lower=demand, upper=MAX_INT)

    G = max_flow(G)

    result = []
    if G:
        for v in G.vertices[1:C + 1]:
            reviews = sorted([e.target for e in v.outgoing if e.flow])
            result.append(' '.join([str(r - C) for r in reviews]))
    else:
        result = ['-1']

    with open(out_file, 'w') as file:
        file.writelines([f'{line}\n' for line in result if line])


if __name__ == '__main__':
    in_file, out_file = sys.argv[1], sys.argv[2]
    run(in_file, out_file)
