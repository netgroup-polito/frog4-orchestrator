"""
@author: fabiomignini
@author: stefanopetrangeli

@author: gabrielecastellano
"""

import logging
import os
import inspect

from threading import Thread
from flask import Flask

from orchestrator_core.api.api import root_blueprint
from orchestrator_core.api.nffg import api as nffg_api
from orchestrator_core.api.user import api as user_api
from orchestrator_core.api.domain_info import api as domain_info_api

from orchestrator_core.config import Configuration

from orchestrator_core.dd_client import DDClient

# load configuration
conf = Configuration()

# initialize logging
conf.log_configuration()
print("[ Configuration file is: '" + Configuration().conf_file + "' ]")

logging.debug("Global Orchestrator Starting...")

# Rest application
if nffg_api is not None and user_api is not None and domain_info_api is not None:
    app = Flask(__name__)
    app.register_blueprint(root_blueprint)
    logging.info("Flask Successfully started")

# start the dd client to receive information about domains
base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
dd_server = DDClient(conf.DD_NAME, conf.BROKER_ADDRESS, conf.DD_CUSTOMER, conf.DD_KEYFILE)
thread = Thread(target=dd_server.start)
thread.start()

logging.info("DoubleDecker Successfully started")

print("Welcome to the Global Orchestrator")
