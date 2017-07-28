import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource, fields
from orchestrator_core.user_validator import UserValidate
from orchestrator_core.api.api import api
from orchestrator_core.userAuthentication import UserAuthentication
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, UserNotFound, UserValidationError

login_user = api.namespace('login', description='Login Resource')
login_user_model = api.model('Login', {
    'username': fields.String(required=True, description='Username', type='string'),
    'password': fields.String(required=True, description='Password', type='string')})


@login_user.route('', methods=['POST'])
@api.doc(responses={404: 'User Not Found'})
class LoginResource(Resource):

    @login_user.expect(login_user_model)
    @login_user.response(200, 'Login Successfully.')
    @login_user.response(400, 'Bad Request.')
    @login_user.response(409, 'Validation Error.')
    @login_user.response(401, 'Unauthorized.')
    @login_user.response(500, 'Internal Error.')
    def post(self):
        """Login info and returning the user token"""
        try:

            login_data = json.loads(request.data.decode())
            UserValidate().validate(login_data)
            resp_token = UserAuthentication().user_login_authenticate_from_rest_request(login_data)
            resp = Response(response=resp_token, status=200, mimetype="application/token")
            return resp

        except wrongRequest as err:
            logging.exception(err)
            return "Bad Request", 400
        except unauthorizedRequest as err:
            logging.debug(err.message)
            return "Unauthorized: " + err.message, 401
        except UserNotFound as err:
            logging.debug(err.message)
            return "Unauthorized: " + err.message, 401
        except UserValidationError as err:
            logging.exception(err)
            return "Login Validation Error: " + err.message, 409
        except requests.HTTPError as err:
            logging.exception(err)
            return str(err), 500
        except requests.ConnectionError as err:
            logging.exception(err)
            return str(err), 500
        except Exception as err:
            logging.exception(err)
            return "Contact the admin: " + str(err), 500
