'''
Created on Oct 23, 2015

@author: fabiomignini
'''
from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.sql.graph import GraphModel
from orchestrator_core.sql.session import SessionModel

session = get_session()
session.query(GraphModel).delete()
session.query(SessionModel).delete()

print("Database sessions deleted")
