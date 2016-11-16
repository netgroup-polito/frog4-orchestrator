'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import configparser, os, inspect
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
            self.conf_file = "config/config.ini"

        self.inizialize()

    def inizialize(self): 
        #TODO: clean obsolete parameters
        config = configparser.RawConfigParser()
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        try:
            if base_folder == "":
                config.read(base_folder + self.conf_file)
            else:
                config.read(base_folder + '/' + self.conf_file)
                
            self._LOG_FILE = config.get('log', 'log_file')
            self._VERBOSE = config.getboolean('log', 'verbose')
            self._DEBUG = config.getboolean('log', 'debug')
            self._CONNECTION = config.get('db','connection')
            
            
            self._SWITCH_TEMPLATE = config.get('switch','template')
            self._SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_name').split(',')]
            self._CONTROL_SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_control_name').split(',')]
                        
            self._DEBUG_MODE = config.getboolean('orchestrator', 'debug_mode')
            
            self._ORCH_PORT = config.get('orchestrator','port')
            self._ORCH_IP = config.get('orchestrator','ip')
            self._ORCH_TIMEOUT = config.get('orchestrator','timeout')
            if config.has_option('orchestrator', 'default_domain'):
                self._DEFAULT_DOMAIN = config.get('orchestrator','default_domain')
            else:
                self._DEFAULT_DOMAIN = None
            
            
            self._DD_NAME = config.get('doubledecker','dd_name')
            self._DD_CUSTOMER = config.get('doubledecker','dd_customer')
            self._BROKER_ADDRESS = config.get('doubledecker','broker_address')
            self._DD_KEYFILE = config.get('doubledecker','dd_keyfile')

            self._DEFAULT_PRIORITY = config.get('flowrule', "default_priority")
            self._TEMPLATE_SOURCE = config.get('templates','source')
            if config.has_option('templates', 'path'):
                self._TEMPLATE_PATH = config.get('templates','path')
            else:
                self._TEMPLATE_PATH = None
            if config.has_option('templates', 'repository_url'):
                self._TEMPLATE_REPOSITORY_URL = config.get('templates', 'repository_url')
            else:
                self._TEMPLATE_REPOSITORY_URL = None
                
        except Exception as ex:
            raise WrongConfigurationFile(str(ex))
    
    @property
    def ORCH_TIMEOUT(self):
        return self._ORCH_TIMEOUT

    @property
    def DEFAULT_DOMAIN(self):
        return self._DEFAULT_DOMAIN

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
    def TEMPLATE_SOURCE(self):
        return self._TEMPLATE_SOURCE

    @property
    def TEMPLATE_REPOSITORY_URL(self):
        return self._TEMPLATE_REPOSITORY_URL
    @property

    def TEMPLATE_PATH(self):
        return self._TEMPLATE_PATH
     
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
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def DEBUG(self):
        return self._DEBUG
    
    @property
    def CONTROL_SWITCH_NAME(self):
        return self._CONTROL_SWITCH_NAME
    
    @property
    def SWITCH_NAME(self):
        return self._SWITCH_NAME
    
    @property
    def SWITCH_TEMPLATE(self):
        return self._SWITCH_TEMPLATE
