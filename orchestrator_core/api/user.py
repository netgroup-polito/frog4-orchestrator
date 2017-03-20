import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource
from sqlalchemy.orm.exc import NoResultFound
from orchestrator_core.user_validator import UserValidate
from orchestrator_core.api.api import api
from orchestrator_core.userAuthentication import UserAuthentication, UserAuthentication, UserLoginAuthentication, UserLoginAuthenticationController, UserTokenAuthentication
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, UserNotFound,UserValidationError, TenantNotFound, TokenNotFound


login_user = api.namespace('login', 'Login Resource')


@login_user.route('/', methods=['POST'])
@api.doc(responses={404: 'User not found'})
class User_login(Resource):

    @login_user.param("Login", "User Authentication details", "body", type="string", required=True)
    @login_user.response(200, 'Login successfully.')
    @login_user.response(400, 'BAD REQUEST.')
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
            return (response, 200)

        except wrongRequest as err:
            logging.exception(err)
            return ("BAD REQUEST", 400)

        except (unauthorizedRequest, UserNotFound, TenantNotFound) as err:
            logging.debug(err.message)
            # return ("Unauthorized for more details see log file \n", 401)
            return ("Unauthorized", 401)

        except UserValidationError as err:
            logging.exception(err)
            return ("Login Validation Error: "+ err.message +"\n", 400)

        except requests.HTTPError as err:
            logging.exception(err)
            return (str(err)+ "\n", 500)

        except requests.ConnectionError as err:
            logging.exception(err)
            return (str(err) + "\n", 500)

        except Exception as err:
            logging.exception(err)
            return ("Contact the admin: "+ str(err) +"\n", 500)




