from vumi_http_proxy.servicemaker import (
    Options, ProxyWorkerServiceMaker, client)
from vumi_http_proxy import http_proxy
from twisted.trial import unittest
from vumi_http_proxy.test import helpers
import yaml


class TestOptions(unittest.TestCase):
    def test_defaults(self):
        options = Options()
        options.parseOptions([])
        self.assertEqual(options["port"], 8080)
        self.assertEqual(options["interface"], "0.0.0.0")
        self.assertEqual(options["configfile"], None)

    def test_override(self):
        options = Options()
        fake_blacklist = ["foo", "bar"]
        fake_dnsservers = [['8.8.8.8', 53], ['8.8.4.4', 53]]
        filename = self.make_config(fake_blacklist, fake_dnsservers)
        options.parseOptions(["--port", 8000])
        options.parseOptions(["--interface", '127.0.0.1'])
        options.parseOptions(["--configfile", filename])
        self.assertEqual(options["port"], 8000)
        self.assertEqual(str(options["interface"]), "127.0.0.1")
        self.assertEqual(str(options["configfile"]), filename)

    def make_config(self, blacklist, dnsservers):
        filename = self.mktemp()
        filecont = yaml.safe_dump(
            {"proxy-blacklist": blacklist, "dns-servers": dnsservers})
        with open(filename, 'w') as stream:
            stream.write(filecont)
        return filename


class TestProxyWorkerServiceMaker(unittest.TestCase):
    def test_makeService(self):
        options = Options()
        options.parseOptions([])
        self.patch(client, 'createResolver', lambda: helpers.TestResolver())
        servicemaker = ProxyWorkerServiceMaker()
        service = servicemaker.makeService(options)
        self.assertTrue(isinstance(service.factory, http_proxy.ProxyFactory))
        self.assertEqual(service.endpoint._interface, '0.0.0.0')
        self.assertEqual(service.endpoint._port, 8080)
