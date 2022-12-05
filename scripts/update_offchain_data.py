import json

OFFCHAIN_DATA_FILENAME = "v2_offchain_data.json"

def saveOffchainData(data):
    with open(OFFCHAIN_DATA_FILENAME, "w") as datafile:
        json.dump(data, datafile)

def loadOffchainData():
    with open(OFFCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

print(f"Updating DAO data...")

data = loadOffchainData()

for i in range(len(data)):
    data[i]["onchain"] = 0

saveOffchainData(data)
