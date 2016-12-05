'''
@author: fabiomignini
@author: stefanopetrangeli
'''

import json
import logging
from .scheduler import Scheduler
import uuid

from orchestrator_core.exception import sessionNotFound, GraphError, wrongRequest, VNFRepositoryError, NoCapabilityFound, FunctionalCapabilityAlreadyInUse, VNFNotFoundInVNFRepository
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
from orchestrator_core.sql.domains_info import DomainInformation

DEBUG_MODE = Configuration().DEBUG_MODE


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator_core
    '''
    def __init__(self, user_data, counter=None):
        self.user_data = user_data
        self.counter = counter

    def get(self, nffg_id):
        #TODO: update this function taking into account the new split algorithm
        if nffg_id is None:
            # Get the list of active graphs
            sessions = Session().get_active_user_sessions(self.user_data.id)
            graphs = []
            for session in sessions:
                graph = {}
                graph['graph_id'] = session.service_graph_id
                graph['graph_name'] = session.service_graph_name
                graph['deploy time'] = str(session.started_at)
                graph['last_update_time'] = str(session.last_update)         
                graphs.append(graph)
            response_dict = {}
            response_dict['active_graphs'] = graphs
            return json.dumps(response_dict)
        else:
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
    
    def update(self, nffg):
        session = Session().get_active_user_session_by_nf_fg_id(nffg.id, error_aware=True)
        Session().updateStatus(session.id, 'updating')
        
        # Get profile from session
        graphs_ref = Graph().getGraphs(session.id)
        try:
            # Get VNFs templates
            self.prepareNFFG(nffg)

            domains, nffgs = Scheduler(self.counter).schedule(nffg)

            domain_nffg_dict = OrderedDict()
            for i in range(0, len(domains)):
                domain_nffg_dict[domains[i]]=nffgs[i]

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
                logging.warning("The domain " + str(domain_id) + " is no longer involved after the update...deleting (sub)graph(s) instantiated in it")
                for graph in old_domain_graph[domain_id]:
                    domain = Domain().getDomain(domain_id)
                    if DEBUG_MODE is True:
                        logging.debug(domain.ip + ":"+  str(domain.port) + " "+ str(graph))
                    else:
                        CA_Interface(self.user_data, domain).delete(graph)
                    Graph().delete_graph(graph)


            for new_domain, new_nffg in domain_nffg_dict.items():
                if new_domain.id in old_domain_graph.keys():
                    new_nffg.db_id = old_domain_graph[new_domain.id].pop()
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

        except (HTTPError, ConnectionError) as ex:
            logging.exception(ex)
            Graph().delete_graph(nffg.db_id)
            Session().set_error(session.id)
            raise ex
        except VNFRepositoryError as ex:
            logging.exception(ex)
            #Session().set_error(session.id)
            raise ex
        except Exception as ex:
            logging.exception(ex)
            '''
            Graph().delete_graph(nffg.db_id)
            '''
            Session().set_error(session.id)
            raise ex
        
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
            Session().inizializeSession(session_id, self.user_data.id, nffg.id, nffg.name)
            try:
                # Manage profile
                self.prepareNFFG(nffg)

                # If nffg's vnf domain is not tagged, tag it:

                # 1) Fetch a list of feasible domains with FC for every nffg's vnf and a list of domains with IC. The IC are searched in the VNF Repository and if feasible they are added to the dictionary.
                feasible_domain_dictionary, infra_cap_domain_dictionary = self.generateFeasibleDomainDictionary(nffg)

                # 2) If domain has FC: checks if endpoints' domain matches with a domain from the feasible_domain_dictionary and tag the vnf domain, otherwise if there's an IC tag the vnf domain with the IC domain
                self.checkEnpointDomainAndTagVNF(nffg, feasible_domain_dictionary, infra_cap_domain_dictionary)

                ##Graph().id_generator(nffg, session_id)
                domains, nffgs = Scheduler(self.counter).schedule(nffg)
                domain_nffg_dict = OrderedDict()
                for i in range(0, len(domains)):
                    domain_nffg_dict[domains[i]]=nffgs[i]

                # Check if all vnf are available and ready to use on the selected domain as FC. Otherwise check if any IC is available.
                self.checkVNFAvailabilityOnTheSelectedDomain(domain_nffg_dict, infra_cap_domain_dictionary)


                for domain, nffg in domain_nffg_dict.items():
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

                Session().updateStatus(session_id, 'complete')

                #debug   
                #Session().set_error(session_id)
            except (HTTPError, ConnectionError) as ex:
                logging.exception(ex)
                Graph().delete_graph(nffg.db_id)
                Session().set_error(session_id)
                raise ex
            except VNFRepositoryError as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except NoCapabilityFound as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
            except FunctionalCapabilityAlreadyInUse as ex:
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
        
        #Session().updateStatus(session_id, 'complete')
                                
        return session_id
        
    def prepareNFFG(self, nffg):
        manager = NFFG_Manager(nffg)  
        
        # Retrieve the VNF templates, if a node is a new graph, expand it
        logging.debug('Add templates to nffg')
        manager.addTemplates()
        logging.debug('Post expansion: '+nffg.getJSON())
        
        # Optimize NF-FG, currently the switch VNF when possible will be collapsed
        manager.mergeUselessVNFs()   
        
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
        # TODO:  If the graph is still under instantiation returns 409
        if status['status'] == 'in_progress':
            raise Exception("Graph busy")
        # If the graph is in ERROR.. raise a proper exception # not currently managed
        if status['status'] == 'error':
            raise GraphError("The graph has encountered a fatal error, contact the administrator")
        # If the graph is deleted, return True # not currently managed
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
        status = {}
        if DEBUG_MODE is True:
            status['status'] = 'complete'
            status['percentage_completed'] = 100
            return status

        graphs_ref = Graph().getGraphs(session_id)
        num_graphs = len(graphs_ref)
        num_graphs_completed = 0
        for graph_ref in graphs_ref:
            # Check where the nffg is instantiated and get the concerned domain orchestrator
            domain = Domain().getDomain(Graph().getDomainID(graph_ref.id))
            nffg_status = CA_Interface(self.user_data, domain).getNFFGStatus(graph_ref.id)
            logging.debug(nffg_status)
            if nffg_status['status'] == 'complete':
                num_graphs_completed = num_graphs_completed + 1

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

    def generateFeasibleDomainDictionary(self, nffg):
        # Fetch a list of feasible domains for every nffg's vnf

        feasible_domain_dictionary = {}  # feasible means domains that have FC + GRE support
        infra_cap_domain_dictionary = {}
        domains_info = DomainInformation().get_domain_info()
        for vnf in nffg.vnfs:
            if vnf.domain is None:  # checks if at least one vnf is without domain name
                # logging.debug('Passato di qui1. vnf name = %s', vnf.name)
                domain_list = []
                infra_domain_list = []
                foundGRE = False
                #foundIC = False
                for domain_id, domain_info in domains_info.items():
                    # logging.debug('Passato di qui1. domain_info = %s', domain_info)
                    foundFC = False
                    logging.debug(domain_info.get_dict())
                    for function_capability in domain_info.capabilities.functional_capabilities:
                        if vnf.name.lower() == function_capability.type.lower():
                            foundFC = True
                            for interface in domain_info.hardware_info.interfaces:  # controlla tutte le interfacce ma alla prima che permette GRE esce dal ciclo
                                if interface.gre is True:  # TODO: Con questo algoritmo controllo solo l'interfaccia del dominio di partenza. Da controllare che l'interfaccia remota a cui si collega permetta anche essa GRE
                                    for neighbor in interface.neighbors:  # controlla tutti i neighbors ma appena trova uno che permette GRE esce dal ciclo
                                        if neighbor.neighbor_type == "IP":
                                            logging.debug(
                                                'Ok! The interface %s supports tunnel GRE usage',
                                                interface.name)
                                            foundGRE = True
                                            domain_list.append(domain_info.name)
                                            break
                                if foundGRE is True:
                                    break

                                    # logging.debug('Passato di qui2. domain name = %s', domain_info.name)
                    if foundFC is False: #se non trovo nessuna FC, controllo se ci sono IC
                        for infrastructural_capability in domain_info.capabilities.infrastructural_capabilities:
                            if infrastructural_capability is not None:
                                #foundIC = True
                                domain = Domain().getDomain(domain_id)
                                try:
                                    CA_Interface(self.user_data, domain).checkVNFfromVNFRepository(vnf.name.lower())
                                except VNFNotFoundInVNFRepository as ex:
                                    logging.debug("Error! VNF not found in VNF repository! Domain: %s", domain.id)
                                    #logging.exception(ex)
                                    continue
                                except Exception as err:
                                    logging.exception(err)
                                    raise err

                                infra_domain_list.append(domain_info.name)
                                logging.debug('Found an infrastructural capability = %s', infrastructural_capability)
                                break




                feasible_domain_dictionary[vnf.name.lower()] = domain_list

                logging.debug('feasible_domain_dictionary = %s', feasible_domain_dictionary)

                infra_cap_domain_dictionary[vnf.name.lower()] = infra_domain_list

                logging.debug('infra_cap_domain_dictionary = %s', infra_cap_domain_dictionary)

        return feasible_domain_dictionary, infra_cap_domain_dictionary

    def checkEnpointDomainAndTagVNF(self, nffg, feasible_domain_dictionary, infra_cap_domain_dictionary):
        # Checks if endpoints' domain matches with a domain from the feasible_domain_dictionary
        for vnf in nffg.vnfs:
            if vnf.domain is None:  # checks if at least one vnf is without domain name
                vnfFoundInDict = False
                for dict_vnf_name, dict_domain_list in feasible_domain_dictionary.items():
                    if vnf.name.lower() == dict_vnf_name.lower(): #trovata la vnf nel dizionario dei domini feasible
                        if dict_domain_list is not None:
                            foundSameDomainName = False
                            firstDomainFeasibleFlag = True
                            for domain_name_from_list in dict_domain_list:
                                vnfFoundInDict = True #ho trovato un dominio nella lista
                                if firstDomainFeasibleFlag is True:
                                    first_domain = domain_name_from_list  # primo dominio analizzato e primo endpoint analizzato
                                    firstDomainFeasibleFlag = False
                                for endpoint in nffg.end_points:
                                    if domain_name_from_list.lower() == endpoint.domain.lower():
                                        vnf.domain = endpoint.domain.lower()  # Taggo il vnf domain con lo stesso domain degli endpoint
                                        foundSameDomainName = True
                                        logging.debug('Ok! Functional Capability. Found a feasible domain=endpoint domain: %s', vnf.domain)
                                        break

                                if foundSameDomainName is True:  # domain coincidente trovato esco dal ciclo
                                    break

                            for domain_name_from_list in dict_domain_list:
                                if domain_name_from_list is not None:
                                    if foundSameDomainName is False:
                                        vnf.domain = first_domain  # se non trovo nessun endpoint domain che coincide taggo la vnf col primo feasible domain analizzato
                                        logging.debug(
                                            'No matching endpoint domain found. Tagging the VNF with the first feasible domain in the list: %s',
                                            vnf.domain)
                if vnfFoundInDict is False: #se non trova la vnf nel dizionario controlla se c'è almeno una IC
                    for infra_cap_vnf_name, infra_cap_domain_list in infra_cap_domain_dictionary.items():
                        if vnf.name.lower() == infra_cap_vnf_name.lower():
                                if infra_cap_domain_list is not None:
                                    foundSameDomainName = False
                                    firstDomainFeasibleFlag = True
                                    for domain_name_from_infra_cap_list in infra_cap_domain_list:
                                        if firstDomainFeasibleFlag is True:
                                            first_domain = domain_name_from_infra_cap_list  # primo dominio analizzato e primo endpoint analizzato
                                            firstDomainFeasibleFlag = False
                                        for endpoint in nffg.end_points:
                                            if domain_name_from_infra_cap_list.lower() == endpoint.domain.lower():
                                                vnf.domain = endpoint.domain.lower()  # Taggo il vnf domain con lo stesso domain degli endpoint
                                                foundSameDomainName = True
                                                logging.debug('Ok! Infrastructural Capability. Found a feasible domain=endpoint domain: %s',
                                                              vnf.domain)
                                                break

                                        if foundSameDomainName is True:  # domain coincidente trovato esco dal ciclo
                                            break

                                    for domain_name_from_infra_cap_list in infra_cap_domain_list:
                                        if domain_name_from_infra_cap_list is not None:
                                            if foundSameDomainName is False:
                                                vnf.domain = first_domain  # se non trovo nessun endpoint domain che coincide taggo la vnf col primo feasible domain analizzato
                                                logging.debug(
                                                    'No matching endpoint domain found. Tagging the VNF with the first feasible domain in the list: %s',
                                                    vnf.domain)
                                #logging.debug('vnf domain della IC con cui sto taggando: %s', vnf.domain)
                                break
                    #se non esiste nessun elemento neanche nel dizionario delle IC il vnf domain viene taggato col default domain




    def checkVNFAvailabilityOnTheSelectedDomain(self, domain_nffg_dict, infra_cap_domain_dictionary):
        # Checks if all vnf are available and ready to use on the selected domain as FC

        for domain, nffg in domain_nffg_dict.items():
            # logging.debug('Passato di qui1: domain id = %s', domain.id )
            domain_info = DomainInformation().get_domain_info()[domain.id]
            logging.debug(domain_info.get_dict())
            for vnf in nffg.vnfs:
                # logging.debug('Passato di qui2: vnf name = %s', vnf.name)
                found = False
                for function_capability in domain_info.capabilities.functional_capabilities:
                    if vnf.name.lower() == function_capability.type.lower():  # convert both of them to lower case for case insensitive comparison
                        logging.debug("Ok! Found the vnf searched in the domain specified in the nffg")
                        if function_capability.ready is True:
                            logging.debug("Ok! The functional capability is ready!")
                            found = True
                            break
                        else:
                            logging.debug("Error! The functional capability is already in use!")
                            raise FunctionalCapabilityAlreadyInUse(
                                "Error! NFFG can't be deployed. The functional capability is already in use!")
                if found is False: #non ho trovato nemeno una function capability, allora controllo se esistono IC per quel dominio
                    for infra_cap_vnf_name, infra_cap_domain_list in infra_cap_domain_dictionary.items():
                        if infra_cap_domain_list == []: #se non ho nessuna IC nel dizionario dei domini feasible
                                raise NoCapabilityFound(
                                    "Error! NFFG can't be deployed. No functional capability and no infrastructural capability found in the domain specified in the nffg.")
                    for infrastructural_capability in domain_info.capabilities.infrastructural_capabilities:
                        if infrastructural_capability is not None:
                            logging.debug("Ok! An IC exists for the vnf searched in the domain specified in the nffg")
                            break
                        else:
                            raise NoCapabilityFound(
                                "Error! NFFG can't be deployed. No functional capability and no infrastructural capability found in the domain specified in the nffg.")

