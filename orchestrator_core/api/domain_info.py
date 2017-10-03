import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource
from sqlalchemy.orm.exc import NoResultFound
from orchestrator_core.api.api import api
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.user_authentication import UserAuthentication
from orchestrator_core.exception import UnauthorizedRequest, UserNotFound, UserTokenExpired, TokenNotFound, \
    DomainNotFound

domain_info = api.namespace('Domain-Information', 'Domain Resource')
@domain_info.route('/', methods=['GET'])
@api.doc(responses={404: 'Domain not found'})

class DomainInfo(Resource):
    @domain_info.param("X-Auth-Token", "Authentication Token", "header", type="string", required=True)
    @domain_info.response(200, 'Domain retrieved.')
    @domain_info.response(401, 'Unauthorized.')
    @domain_info.response(500, 'Internal Error.')
    def get(self, nffg_id=None):
        """
        Returns a domain information
        Get domain information
        """
        try:
            user_data = UserAuthentication().user_token_authenticate_from_rest_request(request)
            controller = UpperLayerOrchestratorController(user_data)
            resp = Response(response=controller.get_domian_information_for_upper_Layer(), status=200,
                            mimetype="application/json")
            return resp

        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            return "Graph not found", 404
        except requests.HTTPError as err:
            logging.exception(err)
            return str(err), 500
        except requests.ConnectionError as err:
            logging.exception(err)
            return str(err), 500
        except DomainNotFound as err:
            return err.message, 400
        except (UnauthorizedRequest, UserNotFound) as err:
            if request.headers.get("X-Auth-Token") is None:
                logging.debug("Unauthorized access attempt ")
            logging.debug(err.message)
            return "Unauthorized", 401
        except TokenNotFound as err:
            logging.exception(err)
            return err.message, 401
        except UserTokenExpired as err:
            logging.exception(err)
            return err.message, 401
        except Exception as err:
            logging.exception(err)
            return "Contact the admin: " + str(err), 500