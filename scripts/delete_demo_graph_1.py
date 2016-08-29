import requests

username = "demo"
password = "demo"
tenant = "demo"
orchestrator_endpoint = "http://130.192.225.107:9000/NF-FG/"
headers = {'Content-Type': 'application/json', 'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}

nffg_id = '101'

url = orchestrator_endpoint + nffg_id
resp = requests.delete(url, headers=headers)
resp.raise_for_status()

print('Job completed')
