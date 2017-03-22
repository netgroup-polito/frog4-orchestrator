import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource, fields
from orchestrator_core.user_validator import UserValidate
from orchestrator_core.api.api import api
from orchestrator_core.userAuthentication import UserLoginAuthentication, UserLoginAuthenticationController
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, UserNotFound,UserValidationError, TenantNotFound

login_user = api.namespace('login', description = 'Login Resource')
login_user_model = api.model('Login', {
    'username': fields.String(required = True, description = 'Username',  type = 'string'),
    'password': fields.String(required = True, description = 'Password',  type = 'string') })
@login_user.route('/', methods=['POST'])
@api.doc(responses={404: 'User not found'})
class User_login(Resource):
    
    @login_user.expect(login_user_model)
    @login_user.response(200, 'LOGIN SUCCESSFULLY')
    @login_user.response(400, 'BAD REQUEST.')
    @login_user.response(402, 'VALIDATION ERROR')
    @login_user.response(401, 'UNAUTHORIZED.')
    @login_user.response(500, 'INTERNAL SERVER ERROR.')
    def post(self):
        """Login info."""
        try:

            login_data = json.loads(request.data.decode())
            UserValidate().validate(login_data)
            user_data = UserLoginAuthentication().UserLoginAuthenticateFromRESTRequest(login_data)
            response = UserLoginAuthenticationController().put(user_data)
            #return jsonify(response)
            return response, 200, {'Content-Type': 'application/token'}

        except wrongRequest as err:
            logging.exception(err)
            return ("BAD REQUEST", 400)

        except (unauthorizedRequest, UserNotFound, TenantNotFound) as err:
            logging.debug(err.message)
            # return ("Unauthorized for more details see log file \n", 401)
            return ("Unauthorized", 401)

        except UserValidationError as err:
            logging.exception(err)
            return ("Login Validation Error: "+ err.message, 402)

        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err), 500)

        except requests.ConnectionError as err:
            logging.exception(err)
            return (str(err), 500)

        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err), 500)
