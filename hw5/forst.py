#!/usr/bin/env python3

import sys


def permute(tasks, assignments, remaining, cost, upper):
    if len(remaining) == 0:
        return True, False, cost, assignments

    opt = cost <= min(tasks[i][1] for i in remaining)

    # prune when deadline is missed
    for i in remaining:
        (p, r, d) = tasks[i]
        start_time = max(cost, r)
        if start_time + p > d:
            return False, opt, cost, assignments

    # prune when remaining time is higher then upper
    remaining_ps = sum(tasks[i][0] for i in remaining)
    min_release = min(tasks[i][1] for i in remaining)
    release = max(min_release, cost)
    if release + remaining_ps >= upper:
        return False, opt, cost, assignments

    best_found, dont_track, best_cost, best_solution = False, opt, float('inf'), []
    for i in remaining:
        new_asgs = assignments + [i]
        (p, r, d) = tasks[i]

        new_cost = max(r, cost) + p
        sol_found, no_track, f_cost, perm = permute(tasks, new_asgs, [t for t in remaining if t != i], new_cost, upper)

        if sol_found:
            best_found = True
            if f_cost < best_cost:
                best_cost = f_cost
                upper = best_cost
                best_solution = perm

        dont_track = dont_track or no_track
        if no_track:
            break

    return best_found, dont_track, best_cost, best_solution


def bradley(tasks):
    upper_bound = max(d for (_, _, d) in tasks.values())
    remaining = [i for i in range(len(tasks))]
    return permute(tasks, [], remaining, 0, upper_bound + 1)


def run(in_path, out_path):
    with open(in_path, "r") as f:
        n = int(f.readline())

        lines = [map(int, line.split()) for line in f.readlines()]

    tasks = {i: (p, r, d) for i, (p, r, d) in enumerate(lines)}
    found, _, cost, solution = bradley(tasks)

    if not found:
        pp = [-1]
    else:
        pp = [0 for _ in range(n)]
        start = 0
        for i in solution:
            (p, r, d) = tasks[i]
            this_s = max(start, r)
            pp[i] = this_s
            start = this_s + p

    with open(out_path, 'w') as f:
        f.write('\n'.join(map(str, pp)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run(sys.argv[1], sys.argv[2])
    else:
        run('instances/public_5.txt', 'out.txt')
