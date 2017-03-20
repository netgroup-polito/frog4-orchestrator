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
from orchestrator_core.api.template import api as template_api

from orchestrator_core.config import Configuration
from orchestrator_core.dd_client import DDClient

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

log_format = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s - %(filename)s:%(lineno)s'
logging.basicConfig(filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt='%d/%m/%Y %I:%M:%S')

logging.debug("Global Orchestrator Starting")
print("Welcome to the Global Orchestrator")

# Rest application
if nffg_api is not None and template_api is not None:
    app = Flask(__name__)
    app.register_blueprint(root_blueprint)
    logging.info("Flask Successfully started")


# start the dd client to receive information about domains
base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
dd_server = DDClient(conf.DD_NAME, conf.BROKER_ADDRESS, conf.DD_CUSTOMER, conf.DD_KEYFILE)
# bug in dd? third parameter should be conf.DD_CUSTOMER instead of conf.DD_KEYFILE
thread = Thread(target=dd_server.start)
thread.start()
logging.info("DoubleDecker Successfully started")
