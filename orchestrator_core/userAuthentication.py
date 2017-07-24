'''
@author: Andrea

'''

from .sql.user import User
from orchestrator_core.exception import unauthorizedRequest, TokenNotFound
from orchestrator_core.config import Configuration
import uuid
import time, logging

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

    def __init__(self):
        self.token_expiration_timestamp = int(Configuration().AUTH_TOKEN_EXPIRATION)

    def __isAnExpiredToken(self, timestamp):
        if timestamp is None:
            return True
        timestamp = int(timestamp)
        tt = int(time.time())
        return ((tt - timestamp) > self.token_expiration_timestamp)

    def UserLoginAuthenticateFromRESTRequest(self, login_data):
        username = login_data['username']
        password = login_data['password']
        return self.authenticateUserFromCredentials(username,password)

    def authenticateUserFromCredentials(self, username, password):
        logging.debug('New POST request for /login/  From user ' + username)
        if username is None or password is None:
            raise unauthorizedRequest('Authentication credentials required')
        user = User().getUser(username)
        if user.password != password:
            raise unauthorizedRequest('Invalid authentication credentials')

        userobj = UserData(user.id, username, password)

        logging.info("Check current token. Get a new token, if it is needed.")
        try:
            have_a_token_details = User().checkUserToken(userobj.id)
            if have_a_token_details.token is False or self.__isAnExpiredToken(have_a_token_details.timestamp):

                while True:
                    token = uuid.uuid4().hex
                    old_Token = User().checkToken(token)
                    if len(old_Token) == 0:
                        break
                timestamp = int(time.time())
                User().inizializeUserAuthentication(userobj.id, token, timestamp)
                logging.debug("New token generated")
                return token
            else:
                logging.debug("Current token is valid.")
                return have_a_token_details.token
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
