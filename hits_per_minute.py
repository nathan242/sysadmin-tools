#!/usr/bin/python

import sys
import os
import time


count = {}
total = 0
highest = 0
average = 0

log = open(sys.argv[1], "r")

for line in log:
    datestring = line.split()[3].replace("[", "")[:-3]
    if datestring in count:
        count[datestring] += 1
    else:
        count[datestring] = 1

for i in sorted(count.keys()):
    print i+" : "+str(count[i])
    total += count[i]
    if count[i] > highest:
        highest = count[i]

average = total/len(count)
print "TOTAL: "+str(total)
print "HIGHEST: "+str(highest)
print "AVERAGE: "+str(average)
