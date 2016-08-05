'''
Created on 07 dic 2015

@author: stefanopetrangeli
'''
import logging
import requests
import json
from orchestrator_core.config import Configuration
from orchestrator_core.sql.domain import Domain
from vnf_template_library.template import Template
from vnf_template_library.validator import ValidateTemplate
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG
from requests.exceptions import HTTPError
from orchestrator_core.exception import LoginError

class CA_Interface(object):
    timeout = Configuration().ORCH_TIMEOUT
        
    def __init__(self, user_data, domain):
        self.ip = domain.ip
        self.port = domain.port
        self.token = Domain().getUserToken(domain.id, user_data.id)
        self.domain_id = domain.id
        self.user_data = user_data
        self.base_url = "http://"+str(self.ip)+":"+str(self.port)
        self.put_url = self.base_url+"/NF-FG/%s"
        self.delete_url = self.base_url+"/NF-FG/%s"
        self.get_nffg_url = self.base_url+"/NF-FG/%s"   
        self.get_status_url = self.base_url+"/NF-FG/status/%s"  
        self.get_template =  self.base_url+"/template/location/%s"
        self.authentication_url = self.base_url+"/login"
        
        if self.token is not None:
            self.headers = {'Content-Type': 'application/json',
            'cache-control': 'no-cache',
            'X-Auth-Token': self.token}
        
    def getNFFGStatus(self, nffg_id):
        if self.token is None:
            self.getToken(self.user_data)
        try:
            resp = requests.get(self.get_status_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
            resp.raise_for_status()
            logging.debug("Check completed")
            return json.loads(resp.text)
        except HTTPError as err:
            if err.response.status_code == 401:
                logging.debug("Token expired, getting a new one...")
                self.getToken(self.user_data)    
                resp = requests.get(self.get_status_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
                resp.raise_for_status()
                logging.debug("Check completed")
                return json.loads(resp.text)
            else:
                raise err
    
    def getNFFG(self, nffg_id):
        if self.token is None:
            self.getToken(self.user_data)
        try:
            resp = requests.get(self.get_nffg_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
            resp.raise_for_status()
            logging.debug(resp.text)
            nffg_dict = json.loads(resp.text)
            ValidateNF_FG().validate(nffg_dict)
            nffg = NF_FG()
            nffg.parseDict(nffg_dict)
            logging.debug("Get NFFG completed")
            return nffg
        except HTTPError as err:
            if err.response.status_code == 401:
                logging.debug("Token expired, getting a new one...")
                self.getToken(self.user_data)                
                resp = requests.get(self.get_nffg_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
                resp.raise_for_status()
                logging.debug(resp.text)
                nffg_dict = json.loads(resp.text)
                ValidateNF_FG().validate(nffg_dict)
                nffg = NF_FG()
                nffg.parseDict(nffg_dict)
                logging.debug("Get NFFG completed")
                return nffg   
            else:
                raise err
    
    def put(self, nffg):
        if self.token is None:
            self.getToken(self.user_data)
        try:
            logging.debug(self.put_url % (nffg.id)+"\n"+nffg.getJSON())
            resp = requests.put(self.put_url % (nffg.id), data = nffg.getJSON(), headers=self.headers, timeout=int(self.timeout))
            resp.raise_for_status()
            logging.debug("Put completed")
            return resp.text
        except HTTPError as err:
            if err.response.status_code == 401:
                logging.debug("Token expired, getting a new one...")
                self.getToken(self.user_data)
                resp = requests.put(self.put_url % (nffg.id), data = nffg.getJSON(), headers=self.headers, timeout=int(self.timeout))
                resp.raise_for_status()
                logging.debug("Put completed")  
                return resp.text
            else:
                raise err
    
    def delete(self, nffg_id):
        if self.token is None:
            self.getToken(self.user_data)
        try:  
            logging.debug(self.delete_url % (nffg_id))
            resp = requests.delete(self.delete_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
            resp.raise_for_status()
            logging.debug("Delete completed")
            return resp.text
        except HTTPError as err:
            if err.response.status_code == 401:
                logging.debug("Token expired, getting a new one...")
                self.getToken(self.user_data)
                resp = requests.delete(self.delete_url % (nffg_id), headers=self.headers, timeout=int(self.timeout))
                resp.raise_for_status()
                logging.debug("Delete completed") 
                return resp.text
            else:
                raise err
                                    
    def getToken(self, user_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        authenticationData = {'username': user_data.username, 'password': user_data.password}
        resp = requests.post(self.authentication_url, data=json.dumps(authenticationData), headers=headers, timeout=int(self.timeout))
        try:
            resp.raise_for_status()
            logging.debug("Authentication successfully performed")
            self.token = resp.text
            self.headers = {'Content-Type': 'application/json',
                'cache-control': 'no-cache',
                'X-Auth-Token': self.token}
            Domain().updateUserToken(self.domain_id, user_data.id, self.token)
        except HTTPError as err:
            logging.error(err)
            raise LoginError("login failed: " + str(err))
        
    """
    def checkToken(self, token):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.head(self.authentication_url, headers=headers)
        logging.debug(resp.status_code)
        if resp.status_code == 204 or resp.status_code == 200:
            return True
        return False
    """
        
