"""
Created on Feb 16, 2017

@author: gabrielecastellano
"""

from domain_information_library.domain_info import DomainInfo
from orchestrator_core.exception import IncoherentDomainInformation


class VirtualTopology:

    def __init__(self, domains_info):
        """

        :param domains_info:
        :type domains_info: dict[int, DomainInfo]
        """
        self._topology_graph = {}
        for domain_id, domain_info in domains_info.items():
            self._topology_graph[domain_info.name] = []
            # discover available virtual channel for domain
            for interface in domain_info.hardware_info.interfaces:
                for neighbor in interface.neighbors:
                    # check if there is a virtual channel to this neighbor domain
                    if neighbor.neighbor_type == "domain":
                        # get domain information for this neighbor
                        neighbor_domain_info = None
                        for _id, di in domains_info.items():
                            if di.name == neighbor.domain_name:
                                neighbor_domain_info = di
                                break
                        if neighbor_domain_info is None:
                            raise IncoherentDomainInformation("Neighbor " + neighbor.domain_name + " not found for " +
                                                              "domain " + domain_info.name)
                        # search the interface of the neighbor
                        for neighbor_interface in neighbor_domain_info.hardware_info.interfaces:
                            if neighbor_interface.get_full_name() == neighbor.remote_interface:
                                virtual_channels = self._get_virtual_channels_between_interfaces(interface,
                                                                                                 neighbor_interface,
                                                                                                 neighbor.domain_name)
                                self._topology_graph[domain_info.name].extend(virtual_channels)
                                break

                    # check for virtual channel across legacy network
                    elif neighbor.neighbor_type == "legacy-network":
                        # get domains attached to this legacy network
                        for _id, far_domain_info in domains_info.items():
                            if far_domain_info.type == "domain" and far_domain_info.name != domain_info.name:
                                # check if this domain has the same legacy network
                                for far_interface in far_domain_info.hardware_info.interfaces:
                                    for far_domain_neighbor in far_interface.neighbors:
                                        if far_domain_neighbor.domain_name == neighbor.domain_name:
                                            virtual_channels = self._get_virtual_channels_between_interfaces(interface, far_interface, far_domain_info.name)
                                            self._topology_graph[domain_info.name].extend(virtual_channels)

    def _get_virtual_channels_between_interfaces(self, domain_a_interface, domain_b_interface, domain_b_name):
        """

        :param domain_a_interface:
        :param domain_b_interface:
        :param domain_b_name:
        :type domain_a_interface: domain_information_library.domain_info.Interface
        :type domain_b_interface: domain_information_library.domain_info.Interface
        :type domain_b_name: str
        :return:
        :rtype: list of dict
        """
        virtual_channels = []

        # get available labeling-methods for this interface
        a_labeling_methods = {}
        if domain_a_interface.gre:
            # TODO the data model does not have a list (or range) of available gre tunnel, suppose all keys are free
            a_labeling_methods["gre"] = [range(0, 2**32)]
        if domain_a_interface.vlan:
            a_labeling_methods["vlan"] = domain_a_interface.free_vlans

        b_labeling_methods = {}
        if domain_a_interface.gre:
            b_labeling_methods["gre"] = [range(0, 2**32)]
        if domain_a_interface.vlan:
            b_labeling_methods["vlan"] = domain_b_interface.free_vlans

        for a_labeling_method in a_labeling_methods.keys():
            # count virtual channel for this labeling method and add to graph
            if b_labeling_methods[a_labeling_method] is not None:
                virtual_channels = self._count_common_labels(a_labeling_methods[a_labeling_method],
                                                             b_labeling_methods[a_labeling_method])
                virtual_channels.append({
                    "peer": domain_b_name,
                    "labeling-method": a_labeling_method,
                    "virtual-channels": virtual_channels,
                    "interface": domain_a_interface.get_full_name()
                })
        return virtual_channels

    @staticmethod
    def _count_common_labels(domain_a_labels, domain_b_labels):
        common_labels = 0
        for l in domain_a_labels:
            if type(l) == range:
                for lb in domain_b_labels:
                    if type(lb) == range:
                        common_labels += len(range(max(l.start, lb.start), min(l.stop, lb.stop)+1))
                    else:
                        if l.start <= lb < l.stop:
                            common_labels += 1
            else:
                if l in domain_b_labels:
                    common_labels += 1
                else:
                    for lb in domain_b_labels:
                        if type(lb) == range:
                            if lb.start <= l < lb.stop:
                                common_labels += 1
                                break
        return common_labels

    def count_virtual_channels(self, domain_a, domain_b, labeling_method=None):
        """

        :param domain_a: domain a name
        :param domain_b: domain b name
        :param labeling_method: filter on a specific labeling method
        :type domain_a: str
        :type domain_b: str
        :type labeling_method: str
        :return: the number of virtual channels between domains
        :rtype int
        """
        count = 0
        if self._topology_graph[domain_a] is not None:
            for virtual_channel in self._topology_graph[domain_a]:
                if virtual_channel["peer"] == domain_b:
                    if labeling_method is None or virtual_channel["labeling-method"] == labeling_method:
                        count += virtual_channel["virtual-channels"]
        return count
