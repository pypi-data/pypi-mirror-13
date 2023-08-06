#!/usr/bin/env python
from click.testing import CliRunner
from vumi_http_proxy import queen_of_ni, http_proxy
from twisted.trial import unittest
import yaml


class TestQueenOfNi(unittest.TestCase):
    def test_queen_of_ni(self):
        runner = CliRunner()
        self.initializers = []
        self.patch(http_proxy.Initialize, 'main',
                   lambda x: self.initializers.append(x))
        fake_blacklist = ["foo", "bar"]
        fake_dnsservers = [['8.8.8.8', 53], ['8.8.4.4', 53]]
        filename = self.make_config(fake_blacklist, fake_dnsservers)
        result = runner.invoke(queen_of_ni.cli, ['--configfile', filename])
        self.assertEqual(result.exception, None)
        self.assertEqual(result.output.splitlines(), [
           'Starting connection to 0.0.0.0:8080',
        ])
        self.assertEqual(result.exit_code, 0)

        [initializer] = self.initializers
        self.assertEquals(type(initializer), http_proxy.Initialize)
        self.assertEquals(initializer.port, 8080)
        self.assertEquals(initializer.ip, "0.0.0.0")
        self.assertEquals(initializer.blacklist, ["foo", "bar"])
        self.assertEquals(
            initializer.dnsservers, [('8.8.8.8', 53), ('8.8.4.4', 53)])

    def make_config(self, blacklist, dnsservers):
        filename = self.mktemp()
        filecont = yaml.safe_dump(
            {"proxy-blacklist": blacklist, "dns-servers": dnsservers})
        with open(filename, 'w') as stream:
            stream.write(filecont)
        return filename
