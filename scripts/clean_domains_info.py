'''
Created on 04 dic 2015

@author: stefanopetrangeli
'''
from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.sql.domains_info import DomainsGreModel, DomainsVlanModel, DomainsInformationModel,DomainsNeighborModel

session = get_session()
session.query(DomainsGreModel).delete()
session.query(DomainsInformationModel).delete()
session.query(DomainsVlanModel).delete()
session.query(DomainsNeighborModel).delete()

print("Database domain_info deleted")
