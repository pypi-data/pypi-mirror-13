'''
Logentries Status plugin for buildbot

This plugin sends a subset of status updates to the Logentries service.

Usage:

    import logentries
    c['status'].append(logentries.LogentriesStatusPush(api_token="da45d4be-e1e7-4de3-9861-45bdab564cb3", endpoint="data.logentries.com", port=10000))

If you want SSL

    import logentries
    c['status'].append(logentries.LogentriesStatusPush(api_token="da45d4be-e1e7-4de3-9861-45bdab564cb3", endpoint="data.logentries.com", port=20000, tls=True))
'''

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor, ssl
from sys import stdout


from buildbot.status.base import StatusReceiverMultiService
from buildbot.status.builder import Results, SUCCESS
import codecs


def _to_unicode(ch):
    return codecs.unicode_escape_decode(ch)[0]


def _is_unicode(ch):
    return isinstance(ch, unicode)


def _create_unicode(ch):
    return unicode(ch, 'utf-8')


class PlainTextAppender(Protocol):
    def __init__(self):
        self.LINE_SEP = _to_unicode(r'\u2028')

    def put(self, token, msg):
        if not _is_unicode(msg):
            multiline = _create_unicode(msg).replace('\n', self.LINE_SEP)
        else:
            multiline = msg.replace('\n', self.LINE_SEP)
        multiline += "\n"
        self.transport.write("{0} {1}".format(token, multiline.encode('utf-8')))


class PlainTextAppenderFactory(ReconnectingClientFactory):
    def __init__(self, token):
        self.token = token

    def startedConnecting(self, connector):
        print 'Started to connect to Logentries'

    def buildProtocol(self, addr):
        print 'Connected to Logentries. {}'.format(addr)
        self.p = PlainTextAppender()
        return self.p

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection to Logentries.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def put(self, msg):
        self.p.put(self.token, msg)


class LogentriesStatusPush(StatusReceiverMultiService):

    def __init__(self, api_token, localhost_replace=False, endpoint='data.logentries.com', port=10000, tls=False, **kwargs):
        StatusReceiverMultiService.__init__(self)

        self.api_token = api_token
        self.localhost_replace = localhost_replace
        self.endpoint = endpoint
        self.port = port
        self.tls = tls

        self.f = PlainTextAppenderFactory(token=api_token)
        if tls:
            self.r = reactor.connectSSL(endpoint, port, self.f, ssl.ClientContextFactory())
        else:
            self.r = reactor.connectTCP(endpoint, port, self.f)

    def sendNotification(self, message):
        self.r.reactor.callLater(1, self.f.put, message)

    def setServiceParent(self, parent):
        StatusReceiverMultiService.setServiceParent(self, parent)
        self.master_status = self.parent
        self.master_status.subscribe(self)
        self.master = self.master_status.master

    def disownServiceParent(self):
        self.master_status.unsubscribe(self)
        self.master_status = None
        for w in self.watched:
            w.unsubscribe(self)
        return StatusReceiverMultiService.disownServiceParent(self)

    def builderAdded(self, name, builder):
        return self  # subscribe to this builder

    def buildFinished(self, builderName, build, result):
        url = self.master_status.getURLForThing(build)
        if self.localhost_replace:
            url = url.replace("//localhost", "//%s" % self.localhost_replace)

        reason = build.getReason()

        message = "url=%s buildername=%s result=%s reason='%s'" % (
            url, builderName, Results[result].upper(), reason)

        self.sendNotification(message)

    def buildStarted(self, builderName, build):
        url = self.master_status.getURLForThing(build)
        if self.localhost_replace:
            url = url.replace("//localhost", "//%s" % self.localhost_replace)

        reason = build.getReason()

        message = "url=%s buildername=%s result=STARTED reason='%s'" % (
            url, builderName, reason)

        self.sendNotification(message)
