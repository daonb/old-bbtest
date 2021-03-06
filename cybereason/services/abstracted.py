
"""
"""

from cybereason.services.ecosystem import logger

from cybereason.boxes.servers import PerspectiveBox


class CRService(object):
    pass


class EpLogger(CRService):
    pass


class EpMessages(CRService):
    pass


class SensorPolicy(CRService):
    """ Service to configure Sensor Policy on the Transparency.

    Configuration can be performed via: Perspective, direct access to Transparency, TBD way of transparency Mock...
    """

    def __init__(self, server):
        """
        :param server: Perspective or transparency object
        """
        self.server = server

    def config(self, configuration):
        if type(self.server) == PerspectiveBox:
            logger.info('config sensor policy')
        else:
            raise NotImplementedError(f'SensorPolicy server does not support {self.server.NAME} server')
