'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import falcon, logging
from threading import Thread
from orchestrator_core.config import Configuration
from orchestrator_core.orchestrator import UpperLayerOrchestrator, TemplateAPI, YANGAPI, TemplateAPILocation, NFFGStatus
from orchestrator_core.dd_server import special_server
import os, inspect
#from orchestrator_core.testclient import special_client

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

#format = '%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s'
log_format = '%(asctime)s %(levelname)s %(message)s - %(filename)s'

logging.basicConfig( filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug("Orchestrator Starting")
print("Welcome to the UN orchestrator_core")
    

# Falcon starts
app = falcon.API()
logging.info("Starting Orchestration Server application")


upper_layer_API = UpperLayerOrchestrator()
nffg_status = NFFGStatus()
template = TemplateAPI()
template_location = TemplateAPILocation()
yang = YANGAPI()

app.add_route('/NF-FG', upper_layer_API)
app.add_route('/NF-FG/{nffg_id}', upper_layer_API)
app.add_route('/NF-FG/status/{nffg_id}', nffg_status)
app.add_route('/template/{image_id}', template)
app.add_route('/template/location/{template_location}', template_location)
app.add_route('/yang/{image_id}', yang)


base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
dd_server = special_server("orchestrator", conf.BROKER_ADDRESS, "public", keyfile=base_folder+"/orchestrator_core/doubledecker/public-keys.json") 
thread = Thread(target=dd_server.start)
thread.start()

logging.info("Falcon Successfully started")






    
    
