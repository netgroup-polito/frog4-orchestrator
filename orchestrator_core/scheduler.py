"""
Created on Feb 16, 2017

@author: gabrielecastellano
"""

from nffg_library.nffg import NF_FG
from domain_information_library.domain_info import DomainInfo
from orchestrator_core.virtual_topology import VirtualTopology


class Scheduler:

    def __init__(self, virtual_topology):
        """

        :param virtual_topology:
        :type virtual_topology: VirtualTopology
        """
        self._virtual_topology = virtual_topology

    def schedule(self, nffg, feasible_domains):
        """
        Performs the scheduling algorithm and labels nffg elements with the scheduled domain
        :param nffg:
        :param feasible_domains:
        :type nffg: NF_FG
        :type feasible_domains: dict[str, DomainInfo]
        :return:
        """
        # TODO implement
        pass
