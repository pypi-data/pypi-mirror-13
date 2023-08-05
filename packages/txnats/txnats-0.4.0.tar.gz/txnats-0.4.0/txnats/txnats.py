from sys import stdout
import logging
import json
from io import BytesIO
from io import BufferedReader
from collections import namedtuple

from twisted.python import log

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet import error

from . import _meta

LANG = "py.twisted"
CLIENT_NAME = "xnats"


ServerInfo = namedtuple(
    "ServerInfo",
    (
        "server_id",
        "version",
        "go",
        "host",
        "port",
        "auth_required",
        "ssl_required",
        "tls_required",
        "tls_verify",
        "max_payload",
    ))


DISCONNECTED = 0
CONNECTED = 1


class NatsError(Exception):
    "Nats Error"


class NatsProtocol(Protocol):
    server_settings = None

    def __init__(self, own_reactor=None, verbose=True, pedantic=False,
                 ssl_required=False, auth_token=None, user="",
                 password="", on_msg=None, on_connect=None):
        """

        @param own_reactor: A Twisted Reactor, defaults to standard. Chiefly
         customizable for testing.
        @param verbose: Turns on +OK protocol acknowledgements.
        @param pedantic: Turns on additional strict format checking, e.g.
         for properly formed subjects
        @param ssl_required: Indicates whether the client requires
         an SSL connection.
        @param auth_token: Client authorization token
        @param user: Connection username (if auth_required is set)
        @param pass: Connection password (if auth_required is set)
        @param on_msg: Handler for messages for subscriptions that don't have
         their own on_msg handler. Default behavior is to write to stdout.
         A callable that takes the following params:
             @param nats_protocol: An instance of NatsProtocol.
             @param sid: A unique alphanumeric subscription ID.
             @param subject: A valid NATS subject.
             @param reply_to: The reply to.
             @param payload: Bytes of the payload.
        @param on_connect: Callable that takes this instance of NatsProtocol
         which will be called upon the first successful connection.
        """
        self.reactor = own_reactor if own_reactor else reactor
        self.status = DISCONNECTED
        self.verbose = verbose
        # Set the number of PING sent out
        self.pout = 0
        self.remaining_bytes = b''

        self.client_info = {
            "verbose": verbose,
            "pedantic": pedantic,
            "ssl_required": ssl_required,
            "auth_token": auth_token,
            "user": user,
            "pass": password,
            "name": CLIENT_NAME,
            "lang": LANG,
            "version": _meta.version,
        }
        if on_msg:
            # Ensure the on_msg signature fits.
            on_msg(nats_protocol=self, sid=0, subject=b"test-subject",
                   reply_to=b'', payload=b'hello, world')
        self.on_msg = on_msg
        self.on_connect_d = defer.Deferred()
        if on_connect:
            self.on_connect_d.addCallback(on_connect)
        self.sids = {}

    def connectionLost(self, reason=connectionDone):
        """Called when the connection is shut down.

        Clear any circular references here, and any external references
        to this Protocol.  The connection has been closed.

        Clear left over remaining bytes because they won't be continued
        properly upon reconnection.

        @type reason: L{twisted.python.failure.Failure}
        """
        self.status = DISCONNECTED
        self.remaining_bytes = b''
        if reason == error.ConnectionLost:
            log.msg("Connection Lost")
            pass
        # TODO: add reconnect
        # TODO: add resubscribe

    def dataReceived(self, data):
        """
        Parse the NATS.io protocol from chunks of data streaming from
        the connected gnatsd.

        The server settings will be set and connect will be sent with this
        client's info upon an INFO, which should happen when the
        transport connects.

        Registered message callback functions will be called with MSGs
        once parsed.

        PONG will be called upon a ping.

        An exception will be raised upon an ERR from gnatsd.

        An +OK doesn't do anything.
        """
        if self.remaining_bytes:
            data = self.remaining_bytes + data
            self.remaining_bytes = b''

        data_buf = BufferedReader(BytesIO(data))
        while True:
            command = data_buf.read(4)
            if command == b"-ERR":
                raise NatsError(data_buf.read())
            elif command == b"+OK\r":
                val = data_buf.read(1)
                if val != b'\n':
                    self.remaining_bytes += command
                    break
            elif command == "MSG ":
                val = data_buf.readline()
                if not val:
                    self.remaining_bytes += command
                    break
                if not val.endswith(b'\r\n'):
                    self.remaining_bytes += command + val
                    break

                meta_data = val.split(" ")
                n_bytes = int(meta_data[-1])
                subject = meta_data[0]
                if len(meta_data) == 4:
                    reply_to = meta_data[2]
                elif len(meta_data) == 3:
                    reply_to = None
                else:
                    self.remaining_bytes += command + val
                    break

                sid = meta_data[1]

                if sid in self.sids:
                    on_msg = self.sids[sid]
                else:
                    on_msg = self.on_msg

                payload = data_buf.read(n_bytes)
                if len(payload) != n_bytes:
                    self.remaining_bytes += command + val + payload
                    break

                if on_msg:
                    on_msg(nats_protocol=self, sid=sid, subject=subject,
                           reply_to=reply_to, payload=payload)
                else:
                    stdout.write(command)
                    stdout.write(val)
                    stdout.write(payload)

                payload_post = data_buf.readline()
                if payload_post != b'\r\n':
                    self.remaining_bytes += (command + val + payload
                                             + payload_post)
                    break
            elif command == "PING":
                self.pong()
                val = data_buf.readline()
                if val != b'\r\n':
                    self.remaining_bytes += command + val
                    break
            elif command == "PONG":
                self.pout -= 1
                val = data_buf.readline()
                if val != b'\r\n':
                    self.remaining_bytes += command + val
                    break
            elif command == "INFO":
                val = data_buf.readline()
                if not val.endswith(b'\r\n'):
                    self.remaining_bytes += command + val
                    break
                settings = json.loads(val)
                self.server_settings = ServerInfo(**settings)
                log.msg(json.dumps(settings), separators=(',', ':'))
                self.status = CONNECTED
                self.connect()
                if self.on_connect_d:
                    self.on_connect_d.callback(self)
                    self.on_connect_d = None
            else:
                log.msg("Not handled command is: {!r}".format(command),
                        logLevel=logging.DEBUG)
                val = data_buf.read()
                self.remaining_bytes += command + val
            if not data_buf.peek(1):
                log.msg("emptied data",
                        logLevel=logging.DEBUG)
                break

    def connect(self):
        """
        Tell the NATS server about this client and it's options.
        """
        payload = b'CONNECT {}\r\n'.format(json.dumps(
            self.client_info, separators=(',', ':')))

        log.msg(payload, logLevel=logging.DEBUG)
        self.transport.write(payload)

    def pub(self, subject,  payload, reply_to=""):
        """
        Publish a payload of bytes to a subject.

        @param subject: The destination subject to publish to.
        @param reply_to: The reply inbox subject that subscribers can use
         to send a response back to the publisher/requestor.
        @param payload: The message payload data, in bytes.
        """
        reply_part = b""
        if reply_to:
            reply_part = b"{} ".format(reply_to)

        # TODO: deal with the payload if it is bigger than the server max.
        op = b"PUB {} {}{}\r\n{}\r\n".format(
            subject, reply_part, len(payload), payload)
        self.transport.write(op)

    def sub(self, subject, sid, queue_group=None, on_msg=None):
        """
        Subscribe to a subject.

        @param subject: The subject name to subscribe to.
        @param sid: A unique alphanumeric subscription ID.
        @param queue_group: If specified, the subscriber will
         join this queue group.
         @param on_msg: A callable that takes the following params:
             @param nats_protocol: An instance of NatsProtocol.
             @param sid: A unique alphanumeric subscription ID.
             @param subject: A valid NATS subject.
             @param reply_to: The reply to.
             @param payload: Bytes of the payload.
        """
        self.sids[b"{}".format(sid)] = on_msg

        queue_group_part = b""
        if queue_group:
            queue_group_part = b"{} ".format(queue_group)

        op = b"SUB {} {}{}\r\n".format(subject, queue_group_part, sid)
        self.transport.write(op)

    def unsub(self, sid, max_msgs=None):
        """
        Unsubcribes the connection from the specified subject,
        or auto-unsubscribes after the specified
        number of messages has been received.

        @param sid: The unique alphanumeric subscription ID of
         the subject to unsubscribe from.
        @type sid: int
        @param max_msgs: Optional number of messages to wait for before
         automatically unsubscribing.
        @type sid: int
        """
        max_msgs_part = b""
        if max_msgs:
            max_msgs_part = b"{}".format(max_msgs)

        op = b"UNSUB {} {}\r\n".format(sid, max_msgs_part)
        self.transport.write(op)

    def ping(self):
        """
        Send ping.
        """
        op = b"PING\r\n"
        self.transport.write(op)
        self.pout += 1

    def pong(self):
        """
        Send pong.
        """
        op = b"PONG\r\n"
        self.transport.write(op)

    def request(self, sid, subject):
        """
        Make a synchronous request for a subject.

        Make a reply to.
        Subscribe to the subject.
        Make a Deferred and add it to the inbox under the reply to.
        Do auto unsubscribe for one message.
        """
        raise NotImplementedError()


