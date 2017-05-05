'''
Created on Oct 30, 2015

@author: fabiomignini
'''
import requests, logging, os
os.environ.setdefault("FROG4_ORCH_CONF", "config/onos-demo-config.ini")
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.userAuthentication import UserData

nffg_id = '12'
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
sqlalchemy_log.setLevel(logging.WARNING)

username = 'isp'
password = 'stack'


controller = UpperLayerOrchestratorController(user_data=UserData(username, password))
controller.delete(nffg_id)
print('Job completed')
exit()
orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG/12"

headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password}
requests.delete(orchestrator_endpoint, headers=headers)
print('Job completed')