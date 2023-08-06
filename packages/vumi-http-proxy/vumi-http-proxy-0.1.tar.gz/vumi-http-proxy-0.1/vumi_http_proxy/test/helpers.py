from twisted.web import server, resource
from twisted.web.client import ResponseDone
from twisted.web.http_headers import Headers
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, succeed
from twisted.internet.endpoints import serverFromString
from twisted.python.failure import Failure

DEFAULT_TIMEOUT = 2

hostnames = {
    'zombo.com': '69.16.230.117',
    'zombie.com': '66.96.162.142'
}


class HttpTestResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html>Allowed</html>"


class HttpTestServer(object):
    def __init__(self, testcase):
        self.site = server.Site(HttpTestResource())
        self.server = None
        testcase.addCleanup(self.cleanup)

    @inlineCallbacks
    def start(self):
        server_endpoint = serverFromString(
            reactor, "tcp:0:interface=127.0.0.1")
        self.server = yield server_endpoint.listen(self.site)
        returnValue(self.server.getHost().port)

    @inlineCallbacks
    def cleanup(self):
        if self.server is not None:
            yield self.server.stopListening()


class TestResolver(object):
    def __init__(self):
        self.hostnames = hostnames

    def getHostByName(self, name, timeout=None, effort=10):
        ip = self.hostnames.get(name)
        return succeed(ip)


class MockResponse(object):
    def __init__(self, code, response_string):
        self.code = code
        self.phrase = "OK"
        self.headers = Headers()
        self.response_string = response_string

    def deliverBody(self, protocol):
        protocol.dataReceived(self.response_string)
        protocol.connectionLost(
            Failure(ResponseDone(u"All Happy")))


class TestAgent(object):
    def request(self, method, uri, headers, bodyProducer):
        response = MockResponse(200, "<html>Allowed</html>")
        return succeed(response)
