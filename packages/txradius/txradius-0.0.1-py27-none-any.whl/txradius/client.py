#!/usr/bin/env python
# coding=utf-8

from twisted.python import log
from twisted.internet import protocol
from twisted.internet import reactor, defer
from txradius.radius import packet
from txradius import message
import six
import time


class RadiusClient(protocol.DatagramProtocol):
    def __init__(self, secret, dictionary, server, authport=1812, acctport=1813,  debug=False):
        self.dict = dictionary
        self.secret = six.b(secret)
        self.server = server
        self.authport = authport
        self.acctport = acctport
        self.debug = debug
        reactor.listenUDP(0, self)

    def close(self):
        self.transport = None
        self.port.stopListening()

    def onError(self, err):
        log.err('Packet process error：%s' % str(err))

    def onResult(self, resp):
        reactor.callLater(0.01, self.close,)
        return resp

    def sendAuth(self, **kwargs):
        User_Password = kwargs.pop("User-Password",None)
        CHAP_Password = kwargs.pop("CHAP-Password",None)
        request = message.AuthMessage(dict=self.dict, secret=self.secret, **kwargs)
        if User_Password:
            request['User-Password'] = request.PwCrypt(User_Password)
        if CHAP_Password:
            request['CHAP-Password'] = request.ChapEcrypt(CHAP_Password)

        if self.debug:
            log.msg("Send radius Request: %s" % (request.format_str()))
        self.transport.write(request.RequestPacket(), (self.server, self.authport))
        self.deferrd = defer.Deferred()
        self.deferrd.addCallbacks(self.onResult,self.onError)
        return self.deferrd

    def sendAcct(self, **kwargs):
        request = message.AcctMessage(dict=self.dict, secret=self.secret, **kwargs)
        if self.debug:
            log.msg("Send radius Request: %s" % (request.format_str()))
        self.transport.write(request.RequestPacket(), (self.server, self.acctport))
        self.deferrd = defer.Deferred()
        self.deferrd.addCallbacks(self.onResult,self.onError)
        return self.deferrd

    def datagramReceived(self, datagram, (host, port)):
        try:
            response = packet.Packet(packet=datagram)
            if self.debug:
                log.msg("Received Radius Response: %s" % (message.format_packet_str(response)))
            self.deferrd.callback(response)
        except Exception as err:
            log.err('Invalid Response packet from %s: %s' % ((host, port), str(err)))
            self.deferrd.errback(response)


def send_auth(secret, dictionary, server, authport=1812, acctport=1813, debug=False, **kwargs):
    return RadiusClient(secret, dictionary, server, authport, acctport, debug).sendAuth(**kwargs)

def send_acct(secret, dictionary, server, authport=1812, acctport=1813, debug=False, **kwargs):
    return RadiusClient(secret, dictionary, server, authport, acctport, debug).sendAcct(**kwargs)









