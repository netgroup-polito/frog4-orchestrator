'''
Created on Oct 1, 2014

@author: fabiomignini
@author: stefanopetrangeli
'''
from sqlalchemy import Column, DateTime, func, VARCHAR, desc
from orchestrator_core.sql.sql_server import get_session
from sqlalchemy.ext.declarative import declarative_base
from orchestrator_core.exception import sessionNotFound
from sqlalchemy.orm.exc import NoResultFound

import base64
import datetime
import logging

Base = declarative_base()

class SessionModel(Base):
    '''
    Maps the database table session
    '''
    __tablename__ = 'session'
    attributes = ['id', 'user_id', 'service_graph_id', 'service_graph_name', 'nf_fgraph', 'status','started_at',
                  'last_update','error','ended']
    id = Column(VARCHAR(64), primary_key=True)
    user_id = Column(VARCHAR(64))
    service_graph_id = Column(VARCHAR(64))
    service_graph_name = Column(VARCHAR(64))
    nf_fgraph = Column(VARCHAR(60000))
    status = Column(VARCHAR(64))
    started_at = Column(DateTime)
    last_update = Column(DateTime, default=func.now())
    error = Column(DateTime)
    ended = Column(DateTime)

class Session(object):
    def __init__(self):
        pass
    
    def inizializeSession(self, session_id, user_id, service_graph_id, service_graph_name, nffg_json):
        '''
        inizialize the session in db
        '''
        session = get_session()  
        with session.begin():
            session_ref = SessionModel(id=session_id, user_id = user_id, service_graph_id = service_graph_id,
                                started_at = datetime.datetime.now(), service_graph_name = service_graph_name,
                                last_update = datetime.datetime.now(), status = 'inizialization',
                                       nf_fgraph = base64.b64encode(nffg_json))
            session.add(session_ref)
        pass

    def updateStatus(self, session_id, status):
        session = get_session()  
        with session.begin():
            session.query(SessionModel).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None)\
                .update({"last_update":datetime.datetime.now(), 'status':status})
    
    def get_active_user_sessions(self, user_id):
        '''
        returns if exists all active session of the user
        '''
        session = get_session()
        session_ref = session.query(SessionModel).filter_by(user_id = user_id).filter_by(ended = None)\
            .filter_by(error = None).all()
        if len(session_ref) == 0 :
            raise sessionNotFound("No active Graph")
        return session_ref    
    
    def set_ended(self, session_id):
        '''
        Set the ended status for the session identified with session_id
        '''
        session = get_session() 
        with session.begin():       
            session.query(SessionModel).filter_by(id=session_id).update({"ended":datetime.datetime.now()},
                                                                        synchronize_session = False)

    def set_error(self, session_id):
        '''
        Set the error status for the active session associated to the user id passed
        '''
        session = get_session()
        with session.begin():
            logging.debug("Put session for session "+str(session_id)+" in error")
            session.query(SessionModel).filter_by(id=session_id).filter_by(ended = None).filter_by(error = None)\
                .update({"error":datetime.datetime.now()}, synchronize_session = False)

    def get_active_user_session_by_nf_fg_id(self, service_graph_id, error_aware=True):
        session = get_session()
        if error_aware:
            session_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).filter_by\
                (ended = None).filter_by(error = None).first()
        else:
            session_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).filter_by\
                (ended = None).order_by(desc(SessionModel.started_at)).first()
        if session_ref is None:
            raise sessionNotFound("No Result Found for graph id: "+str(service_graph_id))
        return session_ref

    def updateSession(self, session_id, status, graph_name, nffg_json):
        session = get_session()
        with session.begin():
            session.query(SessionModel).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None)\
                .update({"last_update":datetime.datetime.now(), 'status':status, 'service_graph_name':graph_name,
                         'nf_fgraph':base64.b64encode(nffg_json)})

    def get_nffg_id(self, session_id):
        session = get_session()
        return session.query(SessionModel).filter_by(id = session_id).one()

    def get_nffg_json(self, session_id):
        session = get_session()
        graphs_ref = session.query(SessionModel).filter_by(id = session_id).filter_by(ended = None).first()
        if graphs_ref is None:
            raise NoResultFound()
        return graphs_ref

    def get_current_user_session_by_nffg_id(self, service_graph_id, user_id):
        session = get_session()
        session_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).filter_by\
            (user_id = user_id).filter_by(ended = None).order_by(desc(SessionModel.started_at)).first()
        if session_ref is None:
            raise NoResultFound()
        return session_ref

    def delete_sessions(self, service_graph_id):
        session = get_session()
        Sessions_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).all()
        for Session_ref in Sessions_ref:
            self.delete_session(Session_ref.id)

    def delete_session(self, session_id):
        session = get_session()
        with session.begin():
            session.query(SessionModel).filter_by(id = session_id).delete()

    def check_nffg_id(self, nffg_id):
        session = get_session()
        with session.begin():
            return session.query(SessionModel).filter_by(service_graph_id = nffg_id).all()

