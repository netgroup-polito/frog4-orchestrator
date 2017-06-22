"""
@author: fabiomignini
@author: stefanopetrangeli
@author: gabrielecastellano
"""

import json
import logging
import base64

from nffg_library.nffg import NF_FG
from orchestrator_core.scheduler import Scheduler
from orchestrator_core.virtual_topology import VirtualTopology
from .splitter import Splitter
import uuid
import random
import string

from orchestrator_core.exception import sessionNotFound, GraphError, FrogDataStoreError, NoFunctionalCapabilityFound, \
    FunctionalCapabilityAlreadyInUse, FeasibleDomainNotFoundForNFFGElement, NoGraphFound, DomainNotFound
from orchestrator_core.nffg_manager import NFFG_Manager
from orchestrator_core.sql.session import Session
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.domain import Domain
from orchestrator_core.config import Configuration
from collections import OrderedDict
from orchestrator_core.ca_rest import CA_Interface
from requests.exceptions import HTTPError, ConnectionError
from orchestrator_core.sql.domains_info import DomainInformation

DEBUG_MODE = Configuration().DEBUG_MODE


class UpperLayerOrchestratorController(object):
    """
    Class that performs the logic of orchestrator_core
    """
    def __init__(self, user_data, counter=None):
        self.user_data = user_data
        self.counter = counter

    def get(self, nffg_id):
        if nffg_id is None:
            # Get the list of active graphs
            sessions = Session().get_active_user_sessions(self.user_data.id)
            graphs = []
            for session in sessions:
                response_json = json.loads(base64.b64decode(Session().get_nffg_json(session.id).nf_fgraph).decode('utf-8'))
                graphs.append(response_json)
            response_dict = dict()
            response_dict["NF-FG"] = graphs
            return json.dumps(response_dict)
        else:
            session_id = Session().get_current_user_session_by_nffg_id(nffg_id, self.user_data.id).id
            logging.debug("Getting session: "+str(session_id))
            response_json = json.loads(base64.b64decode(Session().get_nffg_json(session_id).nf_fgraph).decode('utf-8'))
            return json.dumps(response_json)
    
    def delete(self, nffg_id):
        session = Session().get_current_user_session_by_nffg_id(nffg_id, self.user_data.id)
        logging.debug("Deleting session: " + str(session.id))
        graphs_ref = Graph().get_graphs(session.id)

        for graph_ref in graphs_ref:
            domain = Domain().getDomain(Graph().get_domain_id(graph_ref.id))
            sub_graph_id = Graph().get_sub_graph_id(graph_ref.id)
            try:
                if DEBUG_MODE is True:
                    logging.debug(domain.ip + ":" + str(domain.port) + " " + str(sub_graph_id))
                else:
                    CA_Interface(self.user_data, domain).delete(sub_graph_id)
            except Exception as ex:
                logging.exception(ex)
                Session().set_error(session.id)
                raise ex
            
        logging.debug('Session deleted: ' + str(session.id))
        # Set the field ended in the table session to the actual datetime        
        Graph().delete_session(session.id)
        Session().delete_sessions(nffg_id)
        # Session().set_ended(session.id)
    
    def update(self, nffg):

        session = Session().get_active_user_session_by_nf_fg_id(nffg.id, error_aware=True)
        nffg_json = nffg.getJSON(domain=True).encode('utf-8')
        Session().updateSession(session.id, 'updating', nffg.name, nffg_json)
        # Get profile from session
        graphs_ref = Graph().get_graphs(session.id)
        try:
            # Get VNFs templates
            self.prepare_nffg(nffg)

            # Fetch nffg yet deployed
            old_nffg_dict = json.loads(base64.b64decode(Session().get_nffg_json(session.id).nf_fgraph).decode('utf-8'))
            old_nffg = NF_FG()
            old_nffg.parseDict(old_nffg_dict)

            # Get the diff nffg
            diff_nffg = old_nffg.diff(nffg)

            # label nffg to deploy elements with the status respect the old graph
            self.label_nffg_elements_with_status(nffg, diff_nffg)

            # TODO add here code depending on what we want:
            # 1. relocate old NF if a better placement is available -> copy first part from put()
            # 2. keep old NF placement and schedule just new one -> label here old NF and then copy first part of put()
            # current code is for case 1.

            # 0) Create virtual topology basing on current domain information
            virtual_topology = VirtualTopology(DomainInformation().get_domains_info())

            # 1) Fetch a map with a list of feasible domains for each NF of the nffg and for each ep
            feasible_nf_domains_dict = self.get_nf_feasible_domains_map(nffg)
            feasible_ep_domains_dict = self.get_ep_feasible_domains_map(nffg)

            # 2) Perform the scheduling algorithm (tag nffg untagged elements with best domain)
            scheduler = Scheduler(virtual_topology, feasible_nf_domains_dict, feasible_ep_domains_dict)
            split_flows = scheduler.schedule(nffg)

            # 3) Generate a sub-graph for each involved domain
            domains, nffgs = Splitter(self.counter).split(nffg, split_flows)

            domain_nffg_dict = OrderedDict()
            for i in range(0, len(domains)):
                domain_nffg_dict[domains[i]] = nffgs[i]

            # Maps each domain ID to instantiated graph IDs in it
            old_domain_graph = OrderedDict()
            for graph_ref in graphs_ref:
                if graph_ref.domain_id not in old_domain_graph:
                    old_domain_graph[graph_ref.domain_id] = []
                old_domain_graph[graph_ref.domain_id].append(graph_ref.id)

            # Search for domains no longer involved in the new graph
            to_be_removed_domains = []
            for old_domain_id in old_domain_graph.keys():
                found = False
                for new_domain in domains:
                    if new_domain.id == old_domain_id:
                        found = True
                        break
                if found is False:
                    to_be_removed_domains.append(old_domain_id)
                    
            for domain_id in to_be_removed_domains:
                logging.warning("The domain " + str(domain_id) + " is no longer involved after the update..." +
                                                                 "deleting (sub)graph(s) instantiated on it.")
                for graph_db_id in old_domain_graph[domain_id]:
                    domain = Domain().getDomain(domain_id)
                    sub_graph_id = Graph().get_sub_graph_id(graph_db_id)
                    if DEBUG_MODE is True:
                        logging.debug("DELETE " + domain.ip + ":" + str(domain.port) + " " + str(sub_graph_id))
                    else:
                        CA_Interface(self.user_data, domain).delete(sub_graph_id)
                    Graph().delete_graph(graph_db_id)

            for new_domain, new_nffg in domain_nffg_dict.items():
                if new_domain.id in old_domain_graph.keys():
                    # domain yet involved
                    new_nffg.db_id = old_domain_graph[new_domain.id].pop()
                    new_nffg.id = Graph().get_sub_graph_id(new_nffg.db_id)
                    Graph().set_graph_partial(new_nffg.db_id, partial=len(domain_nffg_dict) > 1)
                else:
                    # domain not yet involved
                    # chose an id for the new sub-graph
                    new_nffg.id = str(nffg.id)
                    Graph().add_graph(new_nffg, session.id, new_domain.id, partial=len(domain_nffg_dict) > 1)
                new_nffg.sanitizeEpIDs()

                if DEBUG_MODE is True:
                    logging.debug(new_domain.ip+":"+str(new_domain.port)+" "+new_nffg.id+"\n"+new_nffg.getJSON())
                else:
                    CA_Interface(self.user_data, new_domain).put(new_nffg)

            Session().updateStatus(session.id, 'complete')

        except (HTTPError, ConnectionError) as ex:
            logging.exception(ex)
            Graph().delete_session(session.id)
            Session().set_error(session.id)
            raise ex
        except FrogDataStoreError as ex:
            logging.exception(ex)
            # Session().set_error(session.id)
            raise ex
        except Exception as ex:
            logging.exception(ex)
            '''
            Graph().delete_graph(nffg.db_id)
            '''
            Session().set_error(session.id)
            raise ex
        
        return session.id
        
    def put(self, nffg, nffg_id):
        """
        Manage the request of NF-FG instantiation
        :param nffg:
        :param nffg_id:
        :type nffg: nffg_library.nffg.NF_FG
        :type nffg_id: int
        """

        logging.info('Graph put request from user '+self.user_data.username)

        if nffg_id is not None:
            nffg.id = str(nffg_id)
            if self.check_nffg_status(nffg.id) is True:
                logging.debug('NF-FG already instantiated, trying to update it')
                session_id = self.update(nffg)
                logging.debug('Update completed')

            else:
                raise NoGraphFound("EXCEPTION - Please first insert this graph then try to update")

        else:

            while True:
                new_nffg_id = ''.join(random.SystemRandom().choice(string.digits) for _ in range(8))
                old_nffg_id = Session().check_nffg_id(new_nffg_id)
                if len(old_nffg_id) == 0:
                    nffg.id = str(new_nffg_id)
                    break

            nffg_json = nffg.getJSON(domain=True).encode('utf-8')
            session_id = uuid.uuid4().hex
            Session().inizializeSession(session_id, self.user_data.id, nffg.id, nffg.name, nffg_json)
            try:
                # Manage profile
                self.prepare_nffg(nffg)

                # 0) Create virtual topology basing on current domain information
                logging.info("Generating virtual topology...")
                virtual_topology = VirtualTopology(DomainInformation().get_domains_info())

                # 1) Fetch a map with a list of feasible domains for each NF of the nffg and for each ep
                logging.info("Finding feasible domains...")
                feasible_nf_domains_dict = self.get_nf_feasible_domains_map(nffg)
                feasible_ep_domains_dict = self.get_ep_feasible_domains_map(nffg)

                # 2) Perform the scheduling algorithm (tag nffg untagged elements with best domain)
                logging.info("Performing scheduling...")
                scheduler = Scheduler(virtual_topology, feasible_nf_domains_dict, feasible_ep_domains_dict)
                split_flows = scheduler.schedule(nffg)
                logging.debug(json.dumps(nffg.getDict(domain=True)))

                # 3) Generate a sub-graph for each involved domain
                logging.info("Splitting graph...")
                domains, nffgs = Splitter(self.counter).split(nffg, split_flows)

                domain_nffg_dict = OrderedDict()
                for i in range(0, len(domains)):
                    nffgs[i].sanitizeEpIDs()
                    domain_nffg_dict[domains[i]] = nffgs[i]

                for domain, sub_nffg in domain_nffg_dict.items():

                    # Chose an id for the sub-graph
                    sub_nffg.id = str(nffg.id)

                    # Save the graph in the database
                    Graph().add_graph(sub_nffg, session_id, domain_id=domain.id, partial=len(domain_nffg_dict) > 1)

                    # Instantiate profile
                    logging.info("Instantiate sub-graph on domain '" + domain.name + "'")

                    if DEBUG_MODE is True:
                        logging.debug(domain.ip + ":" + str(domain.port) + " " + sub_nffg.id+"\n"+sub_nffg.getJSON())
                    else:
                        CA_Interface(self.user_data, domain).put(sub_nffg)

                    logging.info("sub-graph correctly instantiated  on domain '" + domain.name + "'")

                Session().updateStatus(session_id, 'complete')
                logging.info("NF-FG correctly instantiated on session " + session_id)
                # Session().set_error(session_id)
            except (HTTPError, ConnectionError) as ex:
                logging.exception(ex)
                Graph().delete_session(session_id)
                Session().set_error(session_id)
                raise ex
            except FrogDataStoreError as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except NoFunctionalCapabilityFound as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except FunctionalCapabilityAlreadyInUse as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except FeasibleDomainNotFoundForNFFGElement as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except DomainNotFound as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except Exception as ex:
                logging.exception(ex)
                '''
                Graph().delete_graph(nffg.db_id)
                '''
                Session().set_error(session_id)
                raise ex
        nffg_id = Session().get_nffg_id(session_id).service_graph_id
        return nffg_id
        
    @staticmethod
    def prepare_nffg(nffg):
        manager = NFFG_Manager(nffg)  
        
        # Retrieve the VNF templates, if a node is a new graph, expand it
        logging.debug('Add templates to nffg')
        manager.addTemplates()
        logging.debug('Post expansion: '+nffg.getJSON())
        
        # Optimize NF-FG, currently the switch VNF when possible will be collapsed
        manager.mergeUselessVNFs()   
        
    def check_nffg_status(self, service_graph_id):
        # TODO: Check if the graph exists, if true
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
        except sessionNotFound:
            return False
        
        status = self.get_resources_status(session_id)
        
        if status is None:
            return False
        # If the status of the graph is complete, return False
        if status['status'] == 'complete':
            return True
        # TODO:  If the graph is still under instantiation returns 409
        if status['status'] == 'in_progress':
            raise Exception("Graph busy")
        # If the graph is in ERROR.. raise a proper exception # not currently managed
        if status['status'] == 'error':
            raise GraphError("The graph has encountered a fatal error, contact the administrator")
        # If the graph is deleted, return True # not currently managed
        if status['status'] == 'ended' or status['status'] == 'not_found':
            return False
    
    def get_status(self, nffg_id):
        """
        Returns the status of the graph
        """
        logging.debug("Getting resources information for graph id: "+str(nffg_id))
        # TODO: have I to manage a sort of cache? Reading from db the status, maybe
        session_id = Session().get_current_user_session_by_nffg_id(nffg_id, self.user_data.id).id
        logging.debug("Corresponding to session id: "+str(session_id))
        status = self.get_resources_status(session_id)
        return json.dumps(status)
    
    def get_resources_status(self, session_id):
        status = {}
        if DEBUG_MODE is True:
            status['status'] = 'complete'
            status['percentage_completed'] = 100
            return status

        graphs_ref = Graph().get_graphs(session_id)
        num_graphs = len(graphs_ref)
        num_graphs_completed = 0
        for graph_ref in graphs_ref:
            # Check where the nffg is instantiated and get the concerned domain orchestrator
            domain = Domain().getDomain(Graph().get_domain_id(graph_ref.id))
            nffg_status = CA_Interface(self.user_data, domain).getNFFGStatus(graph_ref.sub_graph_id)
            logging.debug(nffg_status)
            if nffg_status['status'] == 'complete':
                num_graphs_completed += 1

        logging.debug("num_graphs_completed "+str(num_graphs_completed))
        logging.debug("num_graphs "+str(num_graphs))

        if num_graphs_completed == num_graphs:
            status['status'] = 'complete'
            if num_graphs != 0:
                status['percentage_completed'] = num_graphs_completed/num_graphs*100
            else:
                status['percentage_completed'] = 100
        else:
            status['status'] = 'in_progress'
            if num_graphs != 0:
                status['percentage_completed'] = num_graphs_completed/num_graphs*100

        return status

    @staticmethod
    def get_nf_feasible_domains_map(nffg):
        """
        Fetch a list of feasible domains for each nffg's NF
        :param nffg:
        :type nffg: NF_FG
        :return:
        :rtype: dict [str, list]
        """

        feasible_domain_dictionary = {}  # feasible means domains that have FC
        domains_info = DomainInformation().get_domains_info()
        for vnf in nffg.vnfs:
            # look for feasible domains for this NF just if there is no pre-assigned domain
            if vnf.status == 'already_deployed':
                feasible_domain_dictionary[vnf.id] = [vnf.domain]
            elif (vnf.domain is not None and vnf.status is None) or vnf.status == 'to_deploy_fixed':
                domain = Domain().getDomainFromName(vnf.domain)
                fc = domains_info[domain.id].capabilities.get_functional_capability(vnf.name.lower())
                if fc is not None and (fc.ready or vnf.status == 'already_deployed'):
                    feasible_domain_dictionary[vnf.id] = [vnf.domain]
                else:
                    raise NoFunctionalCapabilityFound("No suitable FC found for NF '" + vnf.name + "' in domain '" +
                                                      vnf.domain + "' specified in nffg.")
            else:
                old_domain = vnf.domain
                vnf.domain = None
                feasible_domain_dictionary[vnf.id] = []
                for domain_id, domain_info in domains_info.items():
                    logging.debug(domain_info.get_dict())
                    fc = domain_info.capabilities.get_functional_capability(vnf.name.lower())
                    if fc is not None and (fc.ready or old_domain == domain_info.name):
                        feasible_domain_dictionary[vnf.id].append(domain_info.name)
                        logging.debug("Domain '" + domain_info.name + "' is feasible for NF '" + vnf.name + "'")

        logging.debug('feasible_domain_dictionary = %s', feasible_domain_dictionary)

        return feasible_domain_dictionary

    @staticmethod
    def get_ep_feasible_domains_map(nffg):
        """

        :param nffg:
        :type nffg: nffg_library.nffg.NF_FG
        :return:
        """
        feasible_domain_dictionary = {}  # feasible means domains where that EP can be placed
        for ep in nffg.end_points:
            if ep.domain is not None:
                feasible_domain_dictionary[ep.id] = [ep.domain]
            elif nffg.domain is not None:
                feasible_domain_dictionary[ep.id] = [nffg.domain]
            else:
                raise GraphError("Endpoint '" + ep.id + "' is not labeled with a domain, however there is no global " +
                                 "graph domain specified in the nffg.")
        return feasible_domain_dictionary

    @staticmethod
    def label_nffg_elements_with_status(nffg, diff_nffg):
        """
        
        :param nffg: 
        :param diff_nffg:
        :type nffg: NF_FG
        :type diff_nffg: NF_FG
        :return: 
        """

        for diff_vnf in diff_nffg.vnfs:
            if diff_vnf.status == 'already_deployed':
                vnf = nffg.getVNF(diff_nffg.id)
                if vnf is None:
                    continue
                if vnf.domain == diff_vnf.domain:
                    vnf.status = 'already_deployed'
                elif vnf.domain is None:
                    vnf.status = 'to_reschedule'
                    vnf.domain = diff_vnf.domain
                else:
                    vnf.status = 'to_deploy_fixed'
        for vnf in nffg.vnfs:
            if vnf.status is None:
                if vnf.domain is None:
                    vnf.status = 'to_reschedule'
                else:
                    vnf.status = 'to_deploy_fixed'
