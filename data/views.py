from decouple import config
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import datetime
import json
import logging
import requests

fmt = getattr(settings, 'LOG_FORMAT', None)
lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

logging.basicConfig(format=fmt, level=lvl)
logging.debug(f"Logging started on {logging.root.name} for {logging.getLevelName(lvl)}")

ONCHAIN_DATA_FILENAME = "v2_onchain_data.json"
OFFCHAIN_DATA_FILENAME = "v2_offchain_data.json"

def loadOffchainData():
    with open(OFFCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)
    return data

def loadOnchainData():
    with open(ONCHAIN_DATA_FILENAME, "r") as datafile:
        data = json.load(datafile)

    #for i in range(len(data)):
        #average_voting_rate_all_time = 0
        #dao_data = data[i]
        #for j in range(len(dao_data["average_voting_rates"])):
        #    average_voting_rate_all_time += dao_data["average_voting_rates"][j]
        #average_voting_rate_all_time /= len(dao_data["average_voting_rates"])
        #data[i]["average_voting_rate_all_time"] = average_voting_rate_all_time
        # TODO: Need to perform this calculation here.
        # Template values put in to prevent formatting issues for now.
        #data[i]["average_inverse_ginis"] = [avr / 100 for avr in dao_data["average_voting_rates"]]
        #data[i]["average_inverse_gini_all_time"] = average_voting_rate_all_time / 100

    return data

def index(request):
    data = loadOffchainData()

    onchain_data = loadOnchainData()
    data.extend(onchain_data)

    template = loader.get_template('index.html')
    return HttpResponse(template.render({ "data": data }, request))
