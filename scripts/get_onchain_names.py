import json
import csv

DATA_SOURCE = "onchain.csv"

with open(DATA_SOURCE, newline='') as csvfile:
    datafile = list(csv.reader(csvfile))

names = []

for i in range(1, len(datafile)): # Start from 1 to skip header line of csv
    if datafile[i][1] not in names:
        names.append(datafile[i][1])

print(names)
