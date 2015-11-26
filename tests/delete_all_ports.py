'''
Created on Oct 30, 2015

@author: stefanopetrangeli
'''
import requests, json

openstack_url = "http://jolnet-controller:9696/v2.0/ports"

headers = {'X-Auth-Token': "MIIQ0AYJKoZIhvcNAQcCoIIQwTCCEL0CAQExCTAHBgUrDgMCGjCCDyYGCSqGSIb3DQEHAaCCDxcEgg8TeyJhY2Nlc3MiOiB7InRva2VuIjogeyJpc3N1ZWRfYXQiOiAiMjAxNS0xMS0wOVQxMDoyMzo1MC41ODYxNDkiLCAiZXhwaXJlcyI6ICIyMDE1LTExLTA5VDExOjIzOjUwWiIsICJpZCI6ICJwbGFjZWhvbGRlciIsICJ0ZW5hbnQiOiB7ImRlc2NyaXB0aW9uIjogIlNwZXJpbWVudGF6aW9uZSBGdW5jdGlvbiBDaGFpbnMgUG9saXRvICgxKSIsICJlbmFibGVkIjogdHJ1ZSwgImlkIjogImZmMjQ5OGFjZDNlOTRiMGE4ODE1YjBkZjIzMWM0NTIwIiwgIm5hbWUiOiAiUG9saVRPX2NoYWluMSJ9fSwgInNlcnZpY2VDYXRhbG9nIjogW3siZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzQvdjIvZmYyNDk4YWNkM2U5NGIwYTg4MTViMGRmMjMxYzQ1MjAiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODc3NC92Mi9mZjI0OThhY2QzZTk0YjBhODgxNWIwZGYyMzFjNDUyMCIsICJpZCI6ICI1NGJiOGIyNGQ0NmM0MDMxODUzOTkyYzFmYTk5MjAxYiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzQvdjIvZmYyNDk4YWNkM2U5NGIwYTg4MTViMGRmMjMxYzQ1MjAifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY29tcHV0ZSIsICJuYW1lIjogIm5vdmEifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6OTY5Ni8iLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6OTY5Ni8iLCAiaWQiOiAiNTg2ZjZiM2VmYzEwNDQ4Yzg3NTRmMzM1ODlkZWQyNWEiLCAicHVibGljVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo5Njk2LyJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJuZXR3b3JrIiwgIm5hbWUiOiAibmV1dHJvbiJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo4Nzc2L3YyL2ZmMjQ5OGFjZDNlOTRiMGE4ODE1YjBkZjIzMWM0NTIwIiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzYvdjIvZmYyNDk4YWNkM2U5NGIwYTg4MTViMGRmMjMxYzQ1MjAiLCAiaWQiOiAiMDViNWY5OGRhY2RiNDk4MWIzZGVhOWZhZTI1YWYyMmQiLCAicHVibGljVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo4Nzc2L3YyL2ZmMjQ5OGFjZDNlOTRiMGE4ODE1YjBkZjIzMWM0NTIwIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogInZvbHVtZXYyIiwgIm5hbWUiOiAiY2luZGVyX3YyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0OjkyOTIiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6OTI5MiIsICJpZCI6ICI2OTJiNTVlOTFkYjg0MjI4OTVhYTJjMzYxNTg5YWRjYiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0OjkyOTIifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiaW1hZ2UiLCAibmFtZSI6ICJnbGFuY2UifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODc3NyIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo4Nzc3IiwgImlkIjogIjExOGY4ZTBkNzgyMDQwYWRhMGIzOTBlNTVjYjUxYjQ2IiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODc3NyJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJtZXRlcmluZyIsICJuYW1lIjogImNlaWxvbWV0ZXIifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODAwMC92MSIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo4MDAwL3YxIiwgImlkIjogIjNjYWYyNDIzMTdkNDQ2ZGFiY2RkOTJlMTY4Nzg4YWMwIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODAwMC92MSJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJjbG91ZGZvcm1hdGlvbiIsICJuYW1lIjogImhlYXQtY2ZuIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzYvdjEvZmYyNDk4YWNkM2U5NGIwYTg4MTViMGRmMjMxYzQ1MjAiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODc3Ni92MS9mZjI0OThhY2QzZTk0YjBhODgxNWIwZGYyMzFjNDUyMCIsICJpZCI6ICI2NTBiNWJhYjMyZWY0ODg0YjIxYjBjM2EwMTA3ZmJmZCIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzYvdjEvZmYyNDk4YWNkM2U5NGIwYTg4MTViMGRmMjMxYzQ1MjAifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAidm9sdW1lIiwgIm5hbWUiOiAiY2luZGVyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzMvc2VydmljZXMvQWRtaW4iLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODc3My9zZXJ2aWNlcy9DbG91ZCIsICJpZCI6ICI1NTIzZDI3ZWYwMDM0NDIyYTIzMGY3NTZiNDU5YTdmNiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0Ojg3NzMvc2VydmljZXMvQ2xvdWQifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiZWMyIiwgIm5hbWUiOiAibm92YV9lYzIifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODAwNC92MS9mZjI0OThhY2QzZTk0YjBhODgxNWIwZGYyMzFjNDUyMCIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDo4MDA0L3YxL2ZmMjQ5OGFjZDNlOTRiMGE4ODE1YjBkZjIzMWM0NTIwIiwgImlkIjogIjlkOTAyY2I4NDk3ZjQ1YmQ4Zjk1MGNlZWI3OGIzOTI0IiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTYzLjE2Mi4yMzQuNDQ6ODAwNC92MS9mZjI0OThhY2QzZTk0YjBhODgxNWIwZGYyMzFjNDUyMCJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJvcmNoZXN0cmF0aW9uIiwgIm5hbWUiOiAiaGVhdCJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xNjMuMTYyLjIzNC40NDozNTM1Ny92Mi4wIiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0OjUwMDAvdjIuMCIsICJpZCI6ICIwZTJmM2Q4MjJhNzY0YmMwYWYyZWE2MWFmOTlhMzhjYiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE2My4xNjIuMjM0LjQ0OjUwMDAvdjIuMCJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJpZGVudGl0eSIsICJuYW1lIjogImtleXN0b25lIn1dLCAidXNlciI6IHsidXNlcm5hbWUiOiAiQWRtaW5Qb2xpVE8iLCAicm9sZXNfbGlua3MiOiBbXSwgImlkIjogIjk0OGVjYmNkMDVhOTQzZGFhMzg4MzdjOTY5MjA5OTVjIiwgInJvbGVzIjogW3sibmFtZSI6ICJoZWF0X3N0YWNrX293bmVyIn0sIHsibmFtZSI6ICJfbWVtYmVyXyJ9XSwgIm5hbWUiOiAiQWRtaW5Qb2xpVE8ifSwgIm1ldGFkYXRhIjogeyJpc19hZG1pbiI6IDAsICJyb2xlcyI6IFsiNGYyNzFjOTlkNmMyNDExYjk0NzM4OTBlNDMwZWQ3OTciLCAiOWZlMmZmOWVlNDM4NGIxODk0YTkwODc4ZDNlOTJiYWIiXX19fTGCAYEwggF9AgEBMFwwVzELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVVuc2V0MQ4wDAYDVQQHDAVVbnNldDEOMAwGA1UECgwFVW5zZXQxGDAWBgNVBAMMD3d3dy5leGFtcGxlLmNvbQIBATAHBgUrDgMCGjANBgkqhkiG9w0BAQEFAASCAQAZMitQzbXjTuO6JibPAKQ-ER5GbT41Fua2HGQp4bbDW90wj7cCR0J15nwKexN4chdsmW7Zth1-1KhfnnIlK5sVmpSeOMM7FOBICi3ntSUlN0OXlqSlcWGHtmr8P4JbbA8o9EFc1YWyN22cXJqSlwXfHkj7mu4U43lFxT2Ydny0XwYAXA+FXvOaGAsHAxVjCjPV1e-W851JUTyVngovKrum-4xiOUR7h5DdMapZwt5W2L4ZtJfdO6Wn-OWqygxNwQFaAk9HilFnwdQeyxs0wnOxnpBYZlM5zuJSiGnwMSn1Dn5MSuG1PPfQ-JWAoEUXiB4oPXrVd+EYP8wmYhUetSUT"}
jsonn = requests.get(openstack_url, headers=headers)

print(jsonn.text)
json2 = json.loads(jsonn.text)
for port in json2['ports']:
    requests.delete(openstack_url+"/"+port['id'], headers=headers)