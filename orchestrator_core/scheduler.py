'''
Created on Oct 1, 2014

@author: fabiomignini
@author: stefanopetrangeli
'''
from orchestrator_core.config import Configuration
from orchestrator_core.exception import DomainNotFound, GraphError
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.domain import Domain
from orchestrator_core.sql.domains_info import DomainInformation
import itertools, random
import logging
from collections import OrderedDict
from nffg_library.nffg import NF_FG
from orchestrator_core.nffg_manager import NFFG_Manager

DEFAULT_DOMAIN = Configuration().DEFAULT_DOMAIN

class Scheduler(object):
    def __init__(self, flow_prefix = None):
        self.flow_prefix = flow_prefix
    
    def schedule(self, nffg):
        domain_list = []
        nffg_list = [] 
        additional_subgraphs = []
        # Mapping between domain_names and elements belonging to each domain
        domains_dict = self.checkElementsAnnotations(nffg)
        domain_names = list(domains_dict.keys())
        if len(domains_dict) == 1:
            # All elements are tagged with the same domain.
            domain = Domain().getDomainFromName(domain_names[0])
            domain_list.append(domain)
            nffg_list.append(nffg)
            return domain_list, nffg_list
        else:
            domains_info = DomainInformation().get_domain_info()
            if not domains_info:
                raise GraphError("Domains information are not present, so it's not possible to split and deploy the graph according to the domain tags you provided")
            for domain_name in domain_names:
                if Domain().getDomainFromName(domain_name).id not in domains_info:
                    raise GraphError("Domain " + domain_name + " that you specified in the NF-FG has not sent domains information, so it's not possible to split and deploy the graph")
            # Dict that maps each domain to the related subgraph
            domain_to_nffg = OrderedDict()
            for domain_name, domain_elements in domains_dict.items():
                other_elements = list(domains_dict.values())
                other_elements_list = []
                for element in other_elements:
                    if element != domain_elements:
                        other_elements_list = other_elements_list + element
                domain_to_nffg[domain_name] = nffg.split(domain_elements, other_elements_list, flow_prefix = self.flow_prefix)

            # Search matches between each possible couple of domains
            for domain_relationship in itertools.combinations(domain_to_nffg.keys(), 2):
                #print (domain_relationship)
                domain_1_nffg = domain_to_nffg[domain_relationship[0]]
                domain_2_nffg = domain_to_nffg[domain_relationship[1]]
                # Gets endpoints of domain_1 that have to be connected to domain_2
                gen_endpoints_1 = domain_1_nffg.getAutogeneratedEndpoints(domain_relationship[1])
                if gen_endpoints_1:
                    result = self.searchMatchesBetweenDomains(domains_info, Domain().getDomainFromName(domain_relationship[0]).id, Domain().getDomainFromName(domain_relationship[1]).id, len(gen_endpoints_1))
                    if result is not None:
                        characterization = result[0]
                        middle_nffg = result[1]
                        gen_endpoints_2 = domain_1_nffg.getRemoteGeneratedEndpoints(domain_relationship[1], domain_2_nffg)
                        self.characterizeEndpoints(domain_1_nffg, domain_2_nffg, gen_endpoints_1, gen_endpoints_2, characterization, nffg3=middle_nffg)
                        if middle_nffg is not None:
                            additional_subgraphs.append(middle_nffg)
                    else:
                        raise GraphError("Graph cannot be split because domains capabilities are not suitable for this graph. Involved domains: "+ domain_relationship[0] + " and " + domain_relationship[1])

            for domain, nffg in domain_to_nffg.items():
                domain_list.append(Domain().getDomainFromName(domain))
                nffg_list.append(nffg)
            for additional_nffg in additional_subgraphs:
                domain_list.append(Domain().getDomainFromName(additional_nffg.domain))
                nffg_list.append(additional_nffg)

            logging.debug("Graph can be split!")

            return domain_list, nffg_list
    
    def characterizeEndpoints(self, nffg1, nffg2, gen_endpoints_1, gen_endpoints_2, characterization, nffg3=None):
        i=0
        for element in characterization:
            if type(element) is DirectLink:
                nffg_1_endp = nffg1.getEndPoint(gen_endpoints_1[i].id)
                nffg_2_endp = nffg2.getEndPoint(gen_endpoints_2[i].id)
                
                nffg_1_endp.type = "interface"
                nffg_1_endp.node_id = element.node_1
                nffg_1_endp.interface = element.port_1
                nffg_2_endp.type = "interface"
                nffg_2_endp.node_id = element.node_2
                nffg_2_endp.interface = element.port_2
                i = i+1
            elif type(element) is Vlan:
                if element.partial == 1:
                    nffg_1_endp = nffg1.getEndPoint(gen_endpoints_1[i].id)
                    nffg_3_endp = nffg3.getEndPoint(str(i)+"_1")

                    nffg_1_endp.type = "vlan"
                    nffg_1_endp.node_id = element.node_1
                    nffg_1_endp.interface = element.port_1
                    nffg_1_endp.vlan_id = str(element.vlan)
                    nffg_3_endp.name = nffg_1_endp.id
                    nffg_3_endp.type = "vlan"
                    nffg_3_endp.node_id = element.node_2
                    nffg_3_endp.interface = element.port_2         
                    nffg_3_endp.vlan_id = str(element.vlan)
                elif element.partial == 2:
                    nffg_2_endp = nffg2.getEndPoint(gen_endpoints_2[i].id)
                    nffg_3_endp = nffg3.getEndPoint(str(i)+"_2")
                    
                    nffg_3_endp.name = nffg_2_endp.id
                    nffg_3_endp.type = "vlan"
                    nffg_3_endp.node_id = element.node_1
                    nffg_3_endp.interface = element.port_1
                    nffg_3_endp.vlan_id = str(element.vlan)
                    nffg_2_endp.type = "vlan"
                    nffg_2_endp.node_id = element.node_2
                    nffg_2_endp.interface = element.port_2         
                    nffg_2_endp.vlan_id = str(element.vlan)  
                    i = i+1
                else:
                    nffg_1_endp = nffg1.getEndPoint(gen_endpoints_1[i].id)
                    nffg_2_endp = nffg2.getEndPoint(gen_endpoints_2[i].id)
                    
                    nffg_1_endp.type = "vlan"
                    nffg_1_endp.node_id = element.node_1
                    nffg_1_endp.interface = element.port_1
                    nffg_1_endp.vlan_id = str(element.vlan)
                    nffg_2_endp.type = "vlan"
                    nffg_2_endp.node_id = element.node_2
                    nffg_2_endp.interface = element.port_2         
                    nffg_2_endp.vlan_id = str(element.vlan)
                    i = i+1
            elif type(element) is Gre:
                nffg_1_endp = nffg1.getEndPoint(gen_endpoints_1[i].id)
                nffg_2_endp = nffg2.getEndPoint(gen_endpoints_2[i].id)
                ip_1 = element.local_ip
                ip_2 = element.remote_ip
                
                nffg_1_endp.type = "gre-tunnel"
                nffg_1_endp.local_ip = ip_1
                nffg_1_endp.remote_ip = ip_2
                #nffg_1_endp.interface = element.port_1
                nffg_1_endp.gre_key = element.gre_key
                nffg_2_endp.type = "gre-tunnel"
                nffg_2_endp.local_ip = ip_2
                nffg_2_endp.remote_ip = ip_1                
                #nffg_2_endp.interface = element.port_2
                nffg_2_endp.gre_key = element.gre_key     
                i = i+1
            else:
                raise TypeError("Only DirectLink, Vlan and Gre characterizations are supported") 
             
    """
    def matchCapabilites(self, domains_info, number_of_links, domain_id_1, domain_id_2):
        characterizations_score = []
        characterizations_list = []
        ordered_domains_info = OrderedDict()
        ordered_domains_info[user_endpoint_domain_id] = domains_info[user_endpoint_domain_id]
        del domains_info[user_endpoint_domain_id]
        for k, v in domains_info.items():
            ordered_domains_info[k] = v
        
        for domain_relationship in itertools.combinations(ordered_domains_info, 2):
            #print(domain_relationship)
            if domain_relationship[0] == user_endpoint_domain_id:
                print(domain_relationship)
                characterization = self.searchMatchesBetweenDomains(ordered_domains_info, domain_relationship[0], domain_relationship[1], number_of_links)
                if characterization is not None:
                    characterizations_list.append(characterization)
                    characterizations_score.append(self.calculateScore(characterization))
        if len(characterizations_list) == 0:
            return None
        return characterizations_list[characterizations_score.index(max(characterizations_score))]
    """
                
    def searchMatchesBetweenDomains(self, domains_info, domain_id_1, domain_id_2, number_of_links):
        matches_found = 0
        characterization = []
        middle_nffg = None
        domain_1 = domains_info[domain_id_1]
        # Directly linked domains
        #Vlan
        for interface in domain_1.interfaces: 
            for neighbor in interface.neighbors:
                if neighbor.domain_name != "internet" and neighbor.remote_interface is not None:
                    #Search for direct connections
                    try:
                        remote_domain = Domain().getDomainFromName(neighbor.domain_name)
                    except DomainNotFound:
                        #Remote_domain not found, continue
                        continue     
                    remote_node = neighbor.node
                    remote_interface_name = neighbor.remote_interface
                    if remote_domain.id == domain_id_2 and remote_domain.id in domains_info:
                        remote_interface = domains_info[remote_domain.id].getInterface(remote_node, remote_interface_name)
                        if remote_interface is not None and self.isNeighbor(remote_interface, Domain().getDomain(domain_id_1).name, interface) is True:
                            if interface.vlan is True and remote_interface.vlan is True:
                                while matches_found < number_of_links:
                                    vlan_id = self.findFreeVlanId(interface.vlans_free, remote_interface.vlans_free)
                                    if vlan_id is not None:
                                        print ("vlan match found")
                                        matches_found = matches_found + 1
                                        characterization.append(Vlan(interface.node, interface.name, domain_1.type, remote_node, remote_interface_name, remote_domain.type, vlan_id))
                                    else:
                                        logging.debug("vlan id free not found")
                                        break
                                if matches_found == number_of_links:
                                    break
            if matches_found == number_of_links:
                break
        #Direct links
        if matches_found < number_of_links:
            for interface in domain_1.interfaces:
                for neighbor in interface.neighbors:
                    if neighbor.domain_name != "internet" and neighbor.remote_interface is not None:
                        #Search for direct connections
                        try:
                            remote_domain = Domain().getDomainFromName(neighbor.domain_name)
                        except DomainNotFound:
                            #Remote_domain not found, continue
                            continue
                        remote_node = neighbor.node
                        remote_interface_name = neighbor.remote_interface
                        if remote_domain.id == domain_id_2 and remote_domain.id in domains_info:
                            remote_interface = domains_info[remote_domain.id].getInterface(remote_node, remote_interface_name)
                            if remote_interface is not None and self.isNeighbor(remote_interface, Domain().getDomain(domain_id_1).name, interface) is True:
                                print ("direct link match found")
                                matches_found = matches_found + 1
                                characterization.append(DirectLink(interface.node, interface.name, domain_1.type, remote_node, remote_interface_name, remote_domain.type))
                                if matches_found == number_of_links:
                                    break
                if matches_found == number_of_links:
                    break
        # Domains not directly linked
        if matches_found < number_of_links:
            for interface in domain_1.interfaces:
                result = self.searchConnectionThroughADomain(domains_info, interface, domain_id_1, domain_id_2)
                if result is not None:
                    middle_domain = result[0]
                    middle_interface_1 = result[1]
                    middle_interface_2 = result[2]
                    remote_interface = result[3]
                    # TODO: Direct links support?
                    if interface.vlan is True and middle_interface_1.vlan is True and middle_interface_2.vlan is True and remote_interface.vlan is True:
                        middle_nffg = NF_FG()
                        middle_nffg.name = "Passthrough"
                        middle_nffg.domain = middle_domain.name
                        nffg_manager = NFFG_Manager(middle_nffg)
                        while matches_found < number_of_links:
                            vlan_id_1 = self.findFreeVlanId(interface.vlans_free, middle_interface_1.vlans_free)
                            vlan_id_2 = self.findFreeVlanId(middle_interface_2.vlans_free, remote_interface.vlans_free)
                            if vlan_id_1 is not None and vlan_id_2 is not None:
                                print ("vlan match through an external domain found")
                                nffg_manager.addEndpointsCoupleAndFlowrules(matches_found)
                                matches_found = matches_found + 1
                                characterization.append(Vlan(interface.node, interface.name, domain_1.type, middle_interface_1.node, middle_interface_1.name, middle_domain.type, vlan_id_1, partial=1))
                                characterization.append(Vlan(middle_interface_2.node, middle_interface_2.name, middle_domain.type, remote_interface.node, remote_interface.name, Domain().getDomain(domain_id_2).type, vlan_id_2, partial=2))
                            else:
                                logging.debug("vlan id free not found")
                                break
                        if matches_found == number_of_links:
                            break
        # Domains connected through an IP domain
        #GRE
        if matches_found < number_of_links:
            #Search for internet connections
            for interface in domain_1.interfaces:
                if self.isConnectedToIPDomain(interface) is True and interface.gre is True:
                    #if self.checkActiveTunnels(interface, node_id_2) is True:
                    domain_2 = domains_info[domain_id_2]
                    for remote_interface in domain_2.interfaces:
                        if self.isConnectedToIPDomain(remote_interface) is True and remote_interface.gre is True:
                            #Gre_tunnel endpoints found
                            # If local and/or remote interfaces are Openstack compute nodes we need to set the local/remote GRE IP addresses accordingly
                            if interface.node is not None:
                                local_ip = interface.node
                            else:
                                local_ip = Domain().getDomainIP(domain_id_1)
                            if remote_interface.node is not None:
                                remote_ip = remote_interface.node
                            else:
                                remote_ip = Domain().getDomainIP(domain_id_2)
                            while matches_found < number_of_links:
                                print ("gre match found")
                                matches_found = matches_found + 1
                                characterization.append(Gre(local_ip, remote_ip))
                            break
                if matches_found == number_of_links:
                    break

        if matches_found == number_of_links:
            print ("Characterization found")
            return characterization, middle_nffg
        else:
            return None
    """
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg
        '''
        # TODO: scan until a valid node is found
        domain_info = DomainInformation()
        node = None
        for end_point in nffg.end_points:
            if end_point.node_id is not None:
                node = end_point.node_id
                break
            elif end_point.switch_id is not None:
                node = end_point.switch_id
                break
            elif end_point.local_ip is not None:
                node = end_point.local_ip
                break
        if node is None:
            raise NodeNotFound("Unable to determine where to place this graph (endpoint.node_id or endpoint.switch_id or endpoint.local_ip missing)")
        return domain_info.getDomainIDfromNode(node)
    """

    def checkElementsAnnotations(self, nffg):
        domains_dict = OrderedDict()
        endp_and_vnf = nffg.end_points + nffg.vnfs
        for element in endp_and_vnf:
            if element.domain is None:
                if nffg.domain is not None:
                    element.domain = nffg.domain
                elif DEFAULT_DOMAIN is not None:
                    element.domain = DEFAULT_DOMAIN
                else:
                    raise GraphError ("Unable to deploy the graph: neither graph nor its elements are associated to a domain and DEFAULT_DOMAIN is not specified in the configuration file")
            if element.domain not in domains_dict:
                domains_dict[element.domain] = []
            domains_dict[element.domain].append(element)
        return domains_dict

    def findFreeVlanId(self, vlans_free_1, vlans_free_2):
        for vlan_id in vlans_free_1:
            if vlan_id in vlans_free_2:
                vlans_free_1.remove(vlan_id)
                vlans_free_2.remove(vlan_id)
                return vlan_id
    """
    def calculateScore(self, characterization):
        #TODO: different score if multiple characterizations over the same interface?
        vlan_value = 3
        directlink_value = 2
        gre_value = 1

        score=0
        for element in characterization:
            if type(element) is DirectLink:
                score = score + directlink_value
            elif type(element) is Vlan:
                score = score + vlan_value
            elif type(element) is Gre:
                score = score + gre_value
        return score
    """

    def isNeighbor(self, interface_1, domain_name_2, interface_2):
        '''
        Determines whether among the neighbors of interface_1 there is interface_2 of domain_name_2
        '''
        for neighbor in interface_1.neighbors:
            if neighbor.domain_name == domain_name_2 and neighbor.node == interface_2.node and neighbor.remote_interface == interface_2.name:
                return True
        return False

    def isConnectedToIPDomain(self, interface):
        '''
        Determines whether interface is connected to an IP domain
        '''
        for neighbor in interface.neighbors:
            if neighbor.neighbor_type == "IP":
                return True
        return False

    def searchConnectionThroughADomain(self, domains_info, interface, domain_id_1, domain_id_2):
        '''
        Searches if there are domains that connect domain_id_1 and domain_id_2.
        If the connection is found returns the domain in the middle, middle_interface_1 that is the interface connected to domain_id_1, middle_interface_2 that is the interface connected to domain_id_2 and remote_interface of the domain_id_2
        '''
        for neighbor_1 in interface.neighbors:
            if neighbor_1.domain_name != "internet" and neighbor_1.remote_interface is not None:
                try:
                    middle_domain = Domain().getDomainFromName(neighbor_1.domain_name)
                except DomainNotFound:
                    continue
                middle_node = neighbor_1.node
                midle_interface_name = neighbor_1.remote_interface
                if middle_domain.id in domains_info:
                    middle_domain_info = domains_info[middle_domain.id]
                    middle_interface_1 = middle_domain_info.getInterface(middle_node, midle_interface_name)
                    if middle_interface_1 is None or self.isNeighbor(middle_interface_1, Domain().getDomain(domain_id_1).name, interface) is False:
                        continue
                    # First half found
                    for middle_interface_2 in middle_domain_info.interfaces:
                        for neighbor_2 in middle_interface_2.neighbors:
                            if neighbor_2.domain_name != "internet" and neighbor_2.remote_interface is not None:
                                try:
                                    remote_domain = Domain().getDomainFromName(neighbor_2.domain_name)
                                except DomainNotFound:
                                    continue
                                if remote_domain.id == domain_id_2 and remote_domain.id in domains_info:
                                    remote_node = neighbor_2.node
                                    remote_interface_name = neighbor_2.remote_interface
                                    remote_interface = domains_info[remote_domain.id].getInterface(remote_node, remote_interface_name)
                                    if remote_interface is not None and self.isNeighbor(remote_interface, middle_domain.name, middle_interface_2) is True:
                                        # Second half found
                                        return (middle_domain, middle_interface_1, middle_interface_2, remote_interface)
                                    
    """
    def checkActiveTunnels(self, interface, remote_domain_id):
        '''
        Returns True if this interface is not already connected to the remote domain
        '''
        return True
        '''
        for gre_tunnel in interface.gre_tunnels:
            if gre_tunnel.remote_ip == Node().getNode(remote_domain_id).domain_id:
                return False
        return True
        '''
    
    def checkTunnelEndpoint(self, domain_id, interface, characterization):
        '''
        Returns False if this interface is already in a Gre characterization
        '''
        for element in characterization:
            if type(element) is Gre and element.domain_2 == domain_id and element.port_2 == interface.name:
                return False
        return True
    """
