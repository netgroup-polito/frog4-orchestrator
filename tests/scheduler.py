'''
Created on 03 dic 2015

@author: stefanopetrangeli
'''
import requests, json, logging
from orchestrator_core.config import Configuration
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG

username = 'AdminPoliTO'
password = 'AdminPoliTO'
tenant = 'PoliTO_chain1'

conf = Configuration()

# set log level
if conf.DEBUG is True:
    log_level = logging.DEBUG
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
    sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_log.setLevel(logging.WARNING)
elif conf.VERBOSE is True:
    log_level = logging.INFO
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
else:
    log_level = logging.WARNING

log_format = '%(asctime)s %(levelname)s %(message)s - %(filename)s'

logging.basicConfig( filename="../"+conf.LOG_FILE, level=log_level, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug("Orchestrator Starting")


#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0_AR.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo1.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo2.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo3_4vnf.json","r")
nf_fg_file ={"forwarding-graph":{"id":"00000004","name":"Forwarding graph","VNFs":[{"vnf_template":"example.json","id":"00000001","name":"Client function","ports":[{"id":"inout:0","name":"data-port"},{"id":"inout:1","name":"data-port"}]},{"vnf_template":"example.json","id":"00000002","name":"Server function","ports":[{"id":"inout:0","name":"data-port"},{"id":"inout:1","name":"data-port"}]},{"vnf_template":"example.json","id":"00000003","name":"Client function","ports":[{"id":"inout:0","name":"data-port"},{"id":"inout:1","name":"data-port"}]},{"vnf_template":"example.json","id":"00000004","name":"Server function","ports":[{"id":"inout:0","name":"data-port"},{"id":"inout:1","name":"data-port"},{"id":"inout:2","name":"data-port"}]}],"end-points":[{"id":"00000001","name":"user","type":"interface","interface":{"node":"10.0.0.1","interface":"eth0"}},{"id":"00000002","name":"egress","type":"internal"}],"big-switch":{"flow-rules":[{"id":"000000001","priority":2,"match":{"port_in":"endpoint:00000001","protocol":"tcp"},"actions":[{"output":"vnf:00000001:inout:0"}]},{"id":"000000003","priority":1,"match":{"port_in":"endpoint:00000001","protocol":"udp"},"actions":[{"output":"vnf:00000002:inout:0"}]},{"id":"000000002","priority":2,"match":{"port_in":"vnf:00000001:inout:0","protocol":"tcp"},"actions":[{"output":"endpoint:00000001"}]},{"id":"000000004","priority":1,"match":{"port_in":"vnf:00000002:inout:0","protocol":"udp"},"actions":[{"output":"endpoint:00000001"}]},{"id":"000000005","priority":2,"match":{"port_in":"vnf:00000001:inout:1","protocol":"tcp"},"actions":[{"output":"vnf:00000003:inout:0"}]},{"id":"000000006","priority":1,"match":{"port_in":"vnf:00000003:inout:0","protocol":"tcp"},"actions":[{"output":"vnf:00000001:inout:1"}]},{"id":"000000007","priority":2,"match":{"port_in":"vnf:00000002:inout:1","protocol":"udp"},"actions":[{"output":"vnf:00000004:inout:0"}]},{"id":"000000008","priority":1,"match":{"port_in":"vnf:00000004:inout:0","protocol":"udp"},"actions":[{"output":"vnf:00000002:inout:1"}]},{"id":"000000009","priority":2,"match":{"port_in":"vnf:00000003:inout:1","protocol":"tcp"},"actions":[{"output":"endpoint:00000002"}]},{"id":"000000010","priority":1,"match":{"port_in":"endpoint:00000002","protocol":"tcp"},"actions":[{"output":"vnf:00000003:inout:1"}]},{"id":"000000011","priority":2,"match":{"port_in":"vnf:00000004:inout:1","protocol":"udp"},"actions":[{"output":"endpoint:00000002"}]},{"id":"000000012","priority":1,"match":{"port_in":"endpoint:00000002","protocol":"udp"},"actions":[{"output":"vnf:00000004:inout:1"}]}]}}}

#a= in_file.read()
#nf_fg_file = json.loads(a)

ValidateNF_FG().validate(nf_fg_file)
nffg = NF_FG()
nffg.parseDict(nf_fg_file)


controller = UpperLayerOrchestratorController(user_data=UserData(username, password, tenant))
controller.put(nffg)
#controller.delete(51)
#controller.delete(250)
#controller.delete(52)
#controller.delete(200)
#controller.delete(201)

print('Job completed')
exit()

orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG/"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, json.dumps(nf_fg_file), headers=headers)
#requests.delete(orchestrator_endpoint, headers=headers)

print('Job completed')
