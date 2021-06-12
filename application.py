#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time
import json
import traceback
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

def get_src_port(src, dst):
        src = '00:00:00:00:00:00:00:{:0>2}'.format(src)
        dst = '00:00:00:00:00:00:00:{:0>2}'.format(dst)
        for link in known_links:
                if link["src-switch"] == src and link["dst-switch"] == dst:
                        return link['src-port']
                if link["src-switch"] == dst and link["dst-switch"] == src:
                        return link['dst-port']

def modify_flow(switch_id, name, in_port, actions, priority):
        new_flow = {
                    'switch':"00:00:00:00:00:00:00:{:0>2}".format(switch_id),
                    "name": name,
                    "cookie":"0",
                    "priority": priority,
                    "in_port": in_port,
                    "active":"true",
                    "actions": actions
                    }

        #r = requests.get(controller_url + '/wm/staticflowpusher/clear/00:00:00:00:00:00:00:{:0>2}/json'.format(switch_id))
        #r.raise_for_status()

        r = requests.post(controller_url + "/wm/staticflowpusher/json", data=json.dumps(new_flow))
        print("Flow added with status code {} to switch {} in_port {} action {}".format(r.status_code, switch_id, in_port, actions))
        r.raise_for_status()

def update_flows(path):
        for i, node in enumerate(path):
                if i == 0 or i == len(path) - 1:

                        r = requests.get(controller_url + "/wm/staticflowpusher/list/{}/json".format(node))
                        r.raise_for_status()
                        
                        flows = r.json()

                        if i == 0:
                                old_out_port = get_src_port(node, path[-1])
                                for flow in flows[node]:
                                        flow = list(flow.values())[0]
                                        if flow['instructions']['instruction_apply_actions']['actions'] == 'output={}'.format(old_out_port):
                                                in_port = flow['match']['in_port']
                                                out_port = get_src_port(node, path[i+1])
                                                modify_flow(node, 'rest_flow_mod_{}_start'.format(node), in_port, "output={}".format(out_port), "1")
                        
                        elif i == len(path) - 1:
                                old_in_port = get_src_port(node, path[0])
                                print("Old in port " + str(old_in_port))
                                for flow in flows[node]:
                                        flow = list(flow.values())[0]
                                        if flow['match']['in_port'] == str(old_in_port):
                                                actions = flow['instructions']['instruction_apply_actions']['actions'] 
                                                in_port = get_src_port(node, path[i-1])
                                                modify_flow(node, 'rest_flow_mod_{}_end'.format(node), in_port , actions, "1")

                else:
                        in_port = get_src_port(node, path[i-1])
                        out_port = get_src_port(node, path[i+1])
                        modify_flow(node, 'rest_flow_mod_{}_{}'.format(node, path[i+1]), in_port, "output={}".format(out_port), "1")
                         
                        

                                
                
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

restored = []
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
						if port['name'] not in restored:
							for link in known_links:
								if int(link["src-switch"][-2:]) == switch_id and int(port["portNumber"]) == link["src-port"]:
									graph = update_graph()
								
									print("Finding path from {} to {}".format(str(switch_id), str(int(link["dst-switch"][-2:]))))
									path = find_path(graph,str(switch_id), str(int(link["dst-switch"][-2:])))
									print(path)
									update_flows(path[0])
									restored.append(port["name"])
									break

								elif int(link["dst-switch"][-2:]) == switch_id and int(port["portNumber"]) == link["dst-port"]:
									graph = update_graph()
								
									print("Finding path from {} to {}".format(str(switch_id), str(int(link["src-switch"][-2:]))))
									path = find_path(graph,str(switch_id), str(int(link["src-switch"][-2:])))
									print(path)
									update_flows(path[0])
									restored.append(port["name"])
									break
			time.sleep(1)

	except HTTPError as http_err:
		print("HTTP error occurred: {}".format(http_err))
	except Exception as err:
		print(traceback.format_exc())
