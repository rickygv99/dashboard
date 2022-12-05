from decouple import config
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import datetime
import json
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

def queryMarketData(symbol, period_begin_time, period_end_time):
    period_begin_time = datetime.datetime.utcfromtimestamp(period_begin_time).isoformat()
    period_end_time = datetime.datetime.utcfromtimestamp(period_end_time).isoformat()

    response = requests.get(f"{BASE_URL_COINAPI}/ohlcv/{symbol}/history", params = {
        "period_id": "1DAY",
        "time_start": period_begin_time,
        "time_end": period_end_time,
        "apiKey": COIN_API_KEY
    })
    response = response.json()

    price_sum = 0
    volume_sum = 0
    for period_data in response:
        price_sum += float(period_data["price_open"])
        volume_sum += float(period_data["volume_traded"])
    price_average = price_sum / len(response)
    volume_average = volume_sum / len(response)

    return price_average, volume_average

def queryVotingData(space, supply, period_begin_time, period_end_time):
    response = requests.post(BASE_URL_SNAPSHOT, json={
        "query": '''query Proposals($space: String!, $created_gte: Int!, $created_lte: Int!) {
          proposals(first: 2147483646, skip: 0, where: {created_gte: $created_gte, created_lte: $created_lte, state: "closed", space: $space}) {
            id,
            votes,
            author
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

    num_proposals = len(proposals)
    num_votes = 0
    for p in proposals:
        num_votes += int(p["votes"])
    vote_average = 0
    if num_proposals * supply > 0:
        vote_average = 100 * num_votes / (num_proposals * supply)

    author_vp_average = 0
    non_author_vp_average = 0
    author_vp_sum = 0
    non_author_vp_sum = 0
    author_num = 0
    non_author_num = 0
    for p in proposals:
        response = requests.post(BASE_URL_SNAPSHOT, json={
            "query": '''query Votes($proposal: String!) {
              votes(first: 2147483646, skip: 0, where: {proposal: $proposal}) {
                id,
                voter,
                choice,
                vp
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
            if v['voter'] == p['author']:
                author_vp_sum += v['vp']
                author_num += 1
            else:
                non_author_vp_sum += v['vp']
                non_author_num += 1

    if non_author_num > 0:
        non_author_vp_average = non_author_vp_sum / non_author_num
    if author_num > 0:
        author_vp_average = author_vp_sum / author_num

    return vote_average, num_votes, num_proposals, author_vp_sum, non_author_vp_sum # Sum, not average is intentional

def calculateGiniCoefficient(num_proposals, supply, num_votes):
    n = num_proposals * supply
    y = num_votes

    # Undefined Gini Coefficient
    if n == 0 or y == 0:
        return -1

    gini = (n + 1 - 2 * (y * (n + 1) - n * (n + 1) / 2 + (n - y) * (n - y + 1) / 2) / y) / n

    return gini

def calculateInverseGiniCoefficient(num_proposals, supply, num_votes):
    inverse_gini = 1 - calculateGiniCoefficient(num_proposals, supply, num_votes)

    if inverse_gini < 0 or inverse_gini > 1: # Undefined Inverse Gini Coefficient
        inverse_gini = 0

    return inverse_gini

def querySingleDao(dao):
    address = dao["address"]
    decimals = dao["decimals"]
    space = dao["snapshot_space"]
    symbol = dao["coinapi_symbol"]

    supply = queryTotalSupply(address, decimals)

    average_prices = []
    average_volumes = []
    average_voting_rates = []
    average_inverse_ginis = []
    total_votes = 0
    total_proposals = 0
    sum_vp_author = 0
    sum_vp_non_author = 0
    for j in range(NUM_PERIODS):
        period_begin_time = START_TIME + j * PERIOD
        period_end_time = START_TIME + (j + 1) * PERIOD - 1

        if symbol != "":
            price_average, volume_average = queryMarketData(symbol, period_begin_time, period_end_time)
            average_prices.append(price_average)
            average_volumes.append(volume_average)

        voting_rate_average, num_votes, num_proposals, author_vp_sum, non_author_vp_sum = queryVotingData(space, supply, period_begin_time, period_end_time)
        average_voting_rates.append(voting_rate_average)
        total_votes += num_votes
        total_proposals += num_proposals

        inverse_gini_average = calculateInverseGiniCoefficient(num_proposals, supply, num_votes)
        average_inverse_ginis.append(inverse_gini_average)

        sum_vp_author += author_vp_sum
        sum_vp_non_author += non_author_vp_sum

    average_vote_share_authors = 0
    average_vote_share_non_authors = 0
    if supply > 0:
        average_vote_share_authors = sum_vp_author / supply
        average_vote_share_non_authors = sum_vp_non_author / supply

    average_voting_rate_all_time = 0
    if total_proposals * supply > 0:
        average_voting_rate_all_time = 100 * total_votes / (total_proposals * supply)
    average_inverse_gini_all_time = calculateInverseGiniCoefficient(total_proposals, supply, total_votes)

    return average_prices, average_volumes, average_voting_rates, average_inverse_ginis, average_voting_rate_all_time, average_inverse_gini_all_time, average_vote_share_authors, average_vote_share_non_authors

def queryAllDaos(dao_data):
    data = []
    for dao in dao_data:
        print(f"Querying data for DAO : {dao['name']}")
        average_prices, average_volumes, average_voting_rates, average_inverse_ginis, average_voting_rate_all_time, average_inverse_gini_all_time, average_vote_share_authors, average_vote_share_non_authors = querySingleDao(dao)

        data_dao = {}
        data_dao["name"] = dao["name"]
        data_dao["average_prices"] = average_prices
        data_dao["average_volumes"] = average_volumes
        data_dao["average_voting_rates"] = average_voting_rates
        data_dao["average_inverse_ginis"] = average_inverse_ginis
        data_dao["average_voting_rate_all_time"] = average_voting_rate_all_time
        data_dao["average_inverse_gini_all_time"] = average_inverse_gini_all_time
        data_dao["average_vote_share_authors"] = average_vote_share_authors
        data_dao["average_vote_share_non_authors"] = average_vote_share_non_authors
        data.append(data_dao)

    return data

OFFCHAIN_DATA_FILENAME = "v2_offchain_data.json"

def saveOffchainData(data):
    with open(OFFCHAIN_DATA_FILENAME, "w") as datafile:
        json.dump(data, datafile)

def loadOffchainData():
    with open(OFFCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

REFRESH_OFFCHAIN_DATA = False

print("Beginning data queries...")

data = []

if REFRESH_OFFCHAIN_DATA:
    data = queryAllDaos(DAO_DATA)
else:
    data = loadOffchainData()

    daos_to_query = []
    for dao in DAO_DATA:
        if len(daos_to_query) > 7: # We get rate-limited if too many requests at once, better to split them up
            break
        if not any(d['name'] == dao['name'] for d in data):
            daos_to_query.append(dao)

    new_data = queryAllDaos(daos_to_query)
    data.extend(new_data)

saveOffchainData(data)
