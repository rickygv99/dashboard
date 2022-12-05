import json
import csv

DATA_SOURCE = "onchain.csv"
ONCHAIN_DATA_FILENAME = "v2_data.json"

def unshiftDecimals(supply, decimals):
    """
    Etherscan returns the total token supply shifted by their smallest
    decimal representation to transform it into an integer. Here, we
    undo that.
    """
    if decimals != 0:
        return supply / (10 ** decimals)
    return supply

def saveData(data):
    with open(ONCHAIN_DATA_FILENAME, "w") as datafile:
        json.dump(data, datafile)

def loadData():
    with open(ONCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

with open(DATA_SOURCE, newline='') as csvfile:
    datafile = list(csv.reader(csvfile))

REFRESH_ONCHAIN_DATA = True

print("Adding onchain data from csv...")

data = loadData()

dont_update = []
if REFRESH_ONCHAIN_DATA == False:
    for dao in data:
        if "onchain" in dao:
            dont_update.append(dao["name"])

data_to_add = []
data_dao = {}
num_voters = 0
for i in range(1, len(datafile)): # Start from 1 to skip header line of csv
    if "name" in data_dao and data_dao["name"] != datafile[i][1]:
        data_dao["online"]["average_voting_rate_all_time"] /= num_voters
        data_to_add.append(data_dao)
    if "name" not in data_dao or data_dao["name"] != datafile[i][1]:
        data_dao = {}
        data_dao["name"] = datafile[i][1]
        data_dao["average_prices"] = []
        data_dao["average_volumes"] = []
        online_data = {}
        online_data["average_voting_rates"] = []
        online_data["average_inverse_ginis"] = []
        online_data["average_voting_rate_all_time"] = 0
        online_data["average_inverse_gini_all_time"] = 0
        online_data["average_vote_share_authors"] = 0
        online_data["average_vote_share_non_authors"] = 0
        data_dao["online"] = online_data
        num_voters = 0
        supply = unshiftDecimals(float(datafile[i][30]), 16)
    num_voters += 1
    data_dao["online"]["average_voting_rate_all_time"] += float(datafile[i][31])

if num_voters > 0:
    data_dao["online"]["average_voting_rate_all_time"] /= num_voters
    data_to_add.append(data_dao)

for d in data_to_add:
    if not any(d["name"] == dao["name"] for dao in data):
        data.append(d)
    else:
        for i in range(len(data)):
            if data[i]["name"] == d["name"]:
                data[i]["online"] = d["online"]
                break

saveData(data)
