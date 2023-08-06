#!/usr/bin/env python
#
# Topological sorting.
# Copyright (c) 2016 Ruda Moura <ruda.moura@gmail.com>
# Licensed under the terms of the MIT License
#

from __future__ import print_function

import sys
import topological_sort


def tsort(argv=None, stdout=None, stderr=None):
    if argv is None:
        argv = sys.argv
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    if argv[1:]:
        try:
            pairs = topological_sort.read_pairs(open(argv[1]))
        except IOError as err:
            print(err, file=sys.stderr)
            sys.exit(1)
    else:
        pairs = topological_sort.read_pairs(sys.stdin)
    try:
        print('\n'.join(topological_sort.topological_sort(pairs)), file=stdout)
    except topological_sort.CycleError:
        print('Cycle error!', file=stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('Interrupted!', file=stderr)
        sys.exit(1)

if __name__ == '__main__':
    tsort()
