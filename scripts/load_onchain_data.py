import json
import csv

DATA_SOURCE = "onchain.csv"
ONCHAIN_DATA_FILENAME = "v2_onchain_data.json"

def saveOnchainData(data):
    with open(ONCHAIN_DATA_FILENAME, "w") as datafile:
        json.dump(data, datafile)

def loadOnchainData():
    with open(ONCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

with open(DATA_SOURCE, newline='') as csvfile:
    datafile = list(csv.reader(csvfile))

print("Beginning data loading...")

data = []

data_dao = {}
num_voters = 0
for i in range(1, len(datafile)): # Start from 1 to skip header line of csv
    if "name" in data_dao and data_dao["name"] != datafile[i][1] + " (Onchain)":
        data_dao["average_voting_rate_all_time"] /= num_voters
        data.append(data_dao)
    if "name" not in data_dao or data_dao["name"] != datafile[i][1] + " (Onchain)":
        data_dao = {}
        data_dao["name"] = datafile[i][1] + " (Onchain)"
        data_dao["onchain"] = 1
        data_dao["average_prices"] = []
        data_dao["average_volumes"] = []
        data_dao["average_voting_rates"] = []
        data_dao["average_inverse_ginis"] = []
        data_dao["components"] = []
        data_dao["average_voting_rate_all_time"] = 0
        data_dao["average_inverse_gini_all_time"] = 0
        data_dao["average_vote_share_authors"] = 0
        data_dao["average_vote_share_non_authors"] = 0
        num_voters = 0
    num_voters += 1
    data_dao["average_voting_rate_all_time"] += float(datafile[i][31])

if num_voters > 0:
    data_dao["average_voting_rate_all_time"] /= num_voters
    data.append(data_dao)

saveOnchainData(data)
