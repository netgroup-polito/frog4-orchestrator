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
        :return: virtual channels to use for flows split across domains
        """
        # TODO should also provide information about virtual channel to use for each flow that is going to be split
        # check if each element of the nffg has at least a feasible domain
        self._check_nf_and_ep_feasibility()

        # solution is represented with two map:
        # "placement": {NF/EP : index} where each index represent the scheduled domain
        # "split-flows: {element/element : [{domain/domain: labeling-method}]}
        initial_solution = self._init_solution()

        # perform brute-force algorithm to find best solution
        optimal_solution, objective_function = self._brute_force(initial_solution, nffg)

        # check if retrieved solution is feasible
        if objective_function == sys.maxsize:
            raise FeasibleSolutionNotFoundForNFFG("There are no placements satisfying requested graph in the given " +
                                                  "topology")
        self._tag_nffg_with_scheduled_domains(nffg, optimal_solution)

        # schedule a label for each virtual channel
        for split_flow in optimal_solution["split-flows"]:
            for domains, vc in optimal_solution["split-flows"][split_flow].items():
                label = self._virtual_topology.pop_common_label(domains.split('/')[0], domains.split('/')[1],
                                                                vc["interface_a"], vc["interface_b"],
                                                                vc["labeling-method"])
                vc["label"] = label

        return optimal_solution["split-flows"]

    def _init_solution(self):
        initial_solution = {"placement": OrderedDict(), "split-flows": {}}
        for k in self._nf_feasible_domains:
            initial_solution["placement"]["nf:"+k] = 0
        for k in self._ep_feasible_domains:
            initial_solution["placement"]["ep:"+k] = 0
        return initial_solution

    def _schedule_virtual_channels_for_placement(self, solution, nffg):
        """
        Given the placement of a solution, find and store all needed virtual channels
        :param solution:
        :param nffg:
        :type solution: dict
        :type nffg: NF_FG
        :return:
        """
        # TODO if there are multiple (same direction) flows between 2 elements they will have the same name in this dict
        solution["split-flows"] = {}
        involved_domains_set = set()
        for nf, domains in self._nf_feasible_domains.items():
            scheduled_domain = domains[solution["placement"]["nf:"+nf]]
            involved_domains_set.add(scheduled_domain)
        for ep, domains in self._ep_feasible_domains.items():
            scheduled_domain = domains[solution["placement"]["ep:"+ep]]
            involved_domains_set.add(scheduled_domain)
        # for each nffg element, check if there are flow rules sending to an other domain
        for nf, domains in self._nf_feasible_domains.items():
            input_domain = domains[solution["placement"]["nf:"+nf]]
            input_element = "nf:"+nf
            flows = nffg.getFlowRulesSendingTrafficFromVNF(nffg.getVNF(nf))
            for flow in flows:
                for action in flow.actions:
                    if action.output is not None:
                        output_domain = None
                        output_element = None
                        if action.output.split(":")[0] == "endpoint":
                            # output_domain = domains[solution["placement"]["ep:"+action.output.split(":", 1)[1]]]
                            output_domain = self._ep_feasible_domains[action.output.split(":")[1]][
                                solution["placement"]["ep:"+action.output.split(":")[1]]]
                            output_element = "ep:"+action.output.split(":", 1)[1]
                        elif action.output.split(":")[0] == "vnf":
                            # output_domain = domains[solution["placement"]["nf:"+action.output.split(":")[1]]]
                            output_domain = self._nf_feasible_domains[action.output.split(":")[1]][
                                solution["placement"]["nf:"+action.output.split(":")[1]]]
                            output_element = "nf:"+action.output.split(":")[1]
                        # check if this flow is going to be split between two domains
                        if input_domain != output_domain:
                            path = self._virtual_topology.find_path_between_domains_involving_fewest_additional_domains(
                                input_domain, output_domain, involved_domains_set)
                            if path is None:
                                solution["topologically-feasible"] = False
                                return
                            # consume virtual channels for this path
                            vcs = self._virtual_topology.pop_virtual_channels_for_path(path)
                            solution["split-flows"][flow.id+'_'+input_element+'/'+output_element] = vcs
                            involved_domains_set.update(path)
                        break
        for ep, domains in self._ep_feasible_domains.items():
            input_domain = domains[solution["placement"]["ep:"+ep]]
            input_element = "ep:"+ep
            flows = nffg.getFlowRulesSendingTrafficFromEndPoint(ep)
            for flow in flows:
                for action in flow.actions:
                    if action.output is not None:
                        output_domain = None
                        output_element = None
                        if action.output.split(":")[0] == "endpoint":
                            # output_domain = domains[solution["placement"]["ep:"+action.output.split(":", 1)[1]]]
                            output_domain = self._ep_feasible_domains[action.output.split(":")[1]][
                                solution["placement"]["ep:"+action.output.split(":")[1]]]
                            output_element = "ep:"+action.output.split(":", 1)[1]
                        elif action.output.split(":")[0] == "vnf":
                            output_domain = self._nf_feasible_domains[action.output.split(":")[1]][
                                solution["placement"]["nf:"+action.output.split(":")[1]]]
                            # output_domain = domains[solution["placement"]["nf:"+action.output.split(":")[1]]]
                            output_element = "nf:"+action.output.split(":")[1]
                        # check if this flow is going to be split between two domains
                        if input_domain != output_domain:
                            path = self._virtual_topology.find_path_between_domains_involving_fewest_additional_domains(
                                input_domain, output_domain, involved_domains_set)
                            if path is None:
                                solution["topologically-feasible"] = False
                                return
                            # consume virtual channels for this path
                            vcs = self._virtual_topology.pop_virtual_channels_for_path(path)
                            solution["split-flows"][flow.id+'_'+input_element+'/'+output_element] = vcs
                            involved_domains_set.update(path)
                        break
        solution["involved-domains"] = involved_domains_set
        solution["topologically-feasible"] = True

    def _release_virtual_channels_for_solution(self, solution):
        """

        :param solution: dict
        :return:
        """
        for flow in solution["split-flows"]:
            self._virtual_topology.release_virtual_channels(solution["split-flows"][flow])

    @staticmethod
    def _objective_function(solution):
        """
        This objective function returns the number of domains involved in the service
        :param solution:
        :type solution: dict
        :return: number of involved domains
        """

        '''
        involved_domains_set = set()
        for nf, domains in self._nf_feasible_domains.items():
            scheduled_domain = domains[solution["placement"]["nf:"+nf]]
            involved_domains_set.add(scheduled_domain)
        for ep, domains in self._ep_feasible_domains.items():
            scheduled_domain = domains[solution["placement"]["ep:"+ep]]
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
        '''
        if not solution["topologically-feasible"]:
            return sys.maxsize
        else:
            return len(solution["involved-domains"])

    def _brute_force(self, initial_solution, nffg):
        """
        Try all the possible combination and returns the one that minimize the objective function
        :param initial_solution:
        :param nffg:
        :type initial_solution: dict
        :type nffg: NF_FG
        :return: the optimal solution
        """
        current_solution = copy.deepcopy(initial_solution)

        self._schedule_virtual_channels_for_placement(current_solution, nffg)
        best_solution = copy.deepcopy(current_solution)
        best_objective_function = self._objective_function(current_solution)
        self._release_virtual_channels_for_solution(current_solution)

        nffg_element_iterator = len(current_solution["placement"].items())-1

        while True:
            # get next solution
            current_solution, nffg_element_iterator = self._perform_move(current_solution, nffg_element_iterator)
            # check if we tested all combinations
            if nffg_element_iterator == -1:
                break
            # check if returned solution is a new solution, if not then skip it
            if nffg_element_iterator != len(current_solution["placement"].items())-1:
                continue

            # check if current solution is better than the best so far
            self._schedule_virtual_channels_for_placement(current_solution, nffg)
            current_objective_function = self._objective_function(current_solution)
            if current_objective_function < best_objective_function:
                best_solution = copy.deepcopy(current_solution)
                best_objective_function = current_objective_function
            self._release_virtual_channels_for_solution(current_solution)

        return best_solution, best_objective_function

    def _perform_move(self, solution, nffg_element_iterator):
        """
        The next solution is generated by changing a single domain on a single NF/EP
        :param solution: the starting solution
        :param nffg_element_iterator: the index of the nffg element of which the domain should be changed
        :type solution: dict
        :type nffg_element_iterator: int
        :return:
        """
        next_solution = copy.deepcopy(solution)
        # get the name of the nffg element from the iterator, and assigned domain index
        element_to_move = list(solution["placement"].items())[nffg_element_iterator][0]
        current_domain_index = list(solution["placement"].items())[nffg_element_iterator][1]
        if element_to_move.split(':')[0] == "nf":
            domains_list = self._nf_feasible_domains[element_to_move.split(':', 1)[1]]
        else:
            domains_list = self._ep_feasible_domains[element_to_move.split(':', 1)[1]]
        # change domain for this element
        current_domain_index = (current_domain_index + 1) % len(domains_list)
        next_solution["placement"][element_to_move] = current_domain_index

        if current_domain_index == 0:
            nffg_element_iterator -= 1
        else:
            nffg_element_iterator = len(solution["placement"].items()) - 1

        return next_solution, nffg_element_iterator

    def _tag_nffg_with_scheduled_domains(self, nffg, solution):
        """

        :param nffg:
        :param solution:
        :type nffg: NF_FG
        :type solution: dict
        :return:
        """
        for element in solution["placement"]:
            element_type, element_id = tuple(element.split(':', 1))
            if element_type == "nf":
                scheduled_domain = self._nf_feasible_domains[element_id][solution["placement"][element]]
                nffg.getVNF(element_id).domain = scheduled_domain
            else:
                scheduled_domain = self._ep_feasible_domains[element_id][solution["placement"][element]]
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
            scheduled_domain = domains[solution["placement"]["nf:"+nf]]
            involved_domains_set.add(scheduled_domain)
        for ep, domains in self._ep_feasible_domains.items():
            scheduled_domain = domains[solution["placement"]["ep:"+ep]]
            involved_domains_set.add(scheduled_domain)
        base_domain = involved_domains_set.pop()
        base_involved_domains_set = copy.deepcopy(involved_domains_set)
        for domain in base_involved_domains_set:
            path = self._virtual_topology.\
                find_path_between_domains_involving_fewest_additional_domains(base_domain, domain, involved_domains_set)
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
