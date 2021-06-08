

#!/usr/bin/python

import requests
from requests.exceptions import HTTPError
import time
import json



# Path calculations based on initially known topology and down links
# topology: graph created at the beginning of this script
# down_links: entire link row from "/wm/topology/links/json" enpoint
def shortest_path(topology, down_links):
    working_topology = dict(topology)
    for link in down_links:
        src_switch = "S{}".format(int(link["src-switch"][-2:]))
        src_port = link["src-port"]
	dst_switch = "S{}".format(int(link["dst-switch"][-2:]))
	dst_port = link["dst-port"]
	
	src_neighbours = working_topology[src_switch]
	for id, items in src_neighbours.items():
	    start_port, end_port, weight = items
	    if start_port == src_port and end_port == dst_port:
  	        del working_topology[src_switch][dst_switch]
	
	dst_neighbours = working_topology[dst_switch]
	for id, items in dst_neighbours.items():
	    start_port, end_port, weight = items
	    if start_port == src_port and end_port == dst_port:
		del working_topology[dst_switch][src_switch]

    # calculate shortest path   
    dijkstra_graph = {}
    for node, values in working_topology.items():
	dijkstra_graph[node] = {}
	for neighbour, items in values.items():
	    start, end, weight = items 
	    dijkstra_graph[node][neighbour] = weight
    path = dijkstra(dijkstra_graph, "S1", "S7")
    print(path)
	 

# https://stackoverflow.com/a/37237712
# Dijkstra

def get_parent(pos):
    return (pos + 1) // 2 - 1


def get_children(pos):
    right = (pos + 1) * 2
    left = right - 1
    return left, right


def swap(array, a, b):
    array[a], array[b] = array[b], array[a]


class Heap:

    def __init__(self):
        self._array = []

    def peek(self):
        return self._array[0] if self._array else None

    def _get_smallest_child(self, parent):
        return min([
            it
            for it in get_children(parent)
            if it < len(self._array)
        ], key=lambda it: self._array[it], default=-1)

    def _sift_down(self):
        parent = 0
        smallest = self._get_smallest_child(parent)
        while smallest != -1 and self._array[smallest] < self._array[parent]:
            swap(self._array, smallest, parent)
            parent, smallest = smallest, self._get_smallest_child(smallest)

    def pop(self):
        if not self._array:
            return None
        swap(self._array, 0, len(self._array) - 1)
        node = self._array.pop()
        self._sift_down()
        return node

    def _sift_up(self):
        index = len(self._array) - 1
        parent = get_parent(index)
        while parent != -1 and self._array[index] < self._array[parent]:
            swap(self._array, index, parent)
            index, parent = parent, get_parent(parent)

    def add(self, item):
        self._array.append(item)
        self._sift_up()

    def __bool__(self):
        return bool(self._array)


def backtrack(best_parents, start, end):
    if end not in best_parents:
        return None
    cursor = end
    path = [cursor]
    while cursor in best_parents:
        cursor = best_parents[cursor]
        path.append(cursor)
        if cursor == start:
            return list(reversed(path))
    return None


def dijkstra(weighted_graph, start, end):
    """
    Calculate the shortest path for a directed weighted graph.

    Node can be virtually any hashable datatype.

    :param start: starting node
    :param end: ending node
    :param weighted_graph: {"node1": {"node2": weight, ...}, ...}
    :return: ["START", ... nodes between ..., "END"] or None, if there is no
            path
    """
    distances = {i: float("inf") for i in weighted_graph}
    best_parents = {i: None for i in weighted_graph}

    to_visit = Heap()
    to_visit.add((0, start))
    distances[start] = 0

    visited = set()

    while to_visit:
        src_distance, source = to_visit.pop()
        if src_distance > distances[source]:
            continue
        if source == end:
            break
        visited.add(source)
        for target, distance in weighted_graph[source].items():
            if target in visited:
                continue
            new_dist = distances[source] + weighted_graph[source][target]
            if distances[target] > new_dist:
                distances[target] = new_dist
                best_parents[target] = source
                to_visit.add((new_dist, target))

    return backtrack(best_parents, start, end)




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
    topology_graph = {} # element: <switch_id>: {<dst_switch>: (<src_port>, <dst_port>, <weight>), <dst_switch>: (...)}
    for switch_id in range(1,switch_count+1):
        topology_graph["S{}".format(switch_id)] = {}
    for link in known_links:
        dst_id = "S{}".format(int(link["dst-switch"][-2:]))
        dst_port = int(link["dst-port"])
        src_id = "S{}".format(int(link["src-switch"][-2:]))
        src_port = int(link["src-port"])
        topology_graph[dst_id][src_id] = (dst_port, src_port, 1) # weights set to 1 to simplify the program
        topology_graph[src_id][dst_id] = (src_port, dst_port, 1) 

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
				shortest_path(topology_graph, [link])
				break
			    elif int(link["dst-switch"][-2:]) == switch_id and int(port["portNumber"]) == link["dst-port"]:
				shortest_path(topology_graph, [link])
				break
            time.sleep(2)

    except HTTPError as http_err:
        print("HTTP error occurred: {}".format(http_err))
    except Exception as err:
        print("Other error occurred: {}".format(err))
