"""
Created on Jun 20, 2015

@author: fabiomignini
@author: stefanopetrangeli
"""
from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from orchestrator_core.sql.sql_server import get_session
from sqlalchemy.sql import func

from orchestrator_core.config import Configuration
from orchestrator_core.sql.session import Session
import logging

Base = declarative_base()
sqlserver = Configuration().CONNECTION


class GraphModel(Base):
    """
    Maps the database table graph
    """
    __tablename__ = 'graph'
    attributes = ['id', 'session_id', 'domain_id', 'partial', 'sub_graph_id']
    id = Column(Integer, primary_key=True)
    session_id = Column(VARCHAR(64))
    domain_id = Column(Integer)
    partial = Column(Boolean())
    sub_graph_id = Column(VARCHAR(64))


class Graph(object):
    def __init__(self):
        self.user_session = Session()
        self.graph_id = 0

    def add_graph(self, nffg, session_id, domain_id, partial=False):
        """
        
        :param nffg: 
        :param session_id: 
        :param domain_id: 
        :param partial: 
        :type nffg: nffg_library.nffg.NF_FG
        :type session_id: int
        :type partial: bool
        :return: 
        """
        session = get_session()  
        with session.begin():
            self.id_generator(nffg, session_id)
            #if not partial:
                #graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, domain_id=domain_id, partial=partial)
            #else:
            graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, domain_id=domain_id, partial=partial,
                                       sub_graph_id=nffg.id)
            session.add(graph_ref)

    def delete_session(self, session_id):
        session = get_session()
        graphs_ref = session.query(GraphModel).filter_by(session_id=session_id).all()
        for graph_ref in graphs_ref:
            self.delete_graph(graph_ref.id)
            
    @staticmethod
    def set_graph_partial(graph_id, partial=True):
        session = get_session()  
        with session.begin():
            session.query(GraphModel).filter_by(id=graph_id).update({"partial": partial})

    @staticmethod
    def delete_graph(graph_id):
        session = get_session()
        with session.begin():
            session.query(GraphModel).filter_by(id=graph_id).delete()

    @staticmethod
    def _get_higher_graph_id():
        session = get_session()  
        return session.query(func.max(GraphModel.id).label("max_id")).one().max_id

    @staticmethod
    def get_graphs(session_id):
        session = get_session()
        return session.query(GraphModel).filter_by(session_id=session_id).all()

    @staticmethod
    def get_domain_id(graph_id):
        session = get_session()
        return session.query(GraphModel.domain_id).filter_by(id=graph_id).one().domain_id

    @staticmethod
    def get_sub_graph_id(graph_id):
        session = get_session()
        return session.query(GraphModel).filter_by(id=graph_id).one().sub_graph_id

    def id_generator(self, nffg, session_id, update=False, graph_id=None):
        graph_base_id = self._get_higher_graph_id()
        if graph_base_id is not None:
            self.graph_id = int(graph_base_id) + 1
        else:
            self.graph_id = 0
        if not update:
            nffg.db_id = self.graph_id
        else:
            session = get_session()  
            if graph_id is None:
                graphs_ref = session.query(GraphModel).filter_by(session_id = session_id).all()
                nffg.db_id = graphs_ref[0].id
            else:
                nffg.db_id = graph_id            
