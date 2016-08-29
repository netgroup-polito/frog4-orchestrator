import json, requests

username = "demo"
password = "demo"
tenant = "demo"
orchestrator_endpoint = "http://130.192.225.107:9000/NF-FG/"
headers = {'Content-Type': 'application/json', 'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}

nffg_dict_1 = {"forwarding-graph":{"id":"102_1","name":"Demo Graph 2_1","VNFs":[{"id":"00000003","name":"dhcp","vnf_template":"dhcp","ports":[{"id":"inout:0"}]}],"end-points":[{"type":"internal","internal":{"internal-group":"1","node-id":"130.192.225.122"},"id":"00000001"}],"big-switch":{"flow-rules":[{"match":{"port_in":"endpoint:00000001"},"actions":[{"output_to_port":"vnf:00000003:inout:0"}],"priority":10,"id":"1"},{"match":{"port_in":"vnf:00000003:inout:0"},"actions":[{"output_to_port":"endpoint:00000001"}],"priority":10,"id":"2"}]}}}
nffg_dict_2 = {"forwarding-graph":{"id":"102_2","name":"Demo Graph 2_2","VNFs":[{"id":"00000003","name":"user1","vnf_template":"cirros","ports":[{"id":"inout:0"}]}],"end-points":[{"type":"internal","internal":{"internal-group":"1","node-id":"130.192.225.122"},"id":"00000001"}],"big-switch":{"flow-rules":[{"match":{"port_in":"endpoint:00000001"},"actions":[{"output_to_port":"vnf:00000003:inout:0"}],"priority":10,"id":"1"},{"match":{"port_in":"vnf:00000003:inout:0"},"actions":[{"output_to_port":"endpoint:00000001"}],"priority":10,"id":"2"}]}}}
nffg_dict_3 = {"forwarding-graph":{"id":"102_3","name":"Demo Graph 2_3","VNFs":[{"id":"00000003","name":"user2","vnf_template":"cirros","ports":[{"id":"inout:0"}]}],"end-points":[{"type":"internal","internal":{"internal-group":"1","node-id":"130.192.225.122"},"id":"00000001"}],"big-switch":{"flow-rules":[{"match":{"port_in":"endpoint:00000001"},"actions":[{"output_to_port":"vnf:00000003:inout:0"}],"priority":10,"id":"1"},{"match":{"port_in":"vnf:00000003:inout:0"},"actions":[{"output_to_port":"endpoint:00000001"}],"priority":10,"id":"2"}]}}}

resp = requests.put(orchestrator_endpoint, json.dumps(nffg_dict_1), headers=headers)
resp.raise_for_status()

resp = requests.put(orchestrator_endpoint, json.dumps(nffg_dict_2), headers=headers)
resp.raise_for_status()

resp = requests.put(orchestrator_endpoint, json.dumps(nffg_dict_3), headers=headers)
resp.raise_for_status()

print('Job completed')
