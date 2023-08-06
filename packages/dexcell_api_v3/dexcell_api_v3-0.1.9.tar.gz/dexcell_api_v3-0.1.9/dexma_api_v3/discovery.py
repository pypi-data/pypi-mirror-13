__author__ = 'dcortes'

import sys

from repositories.repository_readings import RepositoryReadings
from repositories.repository_device import RepositoryDevice as RepositoryDevices
from repositories.repository_location import RepositoryLocation as RepositoryLocations


def change_underscore_to_uppercase(service_name):
    services = service_name.split("_")
    return "Repository{}".format(''.join([service.capitalize() for service in services]))


def service_to_class(service):
    return getattr(sys.modules[__name__], service)


def build(service_name, token, endpoint="http://api.dexcell.com/v3"):
    service = change_underscore_to_uppercase(service_name)
    service_class = service_to_class(service)
    return service_class(endpoint, token)