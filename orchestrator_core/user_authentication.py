"""
@author: Andrea

"""
import uuid
import time
import logging
from .sql.user import User
from orchestrator_core.exception import unauthorizedRequest, TokenNotFound, UserTokenExpired
from orchestrator_core.config import Configuration


class UserData(object):
    
    def __init__(self, _id=None, usr=None, pwd=None):
        self.id = _id
        self.username = usr
        self.password = pwd

    def get_user_data(self, user_id):
        user = User().getUserFromID(user_id)
        self.username = user.name
        self.password = user.password


class UserAuthentication(object):

    def __init__(self):
        self.token_expiration_timestamp = int(Configuration().AUTH_TOKEN_EXPIRATION)

    def is_an_expired_token(self, timestamp):
        if timestamp is None:
            return True
        timestamp = int(timestamp)
        tt = int(time.time())
        return (tt - timestamp) > self.token_expiration_timestamp

    def user_login_authenticate_from_rest_request(self, login_data):
        username = login_data['username']
        password = login_data['password']
        return self.authenticate_user_from_credentials(username, password)

    def authenticate_user_from_credentials(self, username, password):
        logging.debug('New POST request for /login/  From user ' + username)
        if username is None or password is None:
            raise unauthorizedRequest('Authentication credentials required')
        user = User().getUser(username)
        if user.password != password:
            raise unauthorizedRequest('Invalid authentication credentials')

        user_obj = UserData(user.id, username, password)

        logging.info("Check current token. Get a new token, if it is needed.")
        try:
            have_a_token = User().checkUserToken(user_obj.id)
            if have_a_token is False or self.is_an_expired_token(User().checkUsertimestamp(user_obj.id)):
                while True:
                    token = uuid.uuid4().hex
                    old_token = User().checkToken(token)
                    if len(old_token) == 0:
                        break
                timestamp = int(time.time())
                User().inizializeUserAuthentication(user_obj.id, token, timestamp, have_a_token)
                logging.debug("New token generated")
                return token
            else:
                logging.debug("Current token is valid.")
                return have_a_token
        except Exception as ex:
            logging.exception(ex)
            raise ex

    def user_token_authenticate_from_rest_request(self, request):
        user_token = request.headers.get("X-Auth-Token")
        if user_token is None:
            raise TokenNotFound('Token is required')
        user_details = User().getToken(user_token)
        if user_details.token == user_token:
            if not self.is_an_expired_token(User().checkUsertimestamp(user_details.user_id)):
                user = User().getUserFromID(user_details.user_id)
                username = user.name
                password = user.password
                user_obj = UserData(user.id, username, password)
                logging.debug("Found user token " + str(user_token) + " still valid.")
                return user_obj
            else:
                logging.debug("Found an expired user token " + str(user_token) + ".")
                raise UserTokenExpired("Token expired. You must authenticate again with user/pass")
        raise TokenNotFound('Invalid Token Provided')
