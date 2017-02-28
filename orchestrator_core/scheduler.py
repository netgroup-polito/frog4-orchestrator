"""
Created on Feb 16, 2017

@author: gabrielecastellano
"""

import copy

from collections import OrderedDict

import sys

from nffg_library.nffg import NF_FG
from orchestrator_core.exception import FeasibleSolutionNotFoundForNFFG, FeasibleDomainNotFoundForNFFGElement
from orchestrator_core.virtual_topology import VirtualTopology


class Scheduler:

    def __init__(self, virtual_topology, nf_feasible_domains, ep_feasible_domains):
        """

        :param virtual_topology:
        :param nf_feasible_domains:
        :param ep_feasible_domains:
        :type virtual_topology: VirtualTopology
        :type nf_feasible_domains: dict[str, list of str]
        :type ep_feasible_domains: dict[str, list of str]
        """
        self._virtual_topology = virtual_topology
        self._nf_feasible_domains = nf_feasible_domains
        self._ep_feasible_domains = ep_feasible_domains

    def schedule(self, nffg):
        """
        Performs the scheduling algorithm and labels nffg elements with the scheduled domain
        :param nffg:
        :type nffg: NF_FG
        :return:
        """
        # TODO should also provide information about virtual channel to use for each flow that is going to be split
        # check if each element of the nffg has at least a feasible domain
        self._check_nf_and_ep_feasibility()

        # solution is represented with a map {NF/EP : index} where each index represent the scheduled domain
        initial_solution = self._init_solution()

        # perform brute-force algorithm to find best solution
        optimal_solution, objective_function = self._brute_force(initial_solution)

        # check if retrieved solution is feasible
        if objective_function == sys.maxsize:
            raise FeasibleSolutionNotFoundForNFFG("There are no placements satisfying requested graph in the given " +
                                                  "topology")
        self._tag_nffg_with_scheduled_domains(nffg, optimal_solution)

    def _init_solution(self):
        initial_solution = OrderedDict()
        for k in self._nf_feasible_domains:
            initial_solution["nf:"+k] = 0
        for k in self._ep_feasible_domains:
            initial_solution["ep:"+k] = 0
        return initial_solution

    def _objective_function(self, solution):
        """
        This objective function returns the number of domains involved in the service
        :param solution:
        :type solution: OrderedDict
        :return: number of involved domains
        """
        involved_domains_set = set()
        for nf, domains in self._nf_feasible_domains.items():
            scheduled_domain = domains[solution["nf:"+nf]]
            involved_domains_set.add(scheduled_domain)
        for ep, domains in self._ep_feasible_domains.items():
            scheduled_domain = domains[solution["ep:"+ep]]
            involved_domains_set.add(scheduled_domain)
        # TODO check this just for directly connected domains, considering also required number of virtual channel
        involved_base_domains_set = copy.deepcopy(involved_domains_set)
        base_domain = involved_base_domains_set.pop()
        for domain in involved_base_domains_set:
            path = self._virtual_topology.\
                find_path_between_domains_involving_fewer_additional_domains(base_domain, domain, involved_domains_set)
            if path is None:
                return sys.maxsize
            involved_domains_set.update(path)
        return len(involved_domains_set)

    def _brute_force(self, initial_solution):
        """
        Try all the possible combination and returns the one that minimize the objective function
        :param initial_solution:
        :type initial_solution: OrderedDict
        :return: the optimal solution
        """
        current_solution = copy.deepcopy(initial_solution)
        best_solution = copy.deepcopy(current_solution)
        best_objective_function = self._objective_function(current_solution)
        nffg_element_iterator = len(current_solution.items())-1

        while True:
            # get next solution
            current_solution, nffg_element_iterator = self._perform_move(current_solution, nffg_element_iterator)
            # check if we tested all combinations
            if nffg_element_iterator == -1:
                break
            # check if returned solution is a new solution, if not then skip it
            if nffg_element_iterator != len(current_solution.items())-1:
                continue

            # check if current solution is better than the best so far
            current_objective_function = self._objective_function(current_solution)
            if current_objective_function < best_objective_function:
                best_solution = copy.deepcopy(current_solution)
                best_objective_function = current_objective_function

        return best_solution, best_objective_function

    def _perform_move(self, solution, nffg_element_iterator):
        """
        The next solution is generated by changing a single domain on a single NF/EP
        :param solution: the starting solution
        :param nffg_element_iterator: the index of the nffg element of which the domain should be changed
        :type solution: OrderedDict
        :type nffg_element_iterator: int
        :return:
        """
        next_solution = copy.deepcopy(solution)
        # get the name of the nffg element from the iterator, and assigned domain index
        element_to_move = list(solution.items())[nffg_element_iterator][0]
        current_domain_index = list(solution.items())[nffg_element_iterator][1]
        if element_to_move.split(':')[0] == "nf":
            domains_list = self._nf_feasible_domains[element_to_move.split(':', 1)[1]]
        else:
            domains_list = self._ep_feasible_domains[element_to_move.split(':', 1)[1]]
        # change domain for this element
        current_domain_index = (current_domain_index + 1) % len(domains_list)
        next_solution[element_to_move] = current_domain_index

        if current_domain_index == 0:
            nffg_element_iterator -= 1
        else:
            nffg_element_iterator = len(solution.items()) - 1

        return next_solution, nffg_element_iterator

    def _tag_nffg_with_scheduled_domains(self, nffg, solution):
        """

        :param nffg:
        :param solution:
        :type nffg: NF_FG
        :type solution: OrderedDict
        :return:
        """
        for element in solution:
            element_type, element_id = tuple(element.split(':', 1))
            if element_type == "nf":
                scheduled_domain = self._nf_feasible_domains[element_id][solution[element]]
                nffg.getVNF(element_id).domain = scheduled_domain
            else:
                scheduled_domain = self._ep_feasible_domains[element_id][solution[element]]
                nffg.getEndPoint(element_id).domain = scheduled_domain

    def _check_nf_and_ep_feasibility(self):
        for nf in self._nf_feasible_domains:
            if len(self._nf_feasible_domains[nf]) == 0:
                raise FeasibleDomainNotFoundForNFFGElement("there are not suitable domains for NF with id '" + nf + "'")
        for ep in self._ep_feasible_domains:
            if len(self._ep_feasible_domains[ep]) == 0:
                raise FeasibleDomainNotFoundForNFFGElement("there are not suitable domains for EP with id '" + ep + "'")

    def _is_solution_feasible(self, solution):
        """
        Check if a placement is topologically feasible (each domain can reach each others)
        :param solution:
        :type solution: OrderedDict
        :return:
        """
        involved_domains_set = set()
        for nf, domains in self._nf_feasible_domains.items():
            scheduled_domain = domains[solution["nf:"+nf]]
            involved_domains_set.add(scheduled_domain)
        for ep, domains in self._ep_feasible_domains.items():
            scheduled_domain = domains[solution["ep:"+ep]]
            involved_domains_set.add(scheduled_domain)
        base_domain = involved_domains_set.pop()
        base_involved_domains_set = copy.deepcopy(involved_domains_set)
        for domain in base_involved_domains_set:
            path = self._virtual_topology.\
                find_path_between_domains_involving_fewer_additional_domains(base_domain, domain, involved_domains_set)
            if path is None:
                return False
            base_involved_domains_set.update(path)
        return True

    @staticmethod
    def _are_solutions_equal(solution_a, solution_b):
        for nffg_element in solution_a:
            if solution_a[nffg_element] != solution_b[nffg_element]:
                return False
        return True
