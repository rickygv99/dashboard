from decouple import config
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import csv
import datetime
import json
import os
import requests

from dao_ids import DAO_DATA

ETHERSCAN_API_KEY = config('ETHERSCAN_API_KEY')
COIN_API_KEY = config('COIN_API_KEY')

BASE_URL_SNAPSHOT = "https://hub.snapshot.org/graphql"
BASE_URL_ETHERSCAN = "https://api.etherscan.io/api"
BASE_URL_COINAPI = "https://rest.coinapi.io/v1"

START_TIME = 1640995200 # January 1, 2022 in Unix time (seconds)
PERIOD = 2592000 # 30 days in seconds
NUM_PERIODS = 5

def unshiftDecimals(supply, decimals):
    """
    Etherscan returns the total token supply shifted by their smallest
    decimal representation to transform it into an integer. Here, we
    undo that.
    """
    if decimals != 0:
        return supply / (10 ** decimals)
    return supply

def queryTotalSupply(address, decimals):
    response = requests.get(BASE_URL_ETHERSCAN, params = {
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": address,
        "apikey": ETHERSCAN_API_KEY
    })
    response = response.json()

    supply = int(response["result"])
    unshifted_supply = unshiftDecimals(supply, decimals)

    return unshifted_supply

def queryVotingData(name, space, supply, period_begin_time, period_end_time):
    response = requests.post(BASE_URL_SNAPSHOT, json={
        "query": '''query Proposals($space: String!, $created_gte: Int!, $created_lte: Int!) {
          proposals(first: 2147483646, skip: 0, where: {created_gte: $created_gte, created_lte: $created_lte, state: "closed", space: $space}) {
            id,
            created,
            start,
            end,
            author,
            choices
          }
        }
        ''',
        "variables": {
            "space": space,
            "created_gte": period_begin_time,
            "created_lte": period_end_time
        }
    })
    response = response.json()
    proposals = response["data"]["proposals"]

    fields = ['DAO Name', 'DAO Token Supply', 'Offchain?', 'Proposal ID', 'Proposal Date Created', 'Proposal Date Start', 'Proposal Date End', 'Proposal Author', 'Proposal Choices', 'Voter Address', 'Voter Choice', 'Voter Power', 'Voter Reason', 'Transaction Hash']
    data = []

    for p in proposals:
        response = requests.post(BASE_URL_SNAPSHOT, json={
            "query": '''query Votes($proposal: String!) {
              votes(first: 2147483646, skip: 0, where: {proposal: $proposal}) {
                id,
                voter,
                choice,
                vp,
                reason
              }
            }
            ''',
            "variables": {
                "proposal": p['id']
            }
        })
        response = response.json()
        votes = response["data"]["votes"]

        for v in votes:
            data.append([
                name,
                supply,
                1,
                p['id'],
                p['created'],
                p['start'],
                p['end'],
                p['author'],
                p['choices'],
                v['voter'],
                v['choice'],
                v['vp'],
                v['reason'],
                None
            ])

    return fields, data

def querySingleDao(dao):
    name = dao["name"]
    address = dao["address"]
    decimals = dao["decimals"]
    space = dao["snapshot_space"]

    supply = queryTotalSupply(address, decimals)

    period_begin_time = START_TIME
    period_end_time = START_TIME + NUM_PERIODS * PERIOD - 1

    fields, data = queryVotingData(name, space, supply, period_begin_time, period_end_time)

    return fields, data

print("Beginning data queries...")

for dao in DAO_DATA:
    if f"{dao['snapshot_space']}.csv" in os.listdir("paper_data/"):
        continue

    print(f"Querying DAO {dao['name']}")

    fields, data = querySingleDao(dao)

    with open(f"paper_data/{dao['snapshot_space']}.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(data)
