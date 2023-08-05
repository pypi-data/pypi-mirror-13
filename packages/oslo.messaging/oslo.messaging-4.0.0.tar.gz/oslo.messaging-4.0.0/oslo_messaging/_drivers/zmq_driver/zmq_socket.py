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

from oslo_messaging._drivers.zmq_driver import zmq_address
from oslo_messaging._drivers.zmq_driver import zmq_async
from oslo_messaging._drivers.zmq_driver import zmq_names
from oslo_messaging._i18n import _LE
from oslo_messaging import exceptions

LOG = logging.getLogger(__name__)

zmq = zmq_async.import_zmq()


class ZmqSocket(object):

    def __init__(self, context, socket_type):
        self.context = context
        self.socket_type = socket_type
        self.handle = context.socket(socket_type)
        self.connections = set()

    def type_name(self):
        return zmq_names.socket_type_str(self.socket_type)

    def connections_count(self):
        return len(self.connections)

    def connect(self, address):
        if address not in self.connections:
            self.handle.connect(address)
            self.connections.add(address)

    def setsockopt(self, *args, **kwargs):
        self.handle.setsockopt(*args, **kwargs)

    def setsockopt_string(self, *args, **kwargs):
        self.handle.setsockopt_string(*args, **kwargs)

    def send(self, *args, **kwargs):
        self.handle.send(*args, **kwargs)

    def send_string(self, *args, **kwargs):
        self.handle.send_string(*args, **kwargs)

    def send_json(self, *args, **kwargs):
        self.handle.send_json(*args, **kwargs)

    def send_pyobj(self, *args, **kwargs):
        self.handle.send_pyobj(*args, **kwargs)

    def send_multipart(self, *args, **kwargs):
        self.handle.send_multipart(*args, **kwargs)

    def recv(self, *args, **kwargs):
        return self.handle.recv(*args, **kwargs)

    def recv_string(self, *args, **kwargs):
        return self.handle.recv_string(*args, **kwargs)

    def recv_json(self, *args, **kwargs):
        return self.handle.recv_json(*args, **kwargs)

    def recv_pyobj(self, *args, **kwargs):
        return self.handle.recv_pyobj(*args, **kwargs)

    def recv_multipart(self, *args, **kwargs):
        return self.handle.recv_multipart(*args, **kwargs)

    def close(self, *args, **kwargs):
        self.handle.close(*args, **kwargs)


class ZmqPortRangeExceededException(exceptions.MessagingException):
    """Raised by ZmqRandomPortSocket - wrapping zmq.ZMQBindError"""


class ZmqRandomPortSocket(ZmqSocket):

    def __init__(self, conf, context, socket_type):
        super(ZmqRandomPortSocket, self).__init__(context, socket_type)
        self.conf = conf
        self.bind_address = zmq_address.get_tcp_random_address(self.conf)

        try:
            self.port = self.handle.bind_to_random_port(
                self.bind_address,
                min_port=conf.rpc_zmq_min_port,
                max_port=conf.rpc_zmq_max_port,
                max_tries=conf.rpc_zmq_bind_port_retries)
        except zmq.ZMQBindError:
            LOG.error(_LE("Random ports range exceeded!"))
            raise ZmqPortRangeExceededException()
