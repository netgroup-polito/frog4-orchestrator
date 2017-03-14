"""
Created on Feb 16, 2017

@author: gabrielecastellano
"""
import sys
import random
from collections import OrderedDict

from domain_information_library.domain_info import DomainInfo
from orchestrator_core.exception import IncoherentDomainInformation, PathNotFeasible


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
                            if far_domain_info.name != domain_info.name:
                                # check if this domain has the same legacy network
                                for far_interface in far_domain_info.hardware_info.interfaces:
                                    for far_domain_neighbor in far_interface.neighbors:
                                        if far_domain_neighbor.domain_name == neighbor.domain_name:
                                            virtual_channels = self._get_virtual_channels_between_interfaces(
                                                interface, far_interface, far_domain_info.name)
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
            # TODO the data model does not have a list (or range) of available gre tunnel, assume all keys are free
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
                virtual_channels_no = self._count_common_labels(a_labeling_methods[a_labeling_method],
                                                                b_labeling_methods[a_labeling_method])
                if virtual_channels_no > 0:
                    virtual_channels.append({
                        "peer": domain_b_name,
                        "labeling-method": a_labeling_method,
                        "labels": a_labeling_methods[a_labeling_method],
                        "count": virtual_channels_no,
                        "interface": domain_a_interface.get_full_name(),
                        "remote-interface": domain_b_interface.get_full_name()
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

    def pop_common_label(self, domain_a, domain_b, interface_a, interface_b, labeling_method):

        domain_a_labels = []
        for vc in self._topology_graph[domain_a]:
            if vc["peer"] == domain_b and vc["labeling-method"] == labeling_method\
                    and vc["interface"] == interface_a and vc["remote-interface"] == interface_b:
                domain_a_labels = vc["labels"]
        domain_b_labels = []
        for vc in self._topology_graph[domain_b]:
            if vc["peer"] == domain_a and vc["labeling-method"] == labeling_method\
                    and vc["interface"] == interface_b and vc["remote-interface"] == interface_a:
                domain_b_labels = vc["labels"]

        for l in self.shuffled(domain_a_labels):
            if type(l) == range:
                for lb in self.shuffled(domain_b_labels):
                    if type(lb) == range:
                        sub_start = max(l.start, lb.start)
                        sub_stop = min(l.stop, lb.stop)+1
                        if len(range(sub_start, sub_stop)) > 0:
                            label = random.randint(sub_start, sub_stop-1)
                            r1 = range(l.start, label)
                            r2 = range(label+1, l.stop)
                            domain_a_labels.remove(l)
                            if len(r1) > 1:
                                domain_a_labels.append(r1)
                            elif len(r1) == 1:
                                domain_a_labels.append(list(r1)[0])
                            if len(r2) > 1:
                                domain_a_labels.append(r2)
                            elif len(r2) == 1:
                                domain_a_labels.append(list(r2)[0])
                            r1 = range(lb.start, label)
                            r2 = range(label+1, lb.stop)
                            domain_b_labels.remove(lb)
                            if len(r1) > 1:
                                domain_b_labels.append(r1)
                            elif len(r1) == 1:
                                domain_b_labels.append(list(r1)[0])
                            if len(r2) > 1:
                                domain_b_labels.append(r2)
                            elif len(r2) == 1:
                                domain_b_labels.append(list(r2)[0])
                            return label
                    else:
                        if l.start <= lb < l.stop:
                            r1 = range(l.start, lb)
                            r2 = range(lb+1, l.stop)
                            domain_a_labels.remove(l)
                            domain_b_labels.remove(lb)
                            if len(r1) > 1:
                                domain_a_labels.append(r1)
                            elif len(r1) == 1:
                                domain_a_labels.append(list(r1)[0])
                            if len(r2) > 1:
                                domain_a_labels.append(r2)
                            elif len(r2) == 1:
                                domain_a_labels.append(list(r2)[0])
                            return lb
            else:
                if l in domain_b_labels:
                    domain_a_labels.remove(l)
                    domain_b_labels.remove(l)
                    return l
                else:
                    for lb in self.shuffled(domain_b_labels):
                        if type(lb) == range:
                            if lb.start <= l < lb.stop:
                                r1 = range(lb.start, l)
                                r2 = range(l+1, lb.stop)
                                domain_a_labels.remove(l)
                                domain_b_labels.remove(lb)
                                if len(r1) > 1:
                                    domain_b_labels.append(r1)
                                elif len(r1) == 1:
                                    domain_b_labels.append(list(r1)[0])
                                if len(r2) > 1:
                                    domain_b_labels.append(r2)
                                elif len(r2) == 1:
                                    domain_b_labels.append(list(r2)[0])
                                return l

    @staticmethod
    def shuffled(x):
        y = x[:]
        random.shuffle(y)
        return y

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
                        count += virtual_channel["count"]
        return count

    def find_shortest_path_between_domains(self, domain_a, domain_b):
        """

        :return:
        """
        a_tree = self._get_tree_to_domain(domain_a, domain_b, len(self._topology_graph))
        a_paths = self._get_path_list(a_tree, [])
        a_paths = [path for path in a_paths if path[-1] == domain_b]

        if len(a_paths) == 0:
            return None
        shortest_path = a_paths[0]
        for path in a_paths:
            if len(path) < shortest_path:
                shortest_path = path
        return shortest_path

    def find_path_between_domains_involving_fewest_additional_domains(self, domain_a, domain_b, domains):
        """

        :param domain_a:
        :param domain_b:
        :param domains: domains "free" to involve
        :return:
        """
        a_tree = self._get_tree_to_domain(domain_a, domain_b, len(self._topology_graph))
        a_paths = self._get_path_list(a_tree, [])
        a_paths = [path for path in a_paths if path[-1] == domain_b]

        if len(a_paths) == 0:
            return None
        best_path = a_paths[0]
        fewer_additional_domains = sys.maxsize
        for path in a_paths:
            additional_domains = [x for x in path if x not in domains]
            if len(additional_domains) < fewer_additional_domains:
                best_path = path
                fewer_additional_domains = len(additional_domains)
        return best_path

    def pop_virtual_channels_for_path(self, path):
        """
        Returns virtual channels to use for a given path, removing them from the topology
        :param path: the domains path
        :type path: list of str
        :return: a labeling method for each couple of domain of the path
        :rtype: dict[str, dict]
        """
        virtual_channels = OrderedDict()
        for i in range(len(path) - 1):
            for vc in self._topology_graph[path[i]]:
                if vc["peer"] == path[i+1] and vc["count"] > 0:
                    vc["count"] -= 1
                    virtual_channels[path[i]+'/'+path[i+1]] = {
                        "labeling-method": vc["labeling-method"],
                        "interface_a": vc["interface"],
                        "interface_b": vc["remote-interface"],
                    }
                    break
        if len(virtual_channels) != len(path) - 1:
            self.release_virtual_channels(virtual_channels)
            raise PathNotFeasible("Cannot find necessary virtual channels for path: " + str(path))
        return virtual_channels

    def release_virtual_channels(self, virtual_channels):
        """
        Re-add to the topology virtual channels passed as parameter
        :param virtual_channels: dict[str, dict]
        """
        for domains, labeling_method in virtual_channels.items():
            for vc in self._topology_graph[domains.split('/')[0]]:
                if vc["peer"] == domains.split('/')[1] and vc["labeling-method"] == labeling_method:
                    vc["count"] += 1

    def _get_tree_to_domain(self, root_domain, leaf_domain, deep):
        tree = {root_domain: {}}
        for virtual_channel in self._topology_graph[root_domain]:
            tree[root_domain][virtual_channel["peer"]] = {}
            if virtual_channel["peer"] != leaf_domain and deep > 0 and virtual_channel["count"] > 0:
                tree[root_domain][virtual_channel["peer"]] = self._get_tree_to_domain(virtual_channel["peer"],
                                                                                      leaf_domain, deep-1)
        return tree

    def _get_path_list(self, tree, prefix):
        paths = []
        for domain in tree:
            p = []
            p.extend(prefix)
            p.append(domain)
            if len(tree[domain]) > 0:
                paths.extend(self._get_path_list(tree[domain], p))
            else:
                prefix.append(domain)
                paths.append(prefix)
        return paths
