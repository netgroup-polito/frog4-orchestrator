"""
Created on Oct 1, 2014

@author: fabiomignini
"""
import configparser
import os
import inspect
import logging
from orchestrator_core.exception import WrongConfigurationFile 


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(object, metaclass=Singleton):
    
    def __init__(self):
        if os.getenv("FROG4_ORCH_CONF") is not None:
            self.conf_file = os.environ["FROG4_ORCH_CONF"]
        else:
            self.conf_file = "config/default-config.ini"
        self.log_init = False
        self.inizialize()

    def inizialize(self): 
        config = configparser.RawConfigParser()
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))\
            .rpartition('/')[0]
        try:
            if base_folder == "":
                config.read(str(base_folder) + self.conf_file)
            else:
                config.read(str(base_folder) + '/' + self.conf_file)

            # [orchestrator]
            self._DEBUG_MODE = config.getboolean('orchestrator', 'debug_mode')
            self._ORCH_PORT = config.get('orchestrator', 'port')
            self._ORCH_IP = config.get('orchestrator', 'ip')
            self._ORCH_TIMEOUT = config.get('orchestrator', 'timeout')

            # [log]
            self._LOG_FILE = config.get('log', 'log_file')
            self.__LOG_LEVEL = config.get('log', 'log_level')
            self.__APPEND_LOG = config.getboolean('log', 'append_log')

            # [db]
            self._CONNECTION = config.get('db', 'connection')

            # [switch]
            self._SWITCH_TEMPLATE = config.get('switch', 'template')
            self._SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_name').split(',')]
            self._CONTROL_SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_control_name').split(',')]

            # [doubledecker]
            self._DD_NAME = config.get('doubledecker', 'dd_name')
            self._DD_CUSTOMER = config.get('doubledecker', 'dd_customer')
            self._BROKER_ADDRESS = config.get('doubledecker', 'broker_address')
            self._DD_KEYFILE = config.get('doubledecker', 'dd_keyfile')
            self._DEFAULT_PRIORITY = config.get('flowrule', "default_priority")

            # [authentication]
            self._AUTH_TOKEN_EXPIRATION = config.get('authentication', 'token_expiration')

        except Exception as ex:
            raise WrongConfigurationFile(str(ex))

    def log_configuration(self):
        if not self.log_init and not self.__APPEND_LOG:
            try:
                os.remove(self.LOG_FILE)
            except OSError:
                pass
        log_format = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s - %(filename)s:%(lineno)s'
        if self.__LOG_LEVEL == "DEBUG":
            log_level = logging.DEBUG
            requests_log = logging.getLogger("requests")
            requests_log.setLevel(logging.WARNING)
            sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
            sqlalchemy_log.setLevel(logging.WARNING)
        elif self.__LOG_LEVEL == "INFO":
            log_level = logging.INFO
            requests_log = logging.getLogger("requests")
            requests_log.setLevel(logging.WARNING)
        elif self.__LOG_LEVEL == "WARNING":
            log_level = logging.WARNING
        else:
            log_level = logging.ERROR
        logging.basicConfig(filename=self.LOG_FILE, level=log_level, format=log_format, datefmt='%d/%m/%Y %H:%M:%S')
        logging.info("[CONFIG] Logging just started!")
        self.log_init = True

    @property
    def ORCH_TIMEOUT(self):
        return self._ORCH_TIMEOUT

    @property
    def DD_NAME(self):
        return self._DD_NAME
    
    @property
    def DD_CUSTOMER(self):
        return self._DD_CUSTOMER    
    
    @property
    def BROKER_ADDRESS(self):
        return self._BROKER_ADDRESS
    
    @property
    def DD_KEYFILE(self):
        return self._DD_KEYFILE    
    
    @property
    def DEBUG_MODE(self):
        return self._DEBUG_MODE
     
    @property
    def DEFAULT_PRIORITY(self):
        return self._DEFAULT_PRIORITY
    
    @property
    def ORCH_IP(self):
        return self._ORCH_IP
    
    @property
    def ORCH_PORT(self):
        return self._ORCH_PORT
        
    @property
    def CONNECTION(self):
        return self._CONNECTION

    @property
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def CONTROL_SWITCH_NAME(self):
        return self._CONTROL_SWITCH_NAME
    
    @property
    def SWITCH_NAME(self):
        return self._SWITCH_NAME
    
    @property
    def SWITCH_TEMPLATE(self):
        return self._SWITCH_TEMPLATE

    @property
    def AUTH_TOKEN_EXPIRATION(self):
        return self._AUTH_TOKEN_EXPIRATION
