'''
Created on Oct 30, 2015

@author: fabiomignini
'''
import requests, logging, json, os
os.environ.setdefault("FROG4_ORCH_CONF", "config/onos_demo_config.ini")
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.userAuthentication import UserData
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
sqlalchemy_log.setLevel(logging.WARNING)

username = 'admin'
password = 'qwerty'
tenant = 'admin_tenant'
nffg_json = '{"forwarding-graph":{"name":"simple-nat-graph","VNFs":[{"name":"nat","ports":[{"name":"data-port","id":"USER:0"},{"name":"data-port","id":"WAN:0"}],"id":"00000001","vnf_template":"isp_nat.json"}],"id":"12","end-points":[{"type":"interface","interface":{"if-name":"s2-eth1","node-id":"of:0000000000000002"},"id":"00000001","domain":"onos_domain"},{"type":"interface","interface":{"if-name":"s3-eth1","node-id":"of:0000000000000003"},"id":"00000002","domain":"onos_domain"}],"big-switch":{"flow-rules":[{"match":{"port_in":"endpoint:00000002"},"actions":[{"output_to_port":"vnf:00000001:WAN:0"}],"priority":40001,"id":"000000001"},{"match":{"port_in":"vnf:00000001:WAN:0"},"actions":[{"output_to_port":"endpoint:00000002"}],"priority":40001,"id":"000000002"},{"match":{"port_in":"endpoint:00000001"},"actions":[{"output_to_port":"vnf:00000001:USER:0"}],"priority":40001,"id":"000000003"},{"match":{"port_in":"vnf:00000001:USER:0"},"actions":[{"output_to_port":"endpoint:00000001"}],"priority":40001,"id":"000000004"}]}}}'
nffg_dict = json.loads(nffg_json)

ValidateNF_FG().validate(nffg_dict)
nffg = NF_FG()
nffg.parseDict(nffg_dict)

controller = UpperLayerOrchestratorController(user_data=UserData(usr=username, pwd=password, tnt=tenant))
controller.put(nffg)
print('Job completed')
exit()

orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG/"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, nffg.getJSON(), headers=headers)
print('Job completed')
