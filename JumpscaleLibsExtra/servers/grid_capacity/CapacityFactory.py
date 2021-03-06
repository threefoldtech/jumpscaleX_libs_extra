import requests
import os

from Jumpscale import j

from .CapacityServer import CapacityServer

JSConfigBase = j.baseclasses.object_config_collection


class CapacityFactory(JSConfigBase):
    __jslocation__ = "j.servers.capacity"

    def start(self, instance="main", background=False):
        server = self.get(instance, interactive=False)

        if background:
            cmd = "kosmos '%s.start(instance=\"%s\")'" % (self.__jslocation__, instance)  # IGNORELOCATION
            j.servers.tmux.execute(
                cmd, session="capacity_server", window=instance, pane="main", session_reset=False, window_reset=True
            )
            res = j.sal.nettools.waitConnectionTest("localhost", int(server.config.data["port"]), timeout=1000)
            if res == False:
                raise j.exceptions.Base("Could not start capacity server on port:%s" % int(server.config.data["port"]))
        else:
            server.start()
