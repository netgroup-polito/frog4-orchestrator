'''
Created on Oct 1, 2014

@author: fabiomignini
@author: stefanopetrangeli
'''

import logging
import requests
import json
from flask.views import MethodView
from flask import request, jsonify, Response

from sqlalchemy.orm.exc import NoResultFound
from nffg_library.validator import ValidateNF_FG
from nffg_library.nffg import NF_FG

from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.userAuthentication import UserAuthentication
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, sessionNotFound, UserNotFound, VNFRepositoryError
from orchestrator_core.nffg_manager import NFFG_Manager
from nffg_library.exception import NF_FGValidationError

class YANGAPI(object):
    
    def get(self, request, response, image_id):
        pass
    
class TemplateAPI(object):
    
    def get(self, request, response, image_id):
        pass
    
class TemplateAPILocation(MethodView):
    
    def get(self, template_name):
        """
        Get the template
        ---
        tags:
          - NF-FG
        produces:
          - application/json             
        parameters:
          - name: template_name
            in: path
            description: Template to be retrieved
            type: string            
            required: true
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string                        
                    
        responses:
          200:
            description: Template found  
          401:
            description: Unauthorized
          404:
            description: Template not found
          500:
            description: Internal Error
        """        
        try:
            UserAuthentication().authenticateUserFromRESTRequest(request)
            return jsonify((NFFG_Manager(None).getTemplate(template_name).getDict()))
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-User") is not None:
                logging.debug("Unauthorized access attempt from user "+request.headers.get("X-Auth-User"))
            logging.debug(err.message)
            return ("Unauthorized", 401)
        except FileNotFoundError as err:
            return ("Template not found", 404)
        except VNFRepositoryError as err:
            return ("VNFRepositoryError: Template not found or incorrect VNF-Repository configuration", 404)        
        except Exception as err:
            logging.exception(err)
            return ("Contact the admin "+ str(err), 500)

class NFFGStatus(MethodView):
    def get(self, nffg_id):
        """
        Get the status of a graph
        ---
        tags:
          - NF-FG
        produces:
          - application/json             
        parameters:
          - name: nffg_id
            in: path
            description: Graph ID to be retrieved
            type: string            
            required: true
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string                        
                    
        responses:
          200:
            description: Status correctly retrieved       
          401:
            description: Unauthorized
          404:
            description: Graph not found
          500:
            description: Internal Error
        """            
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
            resp = Response(response=controller.getStatus(nffg_id), status=200, mimetype="application/json")
            return resp

        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            return ("EXCEPTION - NoResultFound", 404)
        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err), 500)
        except sessionNotFound as err:
            logging.exception(err.message)
            return (err.message, 404)
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-User") is not None:
                logging.debug("Unauthorized access attempt from user "+request.headers.get("X-Auth-User"))
            logging.debug(err.message)
            return ("Unauthorized", 401)
        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err), 500)

class ActiveGraphs(MethodView):
    def get(self):
        """
        Get the list of graphs currently deployed
        Returns the list of the active graphs
        ---
        tags:
          - NF-FG
        produces:
          - application/json          
        parameters:
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string      
        responses:
          200:
            description: List retrieved        
          401:
            description: Unauthorized
          500:
            description: Internal Error
        """
        # This class is necessary because there is a conflict in the swagger documentation of get operation
        upper_layer_orch = UpperLayerOrchestrator()
        return upper_layer_orch.get()
      
class UpperLayerOrchestrator(MethodView):
    '''
    Admin class that intercept the REST call through the WSGI server
    '''
    counter = 1
        
    def delete(self, nffg_id):
        """
        Delete a graph
        ---
        tags:
          - NF-FG   
        parameters:
          - name: nffg_id
            in: path
            description: Graph ID to be deleted
            required: true
            type: string            
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string          
        responses:
          200:
            description: Graph deleted         
          401:
            description: Unauthorized
          404:
            description: Graph not found
          500:
            description: Internal Error
        """          
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
            controller.delete(nffg_id)
        
            return ("Session deleted")
            
        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            return ("EXCEPTION - NoResultFound", 404)
        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err), 500)
        except sessionNotFound as err:
            logging.exception(err.message)
            return (err.message, 404)
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-User") is not None:
                logging.debug("Unauthorized access attempt from user "+request.headers.get("X-Auth-User"))
            logging.debug(err.message)
            return ("Unauthorized", 401) 
        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err), 500)
    
    def get(self, nffg_id = None):
        """
        Get a graph
        Returns an already deployed graph
        ---
        tags:
          - NF-FG
        produces:
          - application/json          
        parameters:
          - name: nffg_id
            in: path
            description: Graph ID to be retrieved
            required: true
            type: string
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string      
        responses:
          200:
            description: Graph retrieved        
          401:
            description: Unauthorized
          404:
            description: Graph not found
          500:
            description: Internal Error
        """        
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
            resp = Response(response=controller.get(nffg_id), status=200, mimetype="application/json")
            return resp
                        
        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            return ("EXCEPTION - NoResultFound", 404)
        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err), 500)
        except requests.ConnectionError as err:
            logging.exception(err)
            return (str(err), 500)       
        except sessionNotFound as err:
            logging.exception(err.message)
            return (err.message, 404)
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-User") is not None:
                logging.debug("Unauthorized access attempt from user "+request.headers.get("X-Auth-User"))
            logging.debug(err.message)
            return ("Unauthorized", 401) 
        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err), 500)
        
    def put(self):
        """
        Put a graph
        Deploy a graph
        ---
        tags:
          - NF-FG
        parameters:
          - name: X-Auth-User
            in: header
            description: Username
            required: true
            type: string
          - name: X-Auth-Pass
            in: header
            description: Password
            required: true
            type: string
          - name: X-Auth-Tenant
            in: header
            description: Tenant
            required: true
            type: string
          - name: NF-FG
            in: body
            description: Graph to be deployed
            required: true
            schema:
                type: string
        responses:
          202:
            description: Graph correctly deployed          
          401:
            description: Unauthorized
          400:
            description: Bad request
          500:
            description: Internal Error
        """
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            
            nffg_dict = json.loads(request.data.decode())
            ValidateNF_FG().validate(nffg_dict)
            nffg = NF_FG()
            nffg.parseDict(nffg_dict)
            
            controller = UpperLayerOrchestratorController(user_data, self.counter)
            response = controller.put(nffg)
            self.counter +=1

            return (response, 202)
        
        except wrongRequest as err:
            logging.exception(err)
            return ("Bad Request", 400)
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-User") is not None:
                logging.debug("Unauthorized access attempt from user "+request.headers.get("X-Auth-User"))
            logging.debug(err.message)
            return ("Unauthorized", 401)
        except NF_FGValidationError as err:
            logging.exception(err)            
            return ("NF-FG Validation Error: "+ err.message, 400)
        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err), 500)
        except requests.ConnectionError as err:
            logging.exception(err)
            return (str(err), 500)
        except VNFRepositoryError as err:
            return (err.message, 500)        
        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err), 500)
