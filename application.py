

#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time
import json

# change IP address for your floodlight configuration
controller_url = "http://127.0.0.1:8080"

try:
    # get all switches in the network
    response = requests.get(controller_url + "/wm/core/controller/switches/json")
    response.raise_for_status()

    json_response = response.json()
    # count switches to iterate the API later
    switch_count = len(json_response)

    links_response = requests.get(controller_url + "/wm/topology/links/json")
    links_response.raise_for_status()
    known_links = links_response.json()

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
			
			filtered_links = list(filter(lambda x: (float(x["src-switch"][-2:]) == switch_id or float(x["dst-switch"][-2:]) == switch_id),known_links))
			down_link = 0
			for link in filtered_links:
			    if float(link["src-switch"][-2:]) == float(switch_id) and float(port["portNumber"]) == float(link["src-port"]):
				down_link = link
			    elif float(link["dst-switch"][-2:]) == float(switch_id) and float(port["portNumber"]) == float(link["dst-port"]):
				down_link = link
			    
			if down_link != 0:
			    # check for possible routes
			    src_dpid = down_link["src-switch"]
			    dst_dpid = down_link["dst-switch"]
			    src_port = down_link["src-port"]
			    dst_port = down_link["dst-port"]
			    max_paths = 10
			    routes_response = requests.get(controller_url + "/wm/routing/paths/fast/{}/{}/{}/json".format(src_dpid, dst_dpid, max_paths))
			    
			    try:			    
				available_routes = json.loads(routes_response.text)
			    except:
				available_routes = 0
				# no paths detected
			    print("AVAILABLE ROUTES: {}".format(available_routes))
			    if available_routes == 0:
				# generate new route
				lelek = 0
            time.sleep(2)

    except HTTPError as http_err:
        print("HTTP error occurred: {}".format(http_err))
    except Exception as err:
        print("Other error occurred: {}".format(err))
