#!/usr/bin/env python

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import strports
from twisted.names import client
from twisted.web.client import Agent
from twisted.internet import reactor
from vumi_http_proxy.http_proxy import ProxyFactory
from vumi_http_proxy import config_reader


class Options(usage.Options):
    optParameters = [["port", None, "8080",
                     "The port number to start the proxy"],
                     ["interface", None, "0.0.0.0", "IP to start proxy on"],
                     ["configfile", None, None,
                     "Name of the YAML config file for blacklist and servers"]]

    def postOptions(self):
        try:
            self["port"] = int(self["port"])
        except (ValueError, TypeError):
            raise usage.UsageError('Port must be an integer. Please try again')


class ProxyWorkerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "vumi_http_proxy"
    description = "Service maker to launch proxy from given port and ip addr"
    options = Options

    def makeService(self, options):
        blacklist = config_reader.read_config(options["configfile"])
        factory = ProxyFactory(
            blacklist, client.createResolver(), Agent(reactor))
        return strports.service("tcp:%d:interface=%s" % (
                options["port"], options["interface"]), factory)
