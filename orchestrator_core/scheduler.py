'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from orchestrator_core.exception import NodeNotFound
from orchestrator_core.sql.node import Node
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.domains_info import DomainsInformation
import itertools, random
import logging

class Scheduler(object):
    def __init__(self):
        pass
    
    def schedule(self, nffg):
        node_list = []
        nffg_list = []      
        node = Node().getNodeFromDomainID(self.checkEndpointLocation(nffg))
        node_list.append(node)
        nffg_list.append(nffg)
        
        # check if the nffg can be split (for the moment with a very stupid criterion)
        left = []
        right = []
        splittable = False
        for endpoint in nffg.end_points:
            if endpoint.type == 'interface' and endpoint.name == "user":
                splittable = True
                left.append(endpoint)
                right = nffg.end_points + nffg.vnfs
                right.remove(endpoint)
                break
        # Try to split and match capabilities
        if splittable is True:
            domains_info = DomainsInformation().get_domain_info()
            if not domains_info:
                logging.debug("Domains information are not present, so it's not possible to split the graph")
                return node_list, nffg_list
            if node.id not in domains_info:
                logging.debug("Domain information related to the user endpoint node are not available, so it's not possible to split the graph")
                return node_list, nffg_list
            nffg1, nffg2 = nffg.split(left, right)

            gen_endpoints = nffg1.getAutogeneratedEndpoints()

            characterization = self.matchCapabilites(domains_info, len(gen_endpoints), node.id)
            
            if characterization:
                logging.debug("Graph can be split!")
                self.characterizeEndpoints(nffg1, nffg2, gen_endpoints, characterization)
                nffg_list.clear()
                nffg_list.append(nffg1)   
                nffg_list.append(nffg2)  
                # provisional
                node_list.append(Node().getNodeFromDomainID(self.checkEndpointLocation(nffg2)))
            else:
                logging.debug("Graph cannot be split because domains capabilities are not suitable for this graph")
            
        return node_list, nffg_list
    
    def characterizeEndpoints(self, nffg1, nffg2, gen_endpoints, characterization):
        #nffg1 will be instantiated in the domain that contains the user_endpoint
        i=0
        for element in characterization:
            if type(element) is DirectLink:
                nffg_1_endp = nffg1.getEndPoint(gen_endpoints[i].id)
                nffg_2_endp = nffg2.getEndPoint(gen_endpoints[i].id)
                
                nffg_1_endp.type = "interface"
                nffg_1_endp.node_id = Node().getNode(element.domain_1).domain_id
                nffg_1_endp.interface = element.port_1
                nffg_2_endp.type = "interface"
                nffg_2_endp.node_id = Node().getNode(element.domain_2).domain_id
                nffg_2_endp.interface = element.port_2
            elif type(element) is Vlan:
                nffg_1_endp = nffg1.getEndPoint(gen_endpoints[i].id)
                nffg_2_endp = nffg2.getEndPoint(gen_endpoints[i].id)
                
                nffg_1_endp.type = "vlan"
                nffg_1_endp.node_id = Node().getNode(element.domain_1).domain_id
                nffg_1_endp.interface = element.port_1
                nffg_1_endp.vlan_id = str(element.vlan)
                nffg_2_endp.type = "vlan"
                nffg_2_endp.node_id = Node().getNode(element.domain_2).domain_id
                nffg_2_endp.interface = element.port_2         
                nffg_2_endp.vlan_id = str(element.vlan)
            elif type(element) is Gre:
                nffg_1_endp = nffg1.getEndPoint(gen_endpoints[i].id)
                nffg_2_endp = nffg2.getEndPoint(gen_endpoints[i].id)
                ip_1 = Node().getNode(element.domain_1).domain_id
                ip_2 = Node().getNode(element.domain_2).domain_id
                
                nffg_1_endp.type = "gre-tunnel"
                nffg_1_endp.local_ip = ip_1
                nffg_1_endp.remote_ip = ip_2
                nffg_1_endp.interface = element.port_1
                nffg_1_endp.gre_key = element.gre_key
                nffg_2_endp.type = "gre-tunnel"
                nffg_2_endp.local_ip = ip_2
                nffg_2_endp.remote_ip = ip_1                
                nffg_2_endp.interface = element.port_2         
                nffg_2_endp.gre_key = element.gre_key     
            else:
                raise TypeError("Only DirectLink, Vlan and Gre characterizations are supported")
            i=i+1
        #print(nffg1.getJSON())
        #print(nffg2.getJSON())         
        
    def matchCapabilites(self, domains_info, number_of_links, user_endpoint_node_id):
        characterizations_score = []
        characterizations_list = []
        for domain_relationship in itertools.permutations(domains_info, 2):
            #print(domain_relationship)
            if domain_relationship[0] == user_endpoint_node_id :
                print(domain_relationship)
                characterization = self.searchMatchesBetweenDomains(domains_info, domain_relationship[0], domain_relationship[1], number_of_links)
                if characterization:
                    characterizations_list.append(characterization)
                    characterizations_score.append(self.calculateScore(characterization))
        if len(characterizations_list) == 0:
            return None
        return characterizations_list[characterizations_score.index(max(characterizations_score))]
                
    def searchMatchesBetweenDomains(self, domains_info, node_id_1, node_id_2, number_of_links):
        matches_found = 0
        characterization = []
        domain_1 = domains_info[node_id_1]
        for interface in domain_1.interfaces: 
            vlan_match = False
            if interface.neighbor_domain is not None and interface.neighbor_domain != "internet":
                #Search for direct connections
                try:
                    remote_node = Node().getNodeFromName(interface.neighbor_domain)
                except NodeNotFound:
                    #Remote_node not found, continue
                    continue                        
                remote_interface_name = interface.neighbor_interface
                if remote_node.id == node_id_2 and remote_node.id in domains_info:
                    remote_interface = domains_info[remote_node.id].getInterface(remote_interface_name)
                    if remote_interface is not None and remote_interface.neighbor_domain == Node().getNode(node_id_1).name and remote_interface.neighbor_interface == interface.name:
                        #Connection found between these two domains
                        if interface.vlan is True and remote_interface.vlan is True:
                            vlan_id = self.findFreeVlanId(interface.vlans_used, remote_interface.vlans_used)
                            if vlan_id is not None:
                                print ("vlan match found")
                                vlan_match = True
                                matches_found = matches_found + 1
                                characterization.append(Vlan(node_id_1, interface.name, node_id_2, remote_interface_name, vlan_id))
                        if vlan_match is False:
                            print ("direct link match found")
                            matches_found = matches_found + 1
                            characterization.append(DirectLink(node_id_1, interface.name, node_id_2, remote_interface_name))
                        if matches_found == number_of_links:
                            break

        if matches_found < number_of_links:
            #Search for internet connections
            for interface in domain_1.interfaces: 
                if interface.neighbor_domain is not None and interface.neighbor_domain == "internet" and interface.gre is True:
                    if self.checkActiveTunnels(interface, node_id_2) is True:
                        domain_2 = domains_info[node_id_2]
                        for remote_interface in domain_2.interfaces:
                            if remote_interface.neighbor_domain is not None and remote_interface.neighbor_domain == "internet" and remote_interface.gre is True:
                                if self.checkActiveTunnels(remote_interface, node_id_1) is True:
                                    free_interface = self.checkTunnelEndpoint(node_id_2, remote_interface, characterization)
                                    if free_interface is True:
                                        #Gre_tunnel endpoints found
                                        print ("gre match found")
                                        matches_found = matches_found + 1
                                        characterization.append(Gre(node_id_1, interface.name, node_id_2, remote_interface.name))
                                        break
                            if matches_found == number_of_links:
                                break
                    
        if matches_found == number_of_links:
            print ("Characterization found")
            return characterization
        else:
            return None       
                            
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg
        '''
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
        return node
    
    def findFreeVlanId(self, vlans_used_1, vlans_used_2):
        vlan_id = 2
        while (vlan_id < 4095):
            if vlan_id not in vlans_used_1 and vlan_id not in vlans_used_2:
                return vlan_id
            vlan_id = vlan_id + 1
            
    def calculateScore(self, characterization):
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
    
    def checkActiveTunnels(self, interface, remote_domain_id):
        '''
        Returns True if this interface is not already connected to the remote domain
        '''
        for gre_tunnel in interface.gre_tunnels:
            if gre_tunnel.remote_ip == Node().getNode(remote_domain_id).domain_id:
                return False
        return True
    
    def checkTunnelEndpoint(self, domain_id, interface, characterization):
        '''
        Returns False if this interface is already in a Gre characterization
        '''
        for element in characterization:
            if type(element) is Gre and element.domain_2 == domain_id and element.port_2 == interface.name:
                return False
        return True

class DirectLink(object):
    def __init__(self, domain_1=None, port_1=None, domain_2=None, port_2=None):
        self.domain_1 = domain_1
        self.port_1 = port_1
        self.domain_2 = domain_2
        self.port_2 = port_2
           
class Vlan(object):
    def __init__(self, domain_1=None, port_1=None, domain_2=None, port_2=None, vlan=None):
        self.domain_1 = domain_1
        self.port_1 = port_1
        self.domain_2 = domain_2
        self.port_2 = port_2 
        self.vlan = vlan
        
class Gre(object):
    def __init__(self, domain_1=None, port_1=None, domain_2=None, port_2=None, gre_key=None):
        self.domain_1 = domain_1
        self.port_1 = port_1
        self.domain_2 = domain_2
        self.port_2 = port_2 
        if gre_key is not None:
            self.gre_key = gre_key
        else:
            self.gre_key = '%032x' % random.getrandbits(128)
