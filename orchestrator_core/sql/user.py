'''
@author: Andrea

'''

from sqlalchemy import Column, VARCHAR, Integer
from sqlalchemy.ext.declarative import declarative_base
import logging

from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.exception import UserNotFound, TokenNotFound
from sqlalchemy.orm.exc import NoResultFound
import time

Base = declarative_base()

class UserModel(Base):
    '''
    Maps the database table user
    '''
    __tablename__ = 'user'
    attributes = ['id', 'name', 'password', 'mail']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    password = Column(VARCHAR(64))
    mail = Column(VARCHAR(64))

class UserTokenModel(Base):
    '''
    Maps the database table user token
    '''
    __tablename__ = 'user_token'
    attributes = ['user_id', 'token', 'timestamp']
    user_id = Column(Integer, primary_key=True)
    token = Column(VARCHAR(64))
    timestamp = Column(VARCHAR(64))


class User(object):
    
    def __init__(self):
        pass

    def getUser(self, username):
        session = get_session()
        try:
            return session.query(UserModel).filter_by(name = username).one()
        except Exception as ex:
            raise UserNotFound("User not found") from None
    
    def getUserFromID(self, user_id):
        session = get_session()
        try:
            return session.query(UserModel).filter_by(id = user_id).one()
        except Exception as ex:
            raise UserNotFound("User not found") from None

    def inizializeUserAuthentication(self, user_id, token, timestamp, check_token):
        session = get_session()
        with session.begin():
            if check_token is False:
                user_ref = UserTokenModel(user_id=user_id, token=token, timestamp=timestamp)
                session.add(user_ref)
            else:
                session.query(UserTokenModel).filter_by(user_id=user_id).update(
                    {"token": token, "timestamp": timestamp})

    def checkUserToken(self, user_id):
        session = get_session()
        try:
            return session.query(UserTokenModel).filter_by(user_id=user_id).one().token
        except NoResultFound:
            return False
    def getToken(self, user_token):
        session = get_session()
        try:
            return session.query(UserTokenModel).filter_by(token = user_token).one()
        except Exception as ex:
            raise TokenNotFound("Token is not valid: "+str(user_token)) from None

    def checkToken(self, token):
        session = get_session()
        with session.begin():
            return session.query(UserTokenModel).filter_by(token = token).all()


    def checkUsertimestamp(self, user_id):
        session = get_session()
        try:
            return session.query(UserTokenModel).filter_by(user_id=user_id).one().timestamp
        except NoResultFound:
            return None