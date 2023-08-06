from twisted.python import log
from twisted.web import http, proxy
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.names import client
from twisted.web.client import Agent, readBody
from urlparse import urlparse, urlunparse
from twisted.internet.defer import inlineCallbacks, succeed
# blacklist of disallowed domains (move to proxy_blacklist.py)


class ProxyFactory(http.HTTPFactory):

    def __init__(self, blacklist, resolver, http_client):
        http.HTTPFactory.__init__(self)
        self.blacklist = blacklist
        self.resolver = resolver
        self.http_client = http_client

    def buildProtocol(self, addr):
        return Proxy(self.blacklist, self.resolver, self.http_client)


class CheckProxyRequest(proxy.ProxyRequest):
    def process(self):
        host, _, port = self.getAllHeaders()['host'].partition(':')
        d = self.channel.resolver.getHostByName(host)
        d.addCallback(self.setIP, host)
        d.addErrback(self.handleError)
        return d

    def handleError(self, failure):
        log.err(failure)
        self.setResponseCode(400)
        self.write("<html>Denied</html>")
        self.finish()
        return

    def setIP(self, ip_addr, host):
        if not ip_addr:
            self.setResponseCode(400)
            self.write("<html>ERROR: No IP adresses found for name %r" %
                       host + " </html>")
            self.finish()
            return
        if ip_addr in self.channel.blacklist:
            self.setResponseCode(400)
            self.write("<html>Denied</html>")
            self.finish()
            return
        uri = self.replaceHostWithIP(self.uri, ip_addr)
        headers = self.requestHeaders
        d = self.channel.http_client.request(
            self.method, uri, headers, StringProducer(self.content.read()))
        d.addCallback(self.sendResponseBack)
        return d

    def replaceHostWithIP(self, uri, ip_addr):
        scheme, netloc, path, params, query, fragment = urlparse(uri)
        _, _, port = netloc.partition(':')
        if port:
            ip_addr = "%s:%s" % (ip_addr, port)
        return urlunparse((scheme, ip_addr, path, params, query, fragment))

    @inlineCallbacks
    def sendResponseBack(self, r):
        self.setResponseCode(r.code)
        for key, value in r.headers.getAllRawHeaders():
            self.responseHeaders.addRawHeader(key, value)
        body = yield readBody(r)
        self.write(body)
        self.finish()


class StringProducer(object):
    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class Proxy(proxy.Proxy):

    requestFactory = CheckProxyRequest

    def __init__(self, blacklist, resolver, http_client):
        proxy.Proxy.__init__(self)
        self.blacklist = blacklist
        self.resolver = resolver
        self.http_client = http_client


class Initialize(object):
    def __init__(self, blacklist, ip, port):
        self.blacklist = blacklist
        self.ip = ip
        self.port = port

    def main(self):
        resolver = client.createResolver()
        http_client = Agent(reactor)
        factory = ProxyFactory(self.blacklist, resolver, http_client)
        endpoint = serverFromString(
            reactor, "tcp:%d:interface=%s" % (self.port, self.ip))
        endpoint.listen(factory)
        reactor.run()
