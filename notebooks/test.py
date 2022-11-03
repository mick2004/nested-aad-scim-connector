#!/usr/bin/env python3
from collections import defaultdict

initials, countries, incomes = [],[],[]

dict1 = {}
dict2 = defaultdict(set)

keywordFile = """
1:Qatar:98900

2:Liechtenstein:89400

3:Luxembourg:80600

4:Bermuda:69900

5:Singapore:59700

6:Jersey:57000
""".split("\n\n")

for line in keywordFile:
    line = line.upper().strip("\n").split(":")
    initials.append(line[1][0])
    countries.append(line[1])
    incomes.append(line[2])

for i,country in enumerate(countries):
    dict1[country] = incomes[i]
    dict2[initials[i]].add(country)

print(dict2["L"])