"""
Created on Mar 20, 2017

@author: gabrielecastellano
"""

import logging

from flask import request, jsonify
from flask_restplus import Resource

from orchestrator_core.api.api import api
from orchestrator_core.nffg_manager import NFFG_Manager
from orchestrator_core.userAuthentication import UserTokenAuthentication
from orchestrator_core.exception import unauthorizedRequest, UserNotFound, VNFRepositoryError, TokenNotFound


template_ns = api.namespace('template', 'Template Resource')


class TemplateAPI(object):

    def get(self, image_id):
        pass


@template_ns.route('/location/<template_name>', methods=['GET'],
                   doc={'params': {'template_name': {'description': 'Template to be retrieved'}}})
@api.doc(responses={404: 'Template not found'})
class TemplateLocationResource(Resource):

    @template_ns.param("X-Auth-Token", "Authentication Token", "header", type="string", required=True)
    @template_ns.response(200, 'Template retrieved.')
    @template_ns.response(401, 'Unauthorized.')
    @template_ns.response(500, 'Internal Error.')
    def get(self, template_name):
        """
        Get the NF template
        """
        try:
            UserTokenAuthentication().UserTokenAuthenticateFromRESTRequest(request)
            return jsonify((NFFG_Manager().getTemplate(template_name).getDict()))
        except (unauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-Token") is None:
                logging.debug("Unauthorized access attempt")
            logging.debug(err.message)
            return "Unauthorized", 401
        #except FileNotFoundError:
            #return "Template not found", 404
        except VNFRepositoryError:
            return "VNFRepositoryError: Template not found or incorrect VNF-Repository configuration", 404
        except TokenNotFound as err:
            logging.exception(err)
            return err.message, 401
        except Exception as err:
            logging.exception(err)
            return "Contact the admin " + str(err), 500
