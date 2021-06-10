#!/usr/bin/python

import httplib
import json
  
class StaticFlowPusher(object):
  
    def __init__(self, server):
        self.server = server
  
    def get(self, data):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])
  
    def set(self, data):
        ret = self.rest_call(data, 'POST')
        return ret[0] == 200
  
    def remove(self, objtype, data):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200
  
    def rest_call(self, data, action):
        path = '/wm/staticflowpusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }
        body = json.dumps(data)
        conn = httplib.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        print ret
        conn.close()
        return ret
    
    def clear_tables(self):
        # get switch count to iterate the API
        switch_count = 7
        conn = httplib.HTTPConnection(self.server, 8080)
        
        # clear flow table for each switch
        for id in range(1,switch_count + 1):
            conn.request('GET', '/wm/staticflowpusher/clear/00:00:00:00:00:00:00:0{}/json'.format(id))
            response = conn.getresponse()
            ret = (response.status, response.reason, response.read())
            print ret
            conn.close()
    
  
pusher = StaticFlowPusher('127.0.0.1')

# static path: h1 <-> s1 <-> s2 <-> s6 <-> s7 <-> h2

# switch 1
flow1 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_1",
    "cookie":"0",
    "priority":"32768",
    "in_port":"3",
    "active":"true",
    "actions":"output=1"
    }
  
flow2 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_2",
    "cookie":"0",
    "priority":"32768",
    "in_port":"1",
    "active":"true",
    "actions":"output=3"
    }

# switch 2
flow3 = {
    'switch':"00:00:00:00:00:00:00:02",
    "name":"flow_mod_3",
    "cookie":"0",
    "priority":"32768",
    "in_port":"1",
    "active":"true",
    "actions":"output=3"
    }

flow4 = {
    'switch':"00:00:00:00:00:00:00:02",
    "name":"flow_mod_4",
    "cookie":"0",
    "priority":"32768",
    "in_port":"3",
    "active":"true",
    "actions":"output=1"
    }

# switch 6
flow5 = {
    'switch':"00:00:00:00:00:00:00:06",
    "name":"flow_mod_5",
    "cookie":"0",
    "priority":"32768",
    "in_port":"1",
    "active":"true",
    "actions":"output=4"
    }

flow6 = {
    'switch':"00:00:00:00:00:00:00:06",
    "name":"flow_mod_6",
    "cookie":"0",
    "priority":"32768",
    "in_port":"4",
    "active":"true",
    "actions":"output=1"
    }

# switch 7
flow7 = {
    'switch':"00:00:00:00:00:00:00:07",
    "name":"flow_mod_7",
    "cookie":"0",
    "priority":"32768",
    "in_port":"3",
    "active":"true",
    "actions":"output=2"
    }

flow8 = {
    'switch':"00:00:00:00:00:00:00:07",
    "name":"flow_mod_8",
    "cookie":"0",
    "priority":"32768",
    "in_port":"2",
    "active":"true",
    "actions":"output=3"
    }

# clear flow tables and push new flows
pusher.clear_tables()
pusher.set(flow1)
pusher.set(flow2)
pusher.set(flow3)
pusher.set(flow4)
pusher.set(flow5)
pusher.set(flow6)
pusher.set(flow7)
pusher.set(flow8)