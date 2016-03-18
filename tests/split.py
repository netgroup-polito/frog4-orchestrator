'''
Created on 16 nov 2015

@author: stefanopetrangeli
'''
import requests, json, logging
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.scheduler import Scheduler
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG


#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0_AR.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo1.json","r")
#in_file = open("../../frog4/grafo2.json","r")
in_file = open("../../frog4/grafo3_4vnf.json","r")
in_file = open("../../frog4/grafo_ivano.json","r")
in_file = open("../../frog4/UNs_jolnet/candidate.json","r")


nf_fg_file = json.loads(in_file.read())
#nf_fg_file = {"forwarding-graph":{"id":"2","name":"Forwarding graph","VNFs":[{"vnf_template":"example.json","id":"00000001","name":"Client function","ports":[{"id":"inout:0","name":"data-port"}],"domain":"bella"}],"end-points":[{"id":"00000001","name":"user","type":"interface","interface":{"node-id":"10.1.1.1","interface":"eth0"},"domain":"bella"}],"big-switch":{"flow-rules":[{"id":"000000001","priority":2,"match":{"port_in":"endpoint:00000001"},"actions":[{"output_to_port":"vnf:00000001:inout:0"}]},{"id":"000000002","priority":1,"match":{"port_in":"vnf:00000001:inout:0"},"actions":[{"output_to_port":"endpoint:00000001"}]}]}}}

ValidateNF_FG().validate(nf_fg_file)
nffg = NF_FG()
nffg.parseDict(nf_fg_file)
print(nffg.getJSON())
#nffg1, nffg2 = nffg.split(nffg.end_points, nffg.vnfs) # for graph 0,2

# 3
"""
left = []
left.append(nffg.end_points[0])
nffg1, nffg2 = nffg.split(left, nffg.vnfs) # for graph 3
"""

left = []
left.append(nffg.end_points[0])
left.append(nffg.end_points[1])
left.append(nffg.end_points[2])
right= []
right.append(nffg.vnfs[0])
nffg1, nffg2 = nffg.split(left, right) # for graph 3


"""
left = []
left.append(nffg.vnfs[0])
left.append(nffg.vnfs[1])
right= []
right.append(nffg.vnfs[2])
nffg1, nffg2 = nffg.split(left, right) # for graph1 or 3 
"""

print(nffg1.getJSON())
print(nffg2.getJSON())
"""
left = []
left.append(nffg1.end_points[0])
right= []
right.append(nffg1.vnfs[0])
right.append(nffg1.vnfs[1])
nffg3, nffg4 = nffg1.split(left, right) # for graph1 or 3 

print(nffg3.getJSON())
print(nffg4.getJSON())

#nffg3.join(nffg4)
#print nffg3.getJSON()
nffg4.join(nffg3)
print(nffg4.getJSON())
"""


#nffg1.join(nffg2)
#print nffg1.getJSON()
#print nffg2.getJSON()


print('Job completed')