'''
@author: fabiomignini
@author: stefanopetrangeli
'''
from flask import Flask
from flasgger import Swagger
import logging
import os
import inspect

from threading import Thread
from orchestrator_core.config import Configuration
from orchestrator_core.orchestrator import UpperLayerOrchestrator, TemplateAPI, YANGAPI, TemplateAPILocation, NFFGStatus, ActiveGraphs, User_login
from orchestrator_core.dd_server import DD_Server

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

#log_format = '%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s'
log_format = '%(asctime)s %(levelname)s %(message)s - %(filename)s'

logging.basicConfig(filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug("Global Orchestrator Starting")
print("Welcome to the Global Orchestrator")

"""
Old routes, not supported
template = TemplateAPI()
yang = YANGAPI()

app.add_route('/template/{image_id}', template)
app.add_route('/yang/{image_id}', yang)
"""

app = Flask(__name__)

swagger_config = {
    "swagger_version": "2.0",
    "title": "FROG4 - Global Orchestrator API",
    "headers": [
         ('Access-Control-Allow-Origin', '*')
    ],
    "specs": [
        {
            "version": "1.0.0",
            "title": "Global Orchestrator API",
            "endpoint": 'v1_spec',
            "route": '/v1/spec',
        }
    ],
        "static_url_path": "/apidocs",
        "static_folder": "swaggerui",
        "specs_route": "/specs"
}

Swagger(app, config=swagger_config)

orch = UpperLayerOrchestrator.as_view('NF-FG')
app.add_url_rule(
    '/NF-FG/',
    view_func=orch,
    methods=["PUT"]
)
app.add_url_rule(
    '/NF-FG/<nffg_id>',
    view_func=orch,
    methods=["GET", "DELETE"]
)

active_graphs = ActiveGraphs.as_view("active_graphs")
app.add_url_rule(
    '/NF-FG/',
    view_func=active_graphs,
    methods=["GET"]
)

nffg_status = NFFGStatus.as_view('NFFGStatus')
app.add_url_rule(
    '/NF-FG/status/<nffg_id>',
    view_func=nffg_status,
    methods=["GET"]
)

template_location = TemplateAPILocation.as_view('template_location')
app.add_url_rule(
    '/template/location/<template_name>',
    view_func=template_location,
    methods=["GET"]
)

app.add_url_rule( '/login/', view_func=User_login.as_view('login'), methods=['POST'] )

# start the dd client to receive information about domains
base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
dd_server = DD_Server(conf.DD_NAME, conf.BROKER_ADDRESS, conf.DD_CUSTOMER, conf.DD_KEYFILE)
thread = Thread(target=dd_server.start)
thread.start()

logging.info("Flask Successfully started")
