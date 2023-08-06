from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.endpoints import clientFromString, serverFromString
from twisted.web.client import ProxyAgent, readBody
from twisted.trial import unittest
from vumi_http_proxy.http_proxy import ProxyFactory
from vumi_http_proxy.test import helpers


class TestCheckProxyRequest(unittest.TestCase):
    timeout = helpers.DEFAULT_TIMEOUT

    def setUp(self):
        self.server = helpers.HttpTestServer(self)

    @inlineCallbacks
    def setup_proxy(self, blacklist):
        resolver = helpers.TestResolver()
        http_client = helpers.TestAgent()
        proxy = ProxyFactory(blacklist, resolver, http_client)
        server_endpoint = serverFromString(
            reactor, "tcp:0:interface=127.0.0.1")
        self.server = yield server_endpoint.listen(proxy)
        self.addCleanup(self.server.stopListening)
        returnValue(self.server.getHost().port)

    @inlineCallbacks
    def make_request(self, proxy_port, url):
        client_endpoint = clientFromString(
            reactor, "tcp:host=localhost:port=%s" % (proxy_port,))
        agent = ProxyAgent(client_endpoint)
        response = yield agent.request("GET", url)
        body = yield readBody(response)
        returnValue((response, body))

    @inlineCallbacks
    def check_proxy_request(self, blacklist, ip, expected_code, expected_body):
        http_port = yield self.server.start()
        proxy_port = yield self.setup_proxy(blacklist)
        url = 'http://%s:%s/' % (ip, http_port,)
        response, body = yield self.make_request(proxy_port, url)
        self.assertEqual(response.code, expected_code)
        self.assertEqual(body, expected_body)

    def test_bad_ip(self):
        return self.check_proxy_request(
            ['69.16.230.117'], '', 400,
            "<html>ERROR: No IP adresses found for name '' </html>")

    def test_deny_ip(self):
        return self.check_proxy_request(
            ['69.16.230.117'], 'zombo.com', 400, "<html>Denied</html>")

    def test_allow_ip(self):
        return self.check_proxy_request(
            ['69.16.230.117'], 'zombie.com', 200, '<html>Allowed</html>')
