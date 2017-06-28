'''
Created on 04 dic 2015

@author: stefanopetrangeli
'''
from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.sql.domains_info import DomainsGreModel, DomainsVlanModel, DomainsInformationModel,\
    DomainsNeighborModel,FunctionalCapabilityModel, FunctionSpecificationModel
from orchestrator_core.sql.domain import DomainModel, DomainTokenModel

session = get_session()
session.query(DomainModel).delete()
session.query(DomainsGreModel).delete()
session.query(DomainsInformationModel).delete()
session.query(DomainsVlanModel).delete()
session.query(DomainsNeighborModel).delete()
session.query(FunctionSpecificationModel).delete()
session.query(FunctionalCapabilityModel).delete()
session.query(DomainTokenModel).delete()

print("All the domains information deleted")
