from twisted.internet.protocol import DatagramProtocol
from opencanary.modules import CanaryService

EVENT_NAME = "{{ pkgname }} Incident"

class {{ pkgname }}(DatagramProtocol, CanaryService):
    NAME = '{{ name }}'

    def datagramReceived(self, data, (host, port)):
        logdata = {
            'DESCRIPTION': EVENT_NAME,
            'DATA': data
        }
        self.log(
            logdata,
            src_host=host,
            src_port=port
        )
        self.transport.write(data, (host, port))

    def __init__(self, config=None, logger=None):
        CanaryService.__init__(self, config=config, logger=logger)
        self.port = config.getVal('{{ name }}.port', 8008)
        self.logtype = logger.LOG_USER_1
