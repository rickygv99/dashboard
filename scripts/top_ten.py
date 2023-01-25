import json
import csv
from operator import itemgetter

DATA_SOURCE = "onchain.csv"
ONCHAIN_DATA_FILENAME = "v2_onchain_data.json"

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
address_power = {}
yes_vote_shares = {}
for i in range(1, len(datafile)): # Start from 1 to skip header line of csv
    if "name" in data_dao and data_dao["name"] != datafile[i][1] + " (Online)":
        data_dao["average_voting_rate_all_time"] /= num_voters

        sorted_addresses = sorted(address_power.items(), key=itemgetter(1), reverse=True)
        end_idx = min(10, len(sorted_addresses))
        top_ten_addresses = dict(sorted_addresses[:end_idx])
        data_dao["top_ten_power"] = sum([float(k) for k in top_ten_addresses.values()])
        address_power = {}

        data_dao["yes_vote_shares"] = [min(k[0]/k[1], 0.999) for k in yes_vote_shares.values() if k[1] != 0]
        yes_vote_shares = {}

        data_to_add.append(data_dao)
    if "name" not in data_dao or data_dao["name"] != datafile[i][1] + " (Online)":
        data_dao = {}
        data_dao["name"] = datafile[i][1] + " (Online)"
        data_dao["average_prices"] = []
        data_dao["average_volumes"] = []
        data_dao["average_voting_rates"] = []
        data_dao["average_inverse_ginis"] = []
        data_dao["average_voting_rate_all_time"] = 0
        data_dao["average_inverse_gini_all_time"] = 0
        data_dao["average_vote_share_authors"] = 0
        data_dao["average_vote_share_non_authors"] = 0
        data_dao["top_ten_power"] = 0
        data_dao["yes_vote_shares"] = []
        data_dao["onchain"] = 1
        num_voters = 0
        supply = unshiftDecimals(float(datafile[i][30]), 16)
    num_voters += 1
    data_dao["average_voting_rate_all_time"] += float(datafile[i][31])
    address_power[datafile[i][3]] = float(datafile[i][31])
    if datafile[i][12] in yes_vote_shares:
        yes_vote_shares[datafile[i][12]][0] += float(datafile[i][22])
        yes_vote_shares[datafile[i][12]][1] += float(datafile[i][24])
    elif datafile[i][22] != "" and datafile[i][24] != "":
        yes_vote_shares[datafile[i][12]] = [float(datafile[i][22]), float(datafile[i][24])]

if num_voters > 0:
    data_dao["average_voting_rate_all_time"] /= num_voters
    data_to_add.append(data_dao)

for d in data_to_add:
    if not any(d["name"] + " (Online)" == dao["name"] for dao in data):
        data.append(d)
    else:
        for i in range(len(data)):
            if data[i]["name"] == d["name"] + " (Online)":
                data[i]["online"] = d["online"]
                break

saveData(data)
