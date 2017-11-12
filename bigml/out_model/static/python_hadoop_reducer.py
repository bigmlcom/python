#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

count = 0
previous = None

def print_result(values, prediction, count):
    """Prints input data and predicted value as an ordered list.

    """
    result = \"[%s, %s]\" % (values, prediction)
    print u\"%s\\t%s\" % (result, count)

for line in sys.stdin:
    values, prediction = line.strip().split('\\t')
    if previous is None:
        previous = (values, prediction)
    if values != previous[0]:
        print_result(previous[0], previous[1], count)
        previous = (values, prediction)
        count = 0
    count += 1
if count > 0:
    print_result(previous[0], previous[1], count)
