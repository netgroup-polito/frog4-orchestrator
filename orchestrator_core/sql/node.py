'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import logging
from orchestrator_core.config import Configuration
from orchestrator_core.exception import NodeNotFound, ControllerNotFound, UserLocationNotFound
from orchestrator_core.sql.sql_server import get_session

Base = declarative_base()

class NodeModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'node'
    attributes = ['id', 'name', 'type','domain_id','availability_zone','openstack_controller', 'openflow_controller', 'do_ip', 'do_port']
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(64))
    
    '''
    This field is used to specify what kind of component adapter should be used.
    It can assume the following values:
        HeatCA             # for the FROG component adapter
        OpenStack_compute  # this value doesn't correspond to a component_adapter
                           # in this type of nodes is not possible to directly
                           # instantiate a VNF
        JolnetCA           # for the Jolnet component adapter
        UnifiedNode        # for the Universal node component adapter 
    '''
    type = Column(VARCHAR(64))
    domain_id = Column(VARCHAR(64))
    

class Node(object):
    def __init__(self):
        pass
    
    def addNode(self, name, _type, domain_id, update=False):
        session = get_session()
        with session.begin():
            node_base_id = self._get_higher_node_id()
            if node_base_id is not None:
                node_id = int(node_base_id) + 1
            else:
                node_id = 0
            node_ref = NodeModel(id=node_id, name=name,type=_type, domain_id=domain_id)
            session.add(node_ref)
    
    def getNode(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel).filter_by(id = node_id).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
        
    def getNodeID(self, user_id):
        '''
        This method should return the ingress and egress node for a specific user
        '''
        pass
    
    def getInstantiationNode(self):
        session = get_session()
        try:
            return session.query(NodeModel).filter(NodeModel.type != 'HeatCA' ).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found.")
        
    def getNodeFromNodeID(self, domain_id):
        session = get_session()
        try:
            return session.query(NodeModel).filter_by(domain_id = domain_id).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found for domain id: "+str(domain_id))
    
    def getNodeFromName(self, name):
        session = get_session()
        try:
            return session.query(NodeModel).filter_by(name = name).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found for name: "+str(name))   

    def getNodeDomainID(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.domain_id).filter_by(id = node_id).one().domain_id
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))

    def getComponentAdapter(self, node_id):
        session = get_session()
        logging.debug("node_id: "+str(node_id))
        try:
            return session.query(NodeModel.type).filter_by(id = node_id).one().type
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found")
        
    def _get_higher_node_id(self):  
        session = get_session()  
        return session.query(func.max(NodeModel.id).label("max_id")).one().max_id
    
        