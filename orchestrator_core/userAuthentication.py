'''
@author: Andrea

'''

from .sql.user import User
from orchestrator_core.exception import unauthorizedRequest, TokenNotFound
import uuid
import logging

class UserData(object):
    
    def __init__(self, _id = None, usr=None, pwd=None):
        self.id = _id
        self.username = usr
        self.password = pwd

    def getUserData(self, user_id):
        user = User().getUserFromID(user_id)
        self.username = user.name
        self.password = user.password

class UserLoginAuthentication(object):

    def UserLoginAuthenticateFromRESTRequest(self, login_data):
        username = login_data['username']
        password = login_data['password']
        return UserCredentials().authenticateUserFromCredentials(username,password)

class UserCredentials(object):

    def authenticateUserFromCredentials(self, username, password):
        if username is None or password is None:
            raise unauthorizedRequest('Authentication credentials required')
        user = User().getUser(username)
        if user.password == password:
            userobj = UserData(user.id, username, password)
            return userobj
        raise unauthorizedRequest('Invalid authentication credentials')

class UserLoginAuthenticationController(object):

    def put(self, user_data):
        logging.debug('New POST request for /login/  From user '+user_data.username)
        try:
            have_a_token = User().checkUserToken(user_data.id)
            if have_a_token is False:
                token  = uuid.uuid4().hex
                User().inizializeUserAuthentication(user_data.id, token)
                return token
            else:
                return have_a_token
        except Exception as ex:
            logging.exception(ex)
            raise ex

class UserTokenAuthentication(object):

    def UserTokenAuthenticateFromRESTRequest(self, request):
        user_token = request.headers.get("X-Auth-Token")
        if user_token is None:
            raise TokenNotFound('Token is required')
        token_val = User().getToken(user_token)
        if token_val.token == user_token:
            user = User().getUserFromID(token_val.user_id)
            username = user.name
            password = user.password
            userobj = UserData(user.id, username, password)
            return userobj
        raise TokenNotFound('Invalid Token Provided')
