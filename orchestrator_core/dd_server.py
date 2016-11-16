try:
    from .doubledecker.clientSafe import ClientSafe
except ImportError:
    from doubledecker.clientSafe import ClientSafe

import json
import logging
from .domain_info import DomainInfo, HardwareInfo
from .sql.domain import Domain
from .sql.domains_info import DomainInformation


class DD_Server(ClientSafe):
    def __init__(self, name, dealerurl, customer, keyfile):
        super().__init__(name, dealerurl, customer, keyfile)

    def on_data(self, dest, msg):
        print(dest, " sent", msg)

    def on_pub(self, src, topic, msg):
        # when a new domain information is published, it is parsed and stored on db
        msgstr = "PUB %s from %s: %s" % (str(topic), str(src), str(msg))
        print(msgstr)
        #TODO: validation of msg needed
        try:
            source = src.decode("utf-8")
            #domain_ip = domain.split(':')[0]
            #domain_port = domain.split(':')[1]

            domain_info = json.loads(msg.decode("utf-8"))

            # domain info
            di = DomainInfo()
            di.parse_dict(domain_info)
            domain_id = Domain().addDomain(di.name, di.type, di.domain_ip, di.domain_port)
            di.domain_id = domain_id
            logging.debug("Domain information arrived from %s: %s" % (source, json.dumps(domain_info)))
            DomainInformation().add_domain_info(di)
        except Exception as ex:
            logging.exception(ex)

    def on_reg(self):
        self.subscribe("frog:domain-description", "/0/0/0/")

    def on_discon(self):
        pass

    def unsubscribe(self, topic, scope):
        pass

    def on_error(self, topic, scope):
        pass

    def on_cli(self, dummy, other_dummy):
        pass
