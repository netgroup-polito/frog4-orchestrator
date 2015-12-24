'''
Created on 01 dic 2015

@author: stefanopetrangeli
'''
class DomainInfo(object):
    def __init__(self, name = None, interfaces=None, node_id= None):
        self.name = name
        self.interfaces = interfaces or []
        self.node_id = node_id
                 
    def parseDict(self, domaininfo_dict):
        self.name = domaininfo_dict['netgroup-domain:informations']['name']
        #if 'netgroup-network-manager:informations' in domaininfo_dict['netgroup-domain:informations']:
        if 'openconfig-interfaces:interfaces' in domaininfo_dict['netgroup-domain:informations']['netgroup-network-manager:informations']:
            for interface_dict in domaininfo_dict['netgroup-domain:informations']['netgroup-network-manager:informations']['openconfig-interfaces:interfaces']['openconfig-interfaces:interface']:
                interface = Interface()
                interface.parseDict(interface_dict)
                self.interfaces.append(interface)
    """
    def getDict(self):
        template_dict = {}
        if self.name is not None:
            template_dict['name'] = self.name
        if self.vnf_type is not None:            
            template_dict['vnf-type'] = self.vnf_type
        if self.uri is not None:
            template_dict['uri'] = self.uri
        if self.memory_size is not None:    
            template_dict['memory-size'] = self.memory_size
        if self.root_file_system_size is not None:
            template_dict['root-file-system-size'] = self.root_file_system_size
        if self.ephemeral_file_system_size is not None:
            template_dict['ephemeral-file-system-size'] = self.ephemeral_file_system_size
        if self.swap_disk_size is not None:
            template_dict['swap-disk-size'] = self.swap_disk_size
        if self.expandable is not None:
            template_dict['expandable'] = self.expandable
        template_dict['CPUrequirements'] = self.cpu_requirements.getDict()
        ports_dict = []
        for port in self.ports:
            ports_dict.append(port.getDict())
        if ports_dict:
            template_dict['ports'] = ports_dict
        return template_dict
    """
    
    def addInterface(self, interface):
        if type(interface) is Interface:
            self.interfaces.append(interface)
        else:
            raise TypeError("Tried to add an interface with a wrong type. Expected Interface, found "+type(interface))
        
    def getInterface(self, interface_name):
        for interface in self.interfaces:
            if interface.name == interface_name:
                return interface
        
class Interface(object):
    # Subinterfaces are ignored
    def __init__(self, name=None, _type=None, neighbor_domain=None, neighbor_interface=None, gre=False, gre_tunnels=None, vlan=False, vlans_used=None):
        self.name = name
        self.type = _type
        self.gre = gre
        self.gre_tunnels = gre_tunnels or []
        self.vlan = vlan   
        self.vlans_used = vlans_used or [] 
        self.neighbor_domain = neighbor_domain
        self.neighbor_interface = neighbor_interface
        
    def parseDict(self, interface_dict):
        self.name = interface_dict['name']
        if 'type' in interface_dict['config']:
            self.type = interface_dict['config']['type']
               
        for subinterface_dict in interface_dict['openconfig-interfaces:subinterfaces']['openconfig-interfaces:subinterface']:
            if subinterface_dict['config']['name'] == self.name:
                if subinterface_dict['capabilities']['gre'] == True:
                    self.gre = True
                    if 'netgroup-if-gre:gre' in subinterface_dict:
                        for gre_dict in subinterface_dict['netgroup-if-gre:gre']:
                            gre_tunnel = GreTunnel()
                            gre_tunnel.parseDict(gre_dict)
                            self.gre_tunnels.append(gre_tunnel)
                    
                    
        if 'netgroup-neighbor:neighbor' in interface_dict['openconfig-if-ethernet:ethernet']:
            self.neighbor_domain = interface_dict['openconfig-if-ethernet:ethernet']['netgroup-neighbor:neighbor']['domain']
            if 'interface' in interface_dict['openconfig-if-ethernet:ethernet']['netgroup-neighbor:neighbor']:
                self.neighbor_interface = interface_dict['openconfig-if-ethernet:ethernet']['netgroup-neighbor:neighbor']['interface']

        if 'openconfig-vlan:vlan' in interface_dict['openconfig-if-ethernet:ethernet']:
            self.vlan = True
            if 'openconfig-vlan:config' in interface_dict['openconfig-if-ethernet:ethernet']['openconfig-vlan:vlan']:
                vlan_config = interface_dict['openconfig-if-ethernet:ethernet']['openconfig-vlan:vlan']['openconfig-vlan:config']
                if vlan_config['interface-mode']=="TRUNK":
                    for vlan in vlan_config['trunk-vlans']:
                        self.vlans_used.append(vlan)
                    

    def addGreTunnel(self, gre_tunnel):
        if type(gre_tunnel) is GreTunnel:
            self.gre_tunnels.append(gre_tunnel)
        else:
            raise TypeError("Tried to add a gre tunnel with a wrong type. Expected GreTunnel, found "+type(gre_tunnel))
        
    def addVlan(self, vlan):
        self.vlans_used.append(vlan)
    
class GreTunnel(object):
    def __init__(self, name=None, local_ip=None, remote_ip=None, gre_key=None):
        self.name = name
        self.local_ip = local_ip
        self.remote_ip = remote_ip
        self.gre_key = gre_key
        
    def parseDict(self, gre_dict):
        self.name = gre_dict['config']['name']
        if 'local_ip' in gre_dict['options']:
            self.local_ip = gre_dict['options']['local_ip']
        if 'remote_ip' in gre_dict['options']:
            self.remote_ip = gre_dict['options']['remote_ip']
        if 'key' in gre_dict['options']:
            self.gre_key = gre_dict['options']['key']
                