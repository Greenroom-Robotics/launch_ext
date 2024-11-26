import psutil
import socket
from launch.substitution import Substitution
import launch.logging

class ResolveHost(Substitution):
    def __init__(self, host: str):
        self.__host = host
        self.__logger = launch.logging.get_logger('launch.user')

    def perform(self, context):
        interfaces = psutil.net_if_addrs()
        if self.__host in interfaces:
            interface = interfaces[self.__host][0]
            ip = interface.address
        else:
            ip = socket.gethostbyname(self.__host)
        self.__logger.info(f"Resolved {self.__host} to {ip}")
        return ip

    def describe(self):
        return 'ResolveHost(interface={})'.format(self.__node_level.describe())

    def describe_condition(self, condition):
        return self.describe()
