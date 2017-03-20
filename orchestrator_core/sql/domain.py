"""
Created on Jan 14, 2016

@author: stefanopetrangeli
"""

from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
import logging
from orchestrator_core.exception import DomainNotFound
from orchestrator_core.sql.sql_server import get_session
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class DomainModel(Base):
    """
    Maps the database table Domain
    """
    __tablename__ = 'domain'
    attributes = ['id', 'name', 'type', 'ip', 'port']
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    ip = Column(VARCHAR(64))
    port = Column(Integer)


class DomainTokenModel(Base):
    """
    Maps the database table Domain
    """
    __tablename__ = 'domain_token'
    attributes = ['user_id', 'domain_id', 'token']
    user_id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, primary_key=True)
    token = Column(VARCHAR(64))


class Domain(object):
    def __init__(self):
        pass
    
    def getDomain(self, domain_id):
        session = get_session()
        try:
            return session.query(DomainModel).filter_by(id = domain_id).one()
        except Exception as ex:
            logging.exception(ex)
            raise DomainNotFound("Domain not found: "+str(domain_id)) from None
    
    def getDomainFromName(self, name):
        session = get_session()
        try:
            return session.query(DomainModel).filter_by(name = name).one()
        except Exception as ex:
            logging.exception(ex)
            raise DomainNotFound("Domain not found for name: "+str(name)) from None

    def getDomainIP(self, domain_id):
        session = get_session()
        try:
            return session.query(DomainModel).filter_by(id = domain_id).one().ip
        except Exception as ex:
            logging.exception(ex)
            raise DomainNotFound("Domain not found: "+str(domain_id)) from None

    def getUserToken(self, domain_id, user_id):
        session = get_session()
        try:
            return session.query(DomainTokenModel).filter_by(user_id=user_id).filter_by(domain_id=domain_id).one().token
        except NoResultFound:
            return None

    def updateUserToken(self, domain_id, user_id, token):
        session = get_session()
        with session.begin():
            domain_token = session.query(DomainTokenModel).filter_by(user_id=user_id).filter_by(domain_id=domain_id).one_or_none()
            if domain_token is not None:
                session.query(DomainTokenModel).filter_by(user_id=user_id).filter_by(domain_id=domain_id).update({"token":token})
            else:
                domain_token = DomainTokenModel(user_id=user_id, domain_id=domain_id, token=token)
                session.add(domain_token)
    
    def addDomain(self, domain_name, domain_type, domain_ip, domain_port, update=False):
        session = get_session()
        with session.begin():
            max_id = -1
            domain_refs = session.query(DomainModel).all()
            for domain_ref in domain_refs:
                if domain_ref.id > max_id:
                    max_id = domain_ref.id
                if domain_ref.name == domain_name and domain_ref.type == domain_type and domain_ref.ip == domain_ip and domain_ref.port == int(domain_port):
                    return domain_ref.id
            domain = DomainModel(id=max_id+1, name=domain_name, type=domain_type, ip=domain_ip, port=domain_port)
            session.add(domain)
            return domain.id
