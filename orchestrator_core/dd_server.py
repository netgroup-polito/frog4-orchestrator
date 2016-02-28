try:
    from .doubledecker.clientSafe import ClientSafe
except ImportError:
    from doubledecker.clientSafe import ClientSafe
from .domain_info import DomainInfo
from .sql.domains_info import DomainInformation
from .sql.domain import Domain
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
        try:
            domain = src.decode("utf-8")
            domain_ip = domain.split(':')[0]
            domain_port = domain.split(':')[1]

            domain_info = json.loads(msg.decode("utf-8"))
            
            # domain info
            di = DomainInfo()
            di.parseDict(domain_info)
            
            domain_id = Domain().addDomain(di.name, di.type, domain_ip, domain_port)
            di.domain_id = domain_id
                     
            logging.debug("Domain information arrived from %s: %s" % (domain , json.dumps(domain_info)))
            DomainInformation().add_domain_info(di)
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
