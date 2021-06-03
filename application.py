#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time

# Change IP address for your floodlight configuration
controller_url = "http://192.168.174.129:8080"
current_links = 0

try:
    response = requests.get(controller_url + "/wm/core/controller/summary/json")
    response.raise_for_status()

    json_response = response.json()
    current_links = json_response["# inter-switch links"]

except HTTPError as http_err:
    print('HTTP error occurred: {}'.format(http_err))
except Exception as err:
    print('Other error occurred: {}'.format(err))


while True:
    try:
        response = requests.get(controller_url + "/wm/core/controller/summary/json")
        response.raise_for_status()

        json_response = response.json()
        if json_response["# inter-switch links"] < current_links:
            print("Detected link malfunction!")
            exit()
        else:
            time.sleep(1)
            continue

    except HTTPError as http_err:
        print('HTTP error occurred: {}'.format(http_err))
    except Exception as err:
        print('Other error occurred: {}'.format(err))
