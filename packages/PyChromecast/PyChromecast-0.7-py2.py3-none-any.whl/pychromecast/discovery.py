"""Discovers Chromecasts on the network using mDNS/zeroconf."""
import time
from uuid import UUID

import six
from zeroconf import ServiceBrowser, Zeroconf

DISCOVER_TIMEOUT = 5


class CastListener(object):
    """Zeroconf Cast Services collection."""
    def __init__(self):
        self.services = {}

    @property
    def count(self):
        """Number of discovered cast services."""
        return len(self.services)

    @property
    def devices(self):
        """List of tuples (ip, host) for each discovered device."""
        return list(self.services.values())

    # pylint: disable=unused-argument
    def remove_service(self, zconf, typ, name):
        """ Remove a service from the collection. """
        self.services.pop(name, None)

    def add_service(self, zconf, typ, name):
        """ Add a service to the collection. """
        service = None
        tries = 0
        while service is None and tries < 4:
            try:
                service = zconf.get_service_info(typ, name)
            except IOError:
                # If the zerconf fails to receive the necesarry data we abort
                # adding the service
                break
            tries += 1

        if service:
            ips = zconf.cache.entries_with_name(service.server.lower())
            host = repr(ips[0]) if ips else service.server
            model_name = service.properties.get('md')
            if not isinstance(model_name, six.text_type):
                model_name = model_name.decode('utf-8')
            uuid = service.properties.get('id')
            if uuid:
                uuid = UUID(uuid)
            friendly_name = service.properties.get('fn')
            if not isinstance(friendly_name, six.text_type):
                friendly_name = friendly_name.decode('utf-8')

            self.services[name] = (host, service.port, uuid, model_name,
                                   friendly_name)


def discover_chromecasts(max_devices=None, timeout=DISCOVER_TIMEOUT):
    """ Discover chromecasts on the network. """
    try:
        zconf = Zeroconf()
        listener = CastListener()
        browser = ServiceBrowser(zconf, "_googlecast._tcp.local.", listener)

        if max_devices is None:
            time.sleep(timeout)
            return listener.devices

        else:
            start = time.time()

            while (time.time() - start < timeout and
                   listener.count < max_devices):
                time.sleep(.1)

            return listener.devices
    finally:
        browser.cancel()
        zconf.close()
