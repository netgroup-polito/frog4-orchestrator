from .doubledecker.clientSafe import ClientSafe
from .domain_info import DomainInfo
from .sql.domains_info import DomainsInformation
from .sql.node import Node
import logging, json

class DD_Server(ClientSafe):

    def __init__(self, name, dealerurl, customer, keyfile):
        super().__init__(name, dealerurl, customer, keyfile)

    def on_data(self, dest, msg):
        print(dest, " sent", msg)

    def on_pub(self, src, topic, msg):
        msgstr = "PUB %s from %s: %s" % (str(topic), str(src), str(msg))
        print(msgstr)
        #TODO: validation of msg needed
        domain_name = src.decode("utf-8")
        try:
            node = Node().getNodeFromName(domain_name)
            domain_info = json.loads(msg.decode("utf-8"))
            
            di = DomainInfo(node_id=node.id)
            di.parseDict(domain_info)
            #print (domain_info)
            logging.debug("Domain information arrived from %s: %s" % (domain_name , str(domain_info)))
            DomainsInformation().add_domain_info(di)
        except Exception as ex:
            logging.exception(ex)  

    def on_reg(self):
        self.subscribe("NF-FG","/0/0/0/") 

    def on_discon(self):
        pass

    def unsubscribe(self, topic, scope):
        pass
    
    def on_cli(self, dummy, other_dummy):
        pass
