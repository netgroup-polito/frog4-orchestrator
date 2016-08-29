import json, requests

username = "demo"
password = "demo"
tenant = "demo"
orchestrator_endpoint = "http://130.192.225.107:9000/NF-FG/"
headers = {'Content-Type': 'application/json', 'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}

nffg_dict = \
{
  "forwarding-graph": {
    "id": "10100",
    "name": "Demo Graph 1",
    "VNFs": [
      {
        "id": "00000001",
        "name": "vnf1",
        "vnf_template": "cirros_nodhcp",
        "ports": [
          {
            "id": "inout:0"
          }
        ]
      },
      {
        "id": "00000002",
        "name": "vnf2",
        "vnf_template": "cirros_nodhcp",
        "ports": [
          {
            "id": "inout:0"
          }
        ]
      }
    ],
    "big-switch": {
      "flow-rules": [
        {
          "match": {
            "port_in": "vnf:00000001:inout:0"
          },
          "actions": [
            {
              "output_to_port": "vnf:00000002:inout:0"
            }
          ],
          "priority": 10,
          "id": "1"
        },
        {
          "match": {
            "port_in": "vnf:00000002:inout:0"
          },
          "actions": [
            {
              "output_to_port": "vnf:00000001:inout:0"
            }
          ],
          "priority": 10,
          "id": "2"
        }
      ]
    }
  }
}


resp = requests.put(orchestrator_endpoint, json.dumps(nffg_dict), headers=headers)
resp.raise_for_status()

print('Job completed')
