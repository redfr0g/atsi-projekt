#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time

# change IP address for your floodlight configuration
controller_url = "http://192.168.211.129:8080"

try:
    # get all switches in the network
    response = requests.get(controller_url + "/wm/core/controller/switches/json")
    response.raise_for_status()

    json_response = response.json()
    # count switches to iterate the API later
    switch_count = len(json_response)

except HTTPError as http_err:
    print("HTTP error occurred: {}".format(http_err))
except Exception as err:
    print("Other error occurred: {}".format(err))

while True:
    try:
        # get ports description for each switch
        for switch_id in range(1,switch_count):
            
            response = requests.get(controller_url + "/wm/core/switch/{}/port-desc/json".format(switch_id))
            response.raise_for_status()

            json_response = response.json()
            for port in json_response["portDesc"]:
                # if the port is local do nothing
                if port["portNumber"] == "local":
                    continue
                else:
                    # 1 - port is DOWN, 0 - port is UP
                    if port["state"] == "0":
                        print("Port {} is UP".format(port["name"]))
                    else:
                        # handle restoratation method here
                        print("Port {} is DOWN".format(port["name"]))
            time.sleep(2)

    except HTTPError as http_err:
        print("HTTP error occurred: {}".format(http_err))
    except Exception as err:
        print("Other error occurred: {}".format(err))
