#!/usr/bin/env python
from click.testing import CliRunner
from vumi_http_proxy import queen_of_ni, http_proxy
from twisted.trial import unittest


class TestQueenOfNi(unittest.TestCase):
    def test_queen_of_ni(self):
        runner = CliRunner()
        self.initializers = []
        self.patch(http_proxy.Initialize, 'main',
                   lambda x: self.initializers.append(x))
        fake_blacklist = ["foo", "bar"]
        filename = self.make_blacklist(fake_blacklist)
        result = runner.invoke(queen_of_ni.cli, ['--blacklist', filename])
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

    def make_blacklist(self, blacklist):
        filename = self.mktemp()
        with open(filename, 'w') as stream:
            stream.write("proxy-blacklist:\n")
            for ip_addr in blacklist:
                stream.write(" - " + ip_addr + "\n")
        return filename
