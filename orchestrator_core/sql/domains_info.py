'''
Created on 01 dic 2015

@author: stefanopetrangeli
'''
from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.config import Configuration
from orchestrator_core.sql.session import Session
from orchestrator_core.domain_info import DomainInfo, GreTunnel, Interface
from sqlalchemy.sql import func
from sqlalchemy.orm.exc import NoResultFound

import logging

Base = declarative_base()
sqlserver = Configuration().CONNECTION

class DomainsInformationModel(Base):
    __tablename__ = 'domains_information'
    attributes = ['id', 'domain_ip', 'domain_name','interface','interface_type','neighbor','gre','vlan']
    id = Column(Integer, primary_key=True)
    domain_ip = Column(VARCHAR(64))
    domain_name = Column(VARCHAR(64))
    interface = Column(VARCHAR(64))
    interface_type = Column(VARCHAR(64))
    neighbor = Column(VARCHAR(64))
    gre = Column(Boolean())
    vlan = Column(Boolean())
    
class DomainsVlanModel(Base):    
    __tablename__ = 'domains_vlan'
    attributes = ['id', 'domains_info_id','vlan']
    id = Column(Integer, primary_key=True)
    domains_info_id = Column(Integer)
    vlan = Column(VARCHAR(64))
    
class DomainsGreModel(Base):    
    __tablename__ = 'domains_gre'
    attributes = ['id', 'name', 'domains_info_id','local_ip','remote_ip','gre_key']
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(64))    
    domains_info_id = Column(Integer)
    local_ip = Column(VARCHAR(64))
    remote_ip = Column(VARCHAR(64))    
    gre_key = Column(VARCHAR(64))                
    
class DomainsInformation(object):
    def __init__(self):
        pass
    
    def getDomainNamefromIP(self, domain_ip):
        session = get_session()  
        domain_name=None
        domain_info = session.query(DomainsInformationModel).filter_by(domain_ip = domain_ip).first()
        if domain_info is not None:
            domain_name=domain_info.domain_name
        return domain_name
    
    def get_domain_info(self, domain_name=None):
        session = get_session() 
        domains_info = {}
        if domain_name is not None:
            pass
        else:
            domains_refs = session.query(DomainsInformationModel).all()
            for domain_ref in domains_refs:
                if domain_ref.domain_name not in domains_info:
                    domain_info = DomainInfo(name=domain_ref.domain_name, ip=domain_ref.domain_ip)
                    domains_info[domain_ref.domain_name]=domain_info
                else:
                    domain_info = domains_info[domain_ref.domain_name]
                
                intf = Interface(name=domain_ref.interface, _type=domain_ref.interface_type,neighbor=domain_ref.neighbor,gre=domain_ref.gre, vlan=domain_ref.vlan)
                if intf.gre is True:
                    gre_refs = session.query(DomainsGreModel).filter_by(domains_info_id=domain_ref.id).all()
                    for gre_ref in gre_refs:
                        gre_tunnel = GreTunnel(name=gre_ref.name, local_ip=gre_ref.local_ip, remote_ip=gre_ref.remote_ip, gre_key=gre_ref.gre_key)
                        intf.addGreTunnel(gre_tunnel)
                #TODO: vlan
                       
                domain_info.addInterface(intf)
        return domains_info
                     
    
    def add_domain_info(self, domain_info, update=True):
        session = get_session()  
        with session.begin():
            if update is True:
                try:
                    domain_refs = session.query(DomainsInformationModel).filter_by(domain_name=domain_info.name).all()
                    for domain_ref in domain_refs:
                        session.query(DomainsInformationModel).filter_by(id = domain_ref.id).delete()
                        session.query(DomainsVlanModel).filter_by(domains_info_id=domain_ref.id).delete()
                        session.query(DomainsGreModel).filter_by(domains_info_id=domain_ref.id).delete()
                except NoResultFound:
                    pass                        
            self.id_generator(domain_info)
            for interface in domain_info.interfaces:
                info_ref = DomainsInformationModel(id=self.info_id, domain_ip=domain_info.ip, domain_name=domain_info.name, interface=interface.name, interface_type=interface.type, neighbor=interface.neighbor, gre=interface.gre, vlan=interface.vlan)
                session.add(info_ref)
                for gre_tunnel in interface.gre_tunnels:
                    gre_ref = DomainsGreModel(id=self.gre_id, name=gre_tunnel.name, domains_info_id=self.info_id, local_ip=gre_tunnel.local_ip, remote_ip=gre_tunnel.remote_ip, gre_key=gre_tunnel.gre_key)
                    session.add(gre_ref)
                    self.gre_id = self.gre_id + 1
                #TODO: vlan
                self.info_id = self.info_id + 1      
            
    def id_generator(self, domain_info):
        info_base_id = self._get_higher_info_id()
        vlan_base_id = self._get_higher_vlan_id()
        gre_base_id = self._get_higher_gre_id()
        if info_base_id is not None:
            self.info_id = int(info_base_id) + 1
        else:
            self.info_id = 0
        if vlan_base_id is not None:
            self.vlan_id = int(vlan_base_id) + 1
        else:
            self.vlan_id = 0
        if gre_base_id is not None:
            self.gre_id = int(gre_base_id) + 1
        else:
            self.gre_id = 0  
                
    def _get_higher_info_id(self):  
        session = get_session()  
        return session.query(func.max(DomainsInformationModel.id).label("max_id")).one().max_id
    
    def _get_higher_vlan_id(self):
        session = get_session()  
        return session.query(func.max(DomainsVlanModel.id).label("max_id")).one().max_id
        
    def _get_higher_gre_id(self):
        session = get_session()  
        return session.query(func.max(DomainsGreModel.id).label("max_id")).one().max_id     
