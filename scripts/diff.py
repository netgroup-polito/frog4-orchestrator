'''
Created on Oct 26, 2015

@author: fabiomignini
'''
from nffg_library.nffg import NF_FG
nffg_dict_1 = {"forwarding-graph":{"id":"00000001","name":"Protected access to the internet","VNFs":[{"vnf_template":"switch.json","id":"00000001","name":"switch-data","ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"}],"groups":["isp-function"]},{"vnf_template":"dhcp.json","ports":[{"id":"inout:0","name":"data-port"}],"name":"dhcp","id":"00000002","groups":["isp-function"]},{"vnf_template":"cisco_firewall.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"firewall","id":"00000003"},{"vnf_template":"nat.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"router-nat","id":"00000004","groups":["isp-function"]}],"end-points":[{"id":"00000001","name":"ingress","type":"interface","interface":{"node":"130.192.225.193","interface":"to-br-usr"}},{"id":"00000002","name":"egress","type":"interface-out","interface-out":{"node":"130.192.225.193","interface":"eth2"}}],"big-switch":{"flow-rules":[{"id":"000000001","priority":1,"match":{"port_in":"endpoint:00000001"},"actions":[{"output":"vnf:00000001:L2Port:0"}]},{"id":"000000002","priority":1,"match":{"port_in":"vnf:00000001:L2Port:0"},"actions":[{"output":"endpoint:00000001"}]},{"id":"000000003","priority":1,"match":{"port_in":"vnf:00000002:inout:0"},"actions":[{"output":"vnf:00000001:L2Port:1"}]},{"id":"000000004","priority":1,"match":{"port_in":"vnf:00000001:L2Port:1"},"actions":[{"output":"vnf:00000002:inout:0"}]},{"id":"000000005","priority":1,"match":{"port_in":"vnf:00000003:User:0"},"actions":[{"output":"vnf:00000001:L2Port:2"}]},{"id":"000000006","priority":1,"match":{"port_in":"vnf:00000001:L2Port:2"},"actions":[{"output":"vnf:00000003:User:0"}]},{"id":"000000007","priority":1,"match":{"port_in":"vnf:00000003:WAN:0"},"actions":[{"output":"vnf:00000004:User:0"}]},{"id":"000000008","priority":1,"match":{"port_in":"vnf:00000004:User:0"},"actions":[{"output":"vnf:00000003:WAN:0"}]},{"id":"000000009","priority":1,"match":{"port_in":"endpoint:00000002"},"actions":[{"output":"vnf:00000004:WAN:0"}]},{"id":"000000010","priority":1,"match":{"port_in":"vnf:00000004:WAN:0"},"actions":[{"output":"endpoint:00000002"}]}]}}}
nffg_dict_2 = {"forwarding-graph":{"VNFs":[{"ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"},{"id":"L2Port:3","name":"data-lan"}],"vnf_template":"switch.json","id":"00000001","groups":["isp-function"],"name":"switch-data"},{"ports":[{"id":"inout:0","name":"data-port"}],"vnf_template":"dhcp.json","id":"00000002","groups":["isp-function"],"name":"dhcp"},{"ports":[{"id":"inout:0","name":"data-port"}],"vnf_template":"dhcp.json","id":"00000005","groups":["isp-function"],"name":"dhcp"},{"ports":[{"id":"L2Port:0"},{"id":"L2Port:1"}],"vnf_template":"switch.json","id":"00000006","name":"firewall"},{"ports":[{"id":"User:0"}],"vnf_template":"nat.json","id":"00000004","groups":["isp-function"],"name":"router-nat"}],"end-points":[{"interface":{"node":"130.192.225.193","interface":"to-br-usr"},"type":"interface","id":"00000001","name":"ingress"}],"big-switch":{"flow-rules":[{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:0"}],"id":"000000001","match":{"port_in":"endpoint:00000001"}},{"priority":1,"actions":[{"output":"endpoint:00000001"}],"id":"000000002","match":{"port_in":"vnf:00000001:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:1"}],"id":"000000003","match":{"port_in":"vnf:00000002:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000002:inout:0"}],"id":"000000004","match":{"port_in":"vnf:00000001:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:2"}],"id":"000000005","match":{"port_in":"vnf:00000006:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:00000006:L2Port:0"}],"id":"000000006","match":{"port_in":"vnf:00000001:L2Port:2"}},{"priority":1,"actions":[{"output":"vnf:00000004:User:0"}],"id":"000000007","match":{"port_in":"vnf:00000006:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000006:L2Port:1"}],"id":"000000008","match":{"port_in":"vnf:00000004:User:0"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:3"}],"id":"000000011","match":{"port_in":"vnf:00000005:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000005:inout:0"}],"id":"000000012","match":{"port_in":"vnf:00000001:L2Port:3"}}]},"id":"00000001","name":"Protected access to the internet"}}
nffg_1 = NF_FG()
nffg_1.parseDict(nffg_dict_1)
nffg_2 = NF_FG()
nffg_2.parseDict(nffg_dict_2)
nffg_diff = nffg_1.diff(nffg_2)
print(nffg_diff.getDict(True))