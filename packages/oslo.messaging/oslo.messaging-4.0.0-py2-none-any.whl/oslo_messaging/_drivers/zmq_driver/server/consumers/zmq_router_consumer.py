#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from oslo_messaging._drivers import base
from oslo_messaging._drivers.zmq_driver.server.consumers\
    import zmq_consumer_base
from oslo_messaging._drivers.zmq_driver.server import zmq_incoming_message
from oslo_messaging._drivers.zmq_driver import zmq_address
from oslo_messaging._drivers.zmq_driver import zmq_async
from oslo_messaging._drivers.zmq_driver import zmq_names
from oslo_messaging._i18n import _LE

LOG = logging.getLogger(__name__)

zmq = zmq_async.import_zmq()


class RouterIncomingMessage(base.IncomingMessage):

    def __init__(self, listener, context, message, socket, reply_id, msg_id,
                 poller):
        super(RouterIncomingMessage, self).__init__(listener, context, message)
        self.socket = socket
        self.reply_id = reply_id
        self.msg_id = msg_id
        self.message = message
        poller.resume_polling(socket)

    def reply(self, reply=None, failure=None, log_failure=True):
        """Reply is not needed for non-call messages"""

    def acknowledge(self):
        LOG.debug("Not sending acknowledge for %s", self.msg_id)

    def requeue(self):
        """Requeue is not supported"""


class RouterConsumer(zmq_consumer_base.SingleSocketConsumer):

    def __init__(self, conf, poller, server):
        super(RouterConsumer, self).__init__(conf, poller, server, zmq.ROUTER)
        self.matchmaker = server.matchmaker
        self.targets = []
        self.host = zmq_address.combine_address(self.conf.rpc_zmq_host,
                                                self.port)
        LOG.info("[%s] Run ROUTER consumer" % self.host)

    def listen(self, target):

        LOG.info("[%s] Listen to target %s" % (self.host, target))

        self.targets.append(target)
        self.matchmaker.register(target, self.host,
                                 zmq_names.socket_type_str(zmq.ROUTER))

    def cleanup(self):
        super(RouterConsumer, self).cleanup()
        for target in self.targets:
            self.matchmaker.unregister(target, self.host,
                                       zmq_names.socket_type_str(zmq.ROUTER))

    def _receive_request(self, socket):
        reply_id = socket.recv()
        empty = socket.recv()
        assert empty == b'', 'Bad format: empty delimiter expected'
        request = socket.recv_pyobj()
        return request, reply_id

    def receive_message(self, socket):
        try:
            request, reply_id = self._receive_request(socket)
            LOG.debug("[%(host)s] Received %(type)s, %(id)s, %(target)s"
                      % {"host": self.host,
                         "type": request.msg_type,
                         "id": request.message_id,
                         "target": request.target})

            if request.msg_type == zmq_names.CALL_TYPE:
                return zmq_incoming_message.ZmqIncomingRequest(
                    self.server, socket, reply_id, request, self.poller)
            elif request.msg_type in zmq_names.NON_BLOCKING_TYPES:
                return RouterIncomingMessage(
                    self.server, request.context, request.message, socket,
                    reply_id, request.message_id, self.poller)
            else:
                LOG.error(_LE("Unknown message type: %s") % request.msg_type)

        except zmq.ZMQError as e:
            LOG.error(_LE("Receiving message failed: %s") % str(e))


class RouterConsumerBroker(RouterConsumer):

    def __init__(self, conf, poller, server):
        super(RouterConsumerBroker, self).__init__(conf, poller, server)

    def _receive_request(self, socket):
        reply_id = socket.recv()
        empty = socket.recv()
        assert empty == b'', 'Bad format: empty delimiter expected'
        envelope = socket.recv_pyobj()
        request = socket.recv_pyobj()

        if zmq_names.FIELD_REPLY_ID in envelope:
            request.proxy_reply_id = envelope[zmq_names.FIELD_REPLY_ID]
        return request, reply_id
