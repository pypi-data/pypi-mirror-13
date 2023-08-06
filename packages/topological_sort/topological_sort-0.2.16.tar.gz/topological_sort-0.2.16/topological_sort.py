#!/usr/bin/env python
#
# Topological sorting.
# Copyright (c) 2016 Ruda Moura <ruda.moura@gmail.com>
# Licensed under the terms of the MIT License
#

class CycleError(Exception):
    pass


def get_words(fileobj):
    for line in fileobj:
        if line == '\n': continue
        for word in line.split():
            yield word

def read_pairs(fileobj):
    words = get_words(fileobj)
    while True:
        a = next(words)
        b = next(words)
        yield (a, b)

def make_table(pairs):
    table = {}
    for pair in pairs:
        if pair[0] == pair[1]:  # disconnected node
            table[pair[0]] = [0, []]
        else:
            if pair[0] not in table:
                table[pair[0]] = [0, [pair[1]]]
            else:
                table[pair[0]][1].append(pair[1])
            if pair[1] not in table:
                table[pair[1]] = [1, []]
            else:
                table[pair[1]][0] += 1
    return table

def topological_sort(pairs):
    table = make_table(pairs)
    remaining = True
    while remaining:
        to_reduce = []
        remaining = False
        for vert, info in table.items():
            incident, adjacency = info
            if incident is None:
                continue
            elif incident == 0:
                yield vert
                table[vert][0] = None
                to_reduce.extend(adjacency)
            else:
                remaining = True
        if to_reduce == [] and remaining == True:
            raise CycleError()
        for vert in to_reduce:
            table[vert][0] -= 1