class DirectLink(object):
    def __init__(self, node_1=None, port_1=None, domain_1_type = None, node_2=None, port_2=None, domain_2_type=None):
        self.node_1 = node_1
        self.port_1 = port_1
        self.domain_1_type = domain_1_type
        self.node_2 = node_2
        self.port_2 = port_2
        self.domain_2_type = domain_2_type

           
class Vlan(object):
    def __init__(self, node_1=None, port_1=None, domain_1_type = None, node_2=None, port_2=None, domain_2_type=None, vlan=None, partial=0):
        '''
        Partial can be 0 if the characterization involves directly domain_1 and domain_2, 1 if it involves the domain_1 and a domain in the middle or 2 if it involves a domain in the middle and the domain_2
        '''
        self.node_1 = node_1
        self.port_1 = port_1
        self.domain_1_type = domain_1_type        
        self.node_2 = node_2
        self.port_2 = port_2 
        self.domain_2_type = domain_2_type        
        self.vlan = vlan
        self.partial = partial
        
class Gre(object):
    def __init__(self, local_ip=None, remote_ip=None, gre_key=None):
        self.local_ip = local_ip
        #self.local_port = port_1
        self.remote_ip = remote_ip
        #self.remote_port = port_2
        if gre_key is not None:
            self.gre_key = gre_key
        else:
            self.gre_key = '0x%08x' % random.getrandbits(32)
