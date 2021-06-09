#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time
import json
from dijkstar import Graph, find_path # pip3 install dijkstar; pip3 install --ignore-installed six


def update_graph():
	# get updated links
	try:
		links_response_updated = requests.get(controller_url + "/wm/topology/links/json")
		links_response_updated.raise_for_status()
		known_links_updated = links_response_updated.json()
	except HTTPError as http_err:
		print("HTTP error occurred: {}".format(http_err))
	except Exception as err:
		print("Other error occurred: {}".format(err))

	# create new network graph
	graph = Graph()
	for link in known_links_updated:
		dst_id = "{}".format(int(link["dst-switch"][-2:]))
		src_id = "{}".format(int(link["src-switch"][-2:]))
		graph.add_edge(dst_id, src_id, 1)
		graph.add_edge(src_id, dst_id, 1)

	return graph


# change ip address for your floodlight configuration
controller_url = "http://127.0.0.1:8080"

try:
	# get all switches in the network
	response = requests.get(controller_url + "/wm/core/controller/switches/json")
	response.raise_for_status()
	json_response = response.json()
	
	# count switches to iterate the API later
	switch_count = len(json_response)

	# get initial links
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
		for switch_id in range(1,switch_count+1):
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
						
						for link in known_links:
							if int(link["src-switch"][-2:]) == switch_id and int(port["portNumber"]) == link["src-port"]:
								graph = update_graph()
								
								print("Finding path from {} to {}".format(str(switch_id), str(int(link["dst-switch"][-2:]))))
								path = find_path(graph,str(switch_id), str(int(link["dst-switch"][-2:])))
								print(path)
								break

							elif int(link["dst-switch"][-2:]) == switch_id and int(port["portNumber"]) == link["dst-port"]:
								graph = update_graph()
								
								print("Finding path from {} to {}".format(str(switch_id), str(int(link["src-switch"][-2:]))))
								path = find_path(graph,str(switch_id), str(int(link["src-switch"][-2:])))
								print(path)
								break
			time.sleep(1)

	except HTTPError as http_err:
		print("HTTP error occurred: {}".format(http_err))
	except Exception as err:
		print("Other error occurred: {}".format(err))
