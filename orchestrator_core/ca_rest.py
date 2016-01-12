'''
Created on 07 dic 2015

@author: stefanopetrangeli
'''
import logging
import requests
import json
from orchestrator_core.config import Configuration
from vnf_template_library.template import Template
from vnf_template_library.validator import ValidateTemplate
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG

class CA_Interface(object):
    timeout = Configuration().ORCH_TIMEOUT
        
    def __init__(self, user_data, ip, port, token=None):
        self.ip = ip
        self.port = port
        self.user_data = user_data
        self.base_url = "http://"+str(ip)+":"+str(port)
        self.put_url = self.base_url+"/NF-FG"
        self.delete_url = self.base_url+"/NF-FG/%s"
        self.get_nffg_url = self.base_url+"/NF-FG/%s"   
        self.get_status_url = self.base_url+"/NF-FG/status/%s"  
        self.get_template =  self.base_url+"/template/location/%s"
        self.authentication_url = self.base_url+"/authentication"
        """ DEBUG
        if token is None:
            self.getToken(user_data, ip, port)
        else:
            self.token = token
        
        self.headers = {'Content-Type': 'application/json',
            'cache-control': 'no-cache',
            'X-Auth-Token': self.token}
        """

    def getNFFGStatus(self, nffg_id):
        resp = requests.get(self.get_status_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
        resp.raise_for_status()
        logging.debug("Check completed")
        return resp.text
    
    def getNFFG(self, nffg_id):
        resp = requests.get(self.get_nffg_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
        resp.raise_for_status()
        nffg_dict = json.loads(resp.text)
        ValidateNF_FG().validate(nffg_dict)
        nffg = NF_FG()
        nffg.parseDict(nffg_dict)
        logging.debug("Get NFFG completed")
        return nffg
        
    def put(self, nffg):
        logging.debug(self.put_url+"\n"+nffg.getJSON())
        """
        resp = requests.put(self.put_url, data = nffg.getJSON(), headers=self.headers, timeout=int(self.timeout))
        resp.raise_for_status()
        logging.debug("Put completed")
        return resp.text
        """
    
    def delete(self, nffg_id):
        logging.debug(self.delete_url % (nffg_id))
        """
        resp = requests.delete(self.delete_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
        resp.raise_for_status()
        logging.debug("Delete completed")
        return resp.text   
        """     
    def getToken(self, user_data, ip, port):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        authenticationData = {'username': user_data.username, 'password': user_data.password}
        resp = requests.post(self.authentication_url, data=json.dumps(authenticationData), headers=headers, timeout=int(self.timeout))
        resp.raise_for_status()
        response = json.loads(resp.text)
        self.token = response['token']
        