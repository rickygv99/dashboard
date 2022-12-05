from django.conf import settings
import json
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

OFFCHAIN_DATA_FILENAME = "v2_offchain_data.json"

def saveOffchainData(data):
    with open(OFFCHAIN_DATA_FILENAME, "w") as datafile:
        json.dump(data, datafile)

def loadOffchainData():
    with open(OFFCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

print("Performing PCA...")

NUM_COMPONENTS = 2

data = loadOffchainData()

feature_matrix = []
dao_names = []
for dao in data:
    # Right now, we don't have enough dimensions for a DAO's data if we don't
    # have market data for that DAO
    if len(dao["average_prices"]) == 0 or len(dao["average_volumes"]) == 0:
        continue

    dao_names.append(dao["name"])
    dao_features = dao["average_voting_rates"] + dao["average_prices"] + dao["average_volumes"]
    feature_matrix.append(dao_features)

feature_matrix = np.array(feature_matrix)
feature_matrix_df = pd.DataFrame(feature_matrix)

feature_matrix_df_std = (feature_matrix_df - feature_matrix_df.mean()) / feature_matrix_df.std()

pca = PCA(n_components=NUM_COMPONENTS)
principal_components = pca.fit_transform(feature_matrix_df_std)
principal_df = pd.DataFrame(data=principal_components)
principal_df.index = dao_names

for i in range(len(data)):
    if len(data[i]['average_prices']) == 0 or len(data[i]["average_volumes"]) == 0:
        data[i]["components"] = []
        continue

    df_row = principal_df.loc[[data[i]["name"]]]
    data[i]['components'] = [df_row.iat[0, 0], df_row.iat[0, 1]]

saveOffchainData(data)
