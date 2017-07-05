'''
@author: fabiomignini
@author: stefanopetrangeli
'''
import json,  uuid, os, inspect
from nffg_library.nffg import VNF, Port, EndPoint, FlowRule
from orchestrator_core.config import Configuration
from nffg_library.nffg import NF_FG, Match, Action

SWITCH_NAME = Configuration().SWITCH_NAME
CONTROL_SWITCH_NAME = Configuration().CONTROL_SWITCH_NAME
SWITCH_TEMPLATE = Configuration().SWITCH_TEMPLATE


class NFFG_Manager(object):
    
    def __init__(self, nffg=None):
        """

        :param nffg:
        :type nffg: NF_FG
        """
        self.nffg = nffg

    def getNFFGDict(self, filename): 
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        return self.getDictFromFile(base_folder+"/graphs/", filename)
                
    def getDictFromFile(self, path, filename):
        json_data=open(path+filename).read()
        return json.loads(json_data)

    # Graph optimization
    def mergeUselessVNFs(self):
        '''
        This function try to optimize the NF-FG merging or deleting useless VNFs.
        In the current implementation only the merge of the switch NF (based on the name of the VNF) is done.
        '''
        self.findSwitchToMerge()
    
    def findSwitchToMerge(self):
        # To be merged, the two switch ports that are connected together should not filter the traffic.
        switches = {}
        for vnf in self.nffg.vnfs:
            for switch_name in SWITCH_NAME:
                if vnf.name == switch_name:
                    switches[vnf.id] = vnf
        for flow_rule in self.nffg.flow_rules:
            if flow_rule.match.port_in.split(':')[0] == 'vnf' and flow_rule.match.port_in.split(':')[1] in switches:
                for action in flow_rule.actions:
                    if action.output.split(':')[0] == 'vnf' and action.output.split(':')[1] in switches:
                        self.mergeSwitches(switches[flow_rule.match.port_in.split(':')[1]], 
                                           flow_rule.match.port_in.split(':')[2]+':'+flow_rule.match.port_in.split(':')[3],
                                           switches[action.output.split(':')[1]], 
                                           action.output.split(':')[2]+':'+action.output.split(':')[3], 
                                           SWITCH_NAME[0])
                        self.findSwitchToMerge()
                        return
        switches = {}
        for vnf in self.nffg.vnfs:
            for switch_name in CONTROL_SWITCH_NAME:
                if vnf.name == switch_name:
                    switches[vnf.id] = vnf
        for flow_rule in self.nffg.flow_rules:
            if flow_rule.match.port_in.split(':')[0] == 'vnf' and flow_rule.match.port_in.split(':')[1] in switches:
                for action in flow_rule.actions:
                    if action.output.split(':')[0] == 'vnf' and action.output.split(':')[1] in switches:
                        self.mergeSwitches(switches[flow_rule.match.port_in.split(':')[1]], 
                                           flow_rule.match.port_in.split(':')[2]+':'+flow_rule.match.port_in.split(':')[3],
                                           switches[action.output.split(':')[1]], 
                                           action.output.split(':')[2]+':'+action.output.split(':')[3],
                                           CONTROL_SWITCH_NAME[0])
                        self.findSwitchToMerge()
                        return
    
    def createSwitchVNF(self, switch_name=SWITCH_NAME[0]):
        # Create an ID
        _id = uuid.uuid4().hex
        
        # TODO: Check uniqueness of the ID
        switch = VNF(_id=_id, name=switch_name, vnf_template_location=SWITCH_TEMPLATE)
        return switch
    
    def createSwitchPort(self, switch):
        # Create an ID. Check the switch to obtain the maximum relative ID
        maximum_relative_id = switch.getHigherReletiveIDForPortLabel("L2Port")
        new_relative_id = int(maximum_relative_id) + 1
        _id = "L2Port:"+str(new_relative_id)
        
        return Port(_id=_id, name="auto-generated-port")
    
    def mergeSwitches(self, switch1, port_switch1_id, switch2, port_switch2_id, switch_name):
        
        # Create a new switch
        new_switch = self.createSwitchVNF(switch_name)
        self.nffg.addVNF(new_switch)
        
        # Delete ports and flow-rules that connect the two switches
        self.nffg.deleteConnectionsBetweenVNFs(switch1.id, port_switch1_id, switch2.id, port_switch2_id)
        for port in switch1.ports:
            if port.id == port_switch1_id:
                port_switch1 = port
        switch1.ports.remove(port_switch1)
        for port in switch2.ports:
            if port.id == port_switch2_id:
                port_switch2 = port
        switch2.ports.remove(port_switch2)
        
        # Add to the new switch the ports of the other two
        for switch in [switch1, switch2]:
            
            for port in switch.ports:
                # TODO: If one of the two switches have a control port, this will be added only one time
                new_port = self.createSwitchPort(new_switch)
                new_switch.addPort(new_port)
                # Change the flow-rule of the ports of the old switches with the new port id
                for flow_rule in self.nffg.flow_rules:
                    flow_rule.changePortOfFlowRule('vnf:'+switch.id+':'+port.id, 'vnf:'+new_switch.id+':'+new_port.id)
            
        # Delete the previous switches and their flow-rules
        self.nffg.vnfs.remove(switch1)
        self.nffg.vnfs.remove(switch2)
        
    def addEndpointsCoupleAndFlowrules(self, flow_id, ep1_id, ep2_id, bidirectional=False, flowrule_priority=10):

        flowrule_1 = FlowRule()
        flowrule_1.id = flow_id
        flowrule_1.priority = flowrule_priority
        flowrule_1.match = Match(port_in="endpoint:"+ep1_id)
        flowrule_1.actions.append(Action(output="endpoint:"+ep2_id))
        if self.nffg.getEndPoint(ep1_id) is None:
            endpoint_1 = EndPoint(_id=ep1_id)
            self.nffg.addEndPoint(endpoint_1)
        if self.nffg.getEndPoint(ep2_id) is None:
            endpoint_2 = EndPoint(_id=ep2_id)
            self.nffg.addEndPoint(endpoint_2)
        self.nffg.addFlowRule(flowrule_1)
        if bidirectional:
            flowrule_2 = FlowRule()
            flowrule_2.id = ep2_id + "_reverse"
            flowrule_2.priority = flowrule_priority
            flowrule_2.match = Match(port_in="endpoint:"+ep2_id)
            flowrule_2.actions.append(Action(output="endpoint:"+ep1_id))
            self.nffg.addFlowRule(flowrule_2)

    def addFlowRule(self, flow_id, ep1_id, ep2_id, flowrule_priority=10):
        flowrule = FlowRule()
        flowrule.id = flow_id
        flowrule.priority = flowrule_priority
        flowrule.match = Match(port_in="endpoint:"+ep1_id)
        flowrule.actions.append(Action(output="endpoint:"+ep2_id))
        self.nffg.addFlowRule(flowrule)
