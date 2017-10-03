import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource, fields
from orchestrator_core.api.api import api
from orchestrator_core.user_authentication import UserAuthentication
from orchestrator_core.exception import WrongRequest, UnauthorizedRequest, UserNotFound, UserValidationError

domain_info = api.namespace('Domain-Information', description='Domain Resource')
@domain_info.route('/', methods=['GET'])
@api.doc(responses={404: 'User Not Found'})
class DomainInfo(Resource):

    @domain_info.response(200, 'Successfully.')
    @domain_info.response(400, 'Bad Request.')
    @domain_info.response(401, 'Unauthorized.')
    @domain_info.response(500, 'Internal Error.')
    def get(self):
        """
        """
        try:

            user_data = UserAuthentication().user_token_authenticate_from_rest_request(request)
            return ''

        except WrongRequest as err:
            logging.exception(err)
            return "Bad Request", 400
        except UnauthorizedRequest as err:
            logging.debug(err.message)
            return "Unauthorized: " + err.message, 401
        except requests.HTTPError as err:
            logging.exception(err)
            return str(err), 500
        except requests.ConnectionError as err:
            logging.exception(err)
            return str(err), 500
        except Exception as err:
            logging.exception(err)
            return "Contact the admin: " + str(err), 500