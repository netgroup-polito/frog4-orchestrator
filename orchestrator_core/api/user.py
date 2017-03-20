import logging
import requests
import json
from flask import request, Response
from flask_restplus import Resource
from sqlalchemy.orm.exc import NoResultFound
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG
from orchestrator_core.api.api import api
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.userAuthentication import UserAuthentication
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, sessionNotFound, UserNotFound, \
    VNFRepositoryError, NoFunctionalCapabilityFound, FunctionalCapabilityAlreadyInUse, \
    FeasibleDomainNotFoundForNFFGElement, FeasibleSolutionNotFoundForNFFG, GraphError, IncoherentDomainInformation, \
    UnsupportedLabelingMethod
from nffg_library.exception import NF_FGValidationError

nffg_ns = api.namespace('login', 'login Resource')


@nffg_ns.route('/', methods=['POST'])
@api.doc(responses={404: 'Graph not found'})
class User_login(Resource):
    '''
    User login class that intercept the REST call through the WSGI server
    '''
    def post(self):
        """
        User login
        ---
        tags:
          - login
        parameters:
          - name: Login info
            in: body
            description: User authentication details like ...
            {
                "username":"username",
                "password":"password"
            }
            required: true
            schema:
                type: string
        responses:
            200:
                description: login successfully
            401:
                description: UNAUTHORIZED
            400:
                description: BAD REQUEST
            500:
                description: INTERNAL SERVER ERROR
        """
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




