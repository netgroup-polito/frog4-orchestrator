'''
@author: fabiomignini
@author: stefanopetrangeli
'''

import json
import logging
from .scheduler import Scheduler
import uuid

from orchestrator_core.exception import sessionNotFound, GraphError
from orchestrator_core.nffg_manager import NFFG_Manager
from orchestrator_core.sql.session import Session
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.domain import Domain  
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.config import Configuration
from collections import OrderedDict
from orchestrator_core.ca_rest import CA_Interface
from sqlalchemy.orm.exc import NoResultFound
from requests.exceptions import HTTPError, ConnectionError

DEBUG_MODE = Configuration().DEBUG_MODE


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator_core
    '''
    def __init__(self, user_data):
        self.user_data = user_data

    def get(self, nffg_id):
        session = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False)
        logging.debug("Getting session: "+str(session.id))
        graphs_ref = Graph().getGraphs(session.id)
        instantiated_nffgs = []
        for graph_ref in graphs_ref:
            domain = Domain().getDomain(Graph().getDomainID(graph_ref.id))
            instantiated_nffgs.append(CA_Interface(self.user_data, domain).getNFFG(graph_ref.id))
        
        if not instantiated_nffgs:
            raise NoResultFound()
        # If the graph has been split, we need to rebuild the original nffg
        if len(instantiated_nffgs) == 2:
            instantiated_nffgs[0].join(instantiated_nffgs[1])
        if len(instantiated_nffgs) == 3:
            # Second domain is discarded because not present in the original nffg
            instantiated_nffgs[0].join(instantiated_nffgs[2])
       
        instantiated_nffgs[0].id = str(nffg_id)
        return instantiated_nffgs[0].getJSON()
    
    def delete(self, nffg_id):        
        session = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False)
        logging.debug("Deleting session: "+str(session.id))

        graphs_ref = Graph().getGraphs(session.id)
        for graph_ref in graphs_ref:
            domain = Domain().getDomain(Graph().getDomainID(graph_ref.id))
            
            # Get instantiated nffg
            #TODO: get_nffg to the ca
            #instantiated_nffg = Graph().get_nffg(graph_ref.id)
            #logging.debug('NF-FG that we are going to delete: '+instantiated_nffg.getJSON())
            
            # Check external connections, if a graph is connected to this, the deletion will be cancelled
            #if self.checkExternalConnections(instantiated_nffg):
            #    raise Exception("This graph has been connected with other graph, delete these graph before to delete this.")
            
            # Analyze end-point connections
            #remote_nffgs_dict = self.analizeRemoteConnection(instantiated_nffg, node, delete=True)
            
            # If needed, update the remote graph
            #self.updateRemoteGraph(remote_nffgs_dict)
            
            # De-instantiate profile
            #orchestrator = Scheduler(graph_ref.id, self.user_data).getInstance(node)
            
            try:
                if DEBUG_MODE is True:
                    logging.debug(domain.ip + ":"+  str(domain.port) + " "+ str(graph_ref.id))
                else:
                    CA_Interface(self.user_data, domain).delete(graph_ref.id)
            except Exception as ex:
                logging.exception(ex)
                Session().set_error(session.id)
                raise ex
            
        logging.debug('Session deleted: '+str(session.id))
        # Set the field ended in the table session to the actual datetime        
        Graph().delete_session(session.id)
        Session().set_ended(session.id)
    
    def update(self, nffg, delete = False):        
        session = Session().get_active_user_session_by_nf_fg_id(nffg.id, error_aware=True)
        Session().updateStatus(session.id, 'updating')
        
        # Get profile from session
        graphs_ref = Graph().getGraphs(session.id)
        if len(graphs_ref) > 1:
            # If the graph has been split, the smart update is not supported
            logging.warning("The graph has been split in various nffg, in this case the smart update is not supported.")
            Session().updateStatus(session.id, 'complete')
            self.delete(nffg.id)
        else:
            #graph instantiated in a single domain
            old_graph = graphs_ref[0]
            nffg.db_id = old_graph.id
            
            # Get VNFs templates
            self.prepareNFFG(nffg)
            
            #old_node = Node().getNode(Graph().getNodeID(old_graph.id))
            old_domain = Domain().getDomain(Graph().getDomainID(old_graph.id))

            ##scheduler = Scheduler(old_graph.id, self.user_data)
            ##new_node = scheduler.schedule(nffg)
            domains, nffgs = Scheduler().schedule(nffg)
            
            old_domain_present=False
            for domain in domains:
                if domain.id == old_domain.id:
                    old_domain_present = True
                    break
            
            if old_domain_present is False:
                logging.warning("The graph will be instantiated in a different domain...deleting old graph")
                if DEBUG_MODE is False:
                    CA_Interface(self.user_data, old_domain).delete(old_graph.id)
                Graph().delete_session(session.id)                
            
            domain_nffg_dict = OrderedDict()
            for i in range(0, len(domains)):
                domain_nffg_dict[domains[i]]=nffgs[i]
                
            for new_domain, new_nffg in domain_nffg_dict.items():
                # Change the remote graph ID in remote_endpoint_id to the internal value
                self.convertRemoteGraphID(new_nffg, new_domain)
                # If the orchestrator has to connect two graphs in different nodes,
                # the end-points must be characterized to allow a connection between nodes
                
                ##remote_nffgs_dict = self.analizeRemoteConnection(nffg, new_domain)
            
                # If needed, update the remote graph
                ##self.updateRemoteGraph(remote_nffgs_dict)
                
                if new_domain.id == old_domain.id:
                    Graph().setGraphPartial(new_nffg.db_id, partial=len(domain_nffg_dict)>1)
                else:
                    Graph().add_graph(new_nffg, session.id, partial=len(domain_nffg_dict)>1)
                    Graph().setDomainID(new_nffg.db_id, new_domain.id)
                    
                new_nffg.id = str(new_nffg.db_id)
                
                if DEBUG_MODE is True:
                    logging.debug(new_domain.ip + ":"+  str(new_domain.port) + " "+ new_nffg.id+"\n"+new_nffg.getJSON())
                else:
                    CA_Interface(self.user_data, new_domain).put(new_nffg)
               
            Session().updateStatus(session.id, 'complete')
            if len(domains)>1:
                Session().updateSessionDomain(session.id, domains[0].id, domain.id)
            else:
                Session().updateSessionDomain(session.id, new_domain.id, new_domain.id)     
        
        #Session().updateSessionNode(session.id, new_node.id, new_node.id)
        return session.id
        
    def put(self, nffg):
        """
        Manage the request of NF-FG instantiation
        """
        logging.debug('Put from user '+self.user_data.username+" of tenant "+self.user_data.tenant)
        if self.checkNFFGStatus(nffg.id) is True:
            logging.debug('NF-FG already instantiated, trying to update it')
            session_id = self.update(nffg)
            logging.debug('Update completed')
        else:
            session_id  = uuid.uuid4().hex
            Session().inizializeSession(session_id, self.user_data.getUserID(), nffg.id, nffg.name)
            try:
                # Manage profile
                self.prepareNFFG(nffg)
                                 
                ##Graph().id_generator(nffg, session_id)
                domains, nffgs = Scheduler().schedule(nffg)
                domain_nffg_dict = OrderedDict()
                for i in range(0, len(domains)):
                    domain_nffg_dict[domains[i]]=nffgs[i]
                
                for domain, nffg in domain_nffg_dict.items():
                    # Change the remote graph ID in remote_endpoint_id to the internal value
                    self.convertRemoteGraphID(nffg, domain)
                    
                    # If the orchestrator has to connect two graphs in different nodes,
                    # the end-points must be characterized to allow a connection between nodes
                    ##remote_nffgs_dict = self.analizeRemoteConnection(nffg, domain)
                    
                    # If needed, update the remote graph
                    ##self.updateRemoteGraph(remote_nffgs_dict)
                    
                    # Save the graph in the database, with the state initializing
                    Graph().add_graph(nffg, session_id, partial=len(domain_nffg_dict)>1)
                    
                    Graph().setDomainID(nffg.db_id, domain.id)
                    
                    # Instantiate profile
                    logging.info('Call CA to instantiate NF-FG')
                    nffg.id = str(nffg.db_id)
                    if DEBUG_MODE is True:
                        logging.debug(domain.ip + ":"+  str(domain.port) + " "+ nffg.id+"\n"+nffg.getJSON())
                    else:
                        CA_Interface(self.user_data, domain).put(nffg)
                    logging.debug('NF-FG instantiated')
                     
                if len(domains)>1:
                    Session().updateSessionDomain(session_id, domains[0].id, domain.id)
                else:
                    Session().updateSessionDomain(session_id, domain.id, domain.id)

                #debug   
                #Session().set_error(session_id)
            except (HTTPError, ConnectionError) as ex:
                logging.exception(ex)
                Graph().delete_graph(nffg.db_id)
                Session().set_error(session_id)
                raise ex
            except Exception as ex:
                logging.exception(ex)
                '''
                Graph().delete_graph(nffg.db_id)
                '''
                Session().set_error(session_id)
                raise ex
        
        Session().updateStatus(session_id, 'complete')
                                
        return session_id
        
    def prepareNFFG(self, nffg):
        manager = NFFG_Manager(nffg)  
        
        # Retrieve the VNF templates, if a node is a new graph, expand it
        logging.debug('Add templates to nffg')
        manager.addTemplates()
        logging.debug('Post expansion: '+nffg.getJSON())
        
        # Optimize NF-FG, currently the switch VNF when possible will be collapsed
        manager.mergeUselessVNFs()   
        
        # Change the remote node ID in remote_endpoint_id and in prepare_connection_to_remote_endpoint_id to the internal value
        #self.convertRemoteGraphID(nffg)
        
    def checkNFFGStatus(self, service_graph_id):
        # TODO: Check if the graph exists, if true
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
        except sessionNotFound:
            return False
        
        status = self.getResourcesStatus(session_id)
        
        if status is None:
            return False
        # If the status of the graph is complete, return False
        if status['status'] == 'complete':
            return True
        # If the graph is in ERROR.. raise a proper exception
        if status['status'] == 'error':
            raise GraphError("The graph has encountered a fatal error, contact the administrator")
        # TODO:  If the graph is still under instantiation returns 409
        if status['status'] == 'in_progress':
            raise Exception("Graph busy")
        # If the graph is deleted, return True
        if status['status'] == 'ended' or status['status'] == 'not_found':
            return False
    
    def getStatus(self, nffg_id):
        '''
        Returns the status of the graph
        '''        
        logging.debug("Getting resources information for graph id: "+str(nffg_id))
        # TODO: have I to manage a sort of cache? Reading from db the status, maybe
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id).id
        
        logging.debug("Corresponding to session id: "+str(session_id))
        status = self.getResourcesStatus(session_id)
        return json.dumps(status)
    
    def getResourcesStatus(self, session_id):
        graphs_ref = Graph().getGraphs(session_id)
        for graph_ref in graphs_ref:
            # Check where the nffg is instantiated and get the concerned domain orchestrator
            domain = Domain().getDomain(Graph().getDomainID(graph_ref.id))
            
            status = {}
            if DEBUG_MODE is True:
                status['status'] = 'complete'
                status['percentage_completed'] = 100
            else:
                status = CA_Interface(self.user_data, domain).getNFFGStatus(graph_ref.id)
            logging.debug(status)
            return status
    
    def convertRemoteGraphID(self, nffg, domain):
        '''
        Convert the remote graph id present in the remote_endpoint_id (inside the end-point),
        in the internal ID created by the orchestrator (that is the one sent to the domain orchestrator).
        '''
        for end_point in nffg.end_points:
            remote_domain_found = False
            if end_point.remote_endpoint_id is not None:
                session_id = Session().get_active_user_session_by_nf_fg_id(end_point.remote_endpoint_id.split(':')[0], error_aware=True).id
                graphs_ref = Graph().getGraphs(session_id)
                for graph_ref in graphs_ref:
                    if graph_ref.domain_id == domain.id:
                        end_point.remote_endpoint_id = str(graph_ref.id)+ ':' +end_point.remote_endpoint_id.split(':')[1]
                        remote_domain_found = True
                        break
                if remote_domain_found is False:
                    raise GraphError("Local domain and remote domain are different for remote_endpoint_id: "+str(end_point.remote_endpoint_id))
                
    
    def updateRemoteGraph(self, remote_nffgs_dict):
        #Not used anymore
        for remote_nffg in remote_nffgs_dict.values():
            session = Session().get_active_user_session_by_nf_fg_id(remote_nffg.id, error_aware=True)
            remote_user_data = UserData()
            remote_user_data.getUserData(session.user_id)
            Session().updateStatus(session.id, 'updating')
            self.prepareNFFG(remote_nffg)
            scheduler = Scheduler(remote_nffg.db_id, remote_user_data)
            orchestrator, node = scheduler.schedule(remote_nffg)
            old_nf_fg = Graph().get_nffg(remote_nffg.db_id)
            try:
                orchestrator.updateProfile(remote_nffg, old_nf_fg, node)
            except Exception as ex:
                logging.exception(ex)
                '''
                Graph().delete_graph(nffg.db_id)
                '''
                Session().set_error(session.id)
                raise ex     
            Session().updateStatus(session.id, 'complete')
    
    def analizeRemoteConnection(self, nffg, node, delete=False):
        #Not used anymore
        #TODO: nffg.db_id not set
        '''
        Check if the nffg will be installed on the same domain of an eventually remote graph.
        In this case, the orchestrator has to characterize in a better way the end-point. 
        '''
        # Getting remote graphs
        remote_nffgs_dict = {}
        for end_point in nffg.end_points:
            if end_point.remote_endpoint_id is not None:
                remote_graph_id = end_point.remote_endpoint_id.split(':')[0]
                if remote_graph_id in remote_nffgs_dict:
                    remote_nffg = remote_nffgs_dict[remote_graph_id]
                else:
                    #remote_nffg = Graph().get_nffg(end_point.remote_endpoint_id.split(':')[0])
                    domain = Domain().getDomain(Graph().getDomainID(remote_graph_id))
                    remote_nffg = CA_Interface(self.user_data, domain).getNFFG(remote_graph_id)
                    remote_nffgs_dict[remote_graph_id] = remote_nffg
                    #remote_nffgs_dict[str(remote_nffg.db_id)] = remote_nffg
                for remote_end_point in remote_nffg.end_points:
                    if remote_end_point.id == end_point.remote_endpoint_id.split(':')[1]:
                        if delete is False:
                            remote_end_point.prepare_connection_to_remote_endpoint_ids.append(str(nffg.db_id)+':'+end_point.id)
                        else:
                            remote_end_point.prepare_connection_to_remote_endpoint_ids.remove(str(nffg.db_id)+':'+end_point.id)
                            
        # TODO: characterization in case of different node instantiation
        
        return remote_nffgs_dict
    
    def checkExternalConnections(self, nffg):
        #Not used anymore
        for end_point in nffg.end_points:
            if end_point.prepare_connection_to_remote_endpoint_ids:
                return True
        return False