"""
Created on Jun 20, 2015

@author: fabiomignini
@author: stefanopetrangeli
"""
from sqlalchemy import Column, VARCHAR, Boolean, Integer, Text
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
    attributes = ['id', 'session_id', 'domain_id', 'partial', 'whole_graph', 'sub_graph']
    id = Column(Integer, primary_key=True)
    session_id = Column(VARCHAR(64))
    domain_id = Column(Integer)
    partial = Column(Boolean())
    whole_graph = Column(Text)
    sub_graph = Column(Text)


class Graph(object):
    def __init__(self):
        self.user_session = Session()

    def add_graph(self, nffg, session_id, partial=False, whole_graph=None):
        """
        
        :param nffg: 
        :param session_id: 
        :param partial: 
        :param whole_graph: 
        :type nffg: nffg_library.nffg.NF_FG
        :type session_id: int
        :type partial: bool
        :type whole_graph: nffg_library.nffg.NF_FG
        :return: 
        """
        session = get_session()  
        with session.begin():
            self.id_generator(nffg, session_id)
            graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, partial=partial,
                                   whole_graph=whole_graph.getJSON(domain=True), sub_graph=nffg.getJSON(domain=True))
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
    def get_whole_graph(session_id):
        session = get_session()
        return session.query(GraphModel).filter_by(session_id=session_id).first().whole_graph
    
    @staticmethod
    def get_domain_id(graph_id):
        session = get_session()
        return session.query(GraphModel.domain_id).filter_by(id=graph_id).one().domain_id

    @staticmethod
    def set_domain_id(graph_id, domain_id):
        session = get_session()
        with session.begin():
            logging.debug(session.query(GraphModel).filter_by(id=graph_id).update({"domain_id": domain_id}))
            
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
    """
    def _getGraph(self, graph_id):
        session = get_session()  
        try:
            return session.query(GraphModel).filter_by(id=graph_id).one()
        except Exception as ex:
            logging.error(ex)
            raise GraphNotFound("Graph not found for db id: "+str(graph_id))
    
    def _getGraphID(self, service_graph_id):
        session = get_session()  
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
            return session.query(GraphModel).filter_by(session_id=session_id).one().id
        except Exception as ex:
            logging.error(ex)
            raise GraphNotFound("Graph not found for service graph id: "+str(service_graph_id))
    """      
