'''
@author: Andrea

'''

from .sql.user import User
from orchestrator_core.exception import unauthorizedRequest, TenantNotFound, TokenNotFound
from orchestrator_core.config import Configuration
import json
import uuid
import logging

TENANT_NAME = Configuration().TENANT_NAME

class UserData(object):
    
    def __init__(self, _id = None, usr=None, pwd=None, tnt=None):
        self.id = _id
        self.username = usr
        self.password = pwd
        self.tenant = tnt

    def getUserData(self, user_id):
        user = User().getUserFromID(user_id)
        self.username = user.name
        self.password = user.password
        tenant = User().getTenantName(user.tenant_id)
        self.tenant = tenant

class UserLoginAuthentication(object):

    def UserLoginAuthenticateFromRESTRequest(self, login_data):
        username = login_data['username']
        password = login_data['password']
        tenant = TENANT_NAME
        return UserCredentials().authenticateUserFromCredentials(username,password,tenant)

class UserCredentials(object):

    def authenticateUserFromCredentials(self, username, password, tenant):
        if username is None or password is None or tenant is None:
            raise unauthorizedRequest('Authentication credentials required')
        user = User().getUser(username)
        if user.password == password:
            tenantName = User().getTenantName(user.tenant_id)
            if tenantName == tenant:
                userobj = UserData(user.id, username, password, tenant)
                return userobj
            raise TenantNotFound('Invalid Tenant Provided, Please check the frog configuration file [tenant] section')
        raise unauthorizedRequest('Invalid authentication credentials')

class UserLoginAuthenticationController(object):

    def put(self, user_data):
        logging.debug('New POST request for /login/  From user '+user_data.username+" of tenant "+user_data.tenant)
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
            tenant = User().getTenantName(user.tenant_id)
            userobj = UserData(user.id, username, password, tenant)
            return userobj
        raise TokenNotFound('Invalid Token Provided')

