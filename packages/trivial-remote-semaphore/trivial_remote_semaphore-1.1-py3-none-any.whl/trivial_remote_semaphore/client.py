#   Copyright 2015-2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import sys
import time

import zmq

ZMQ_CONTEXT = zmq.Context()


class Client:
    def __init__(self, server):
        self._server = server

    def _send_message(self, message):
        socket = ZMQ_CONTEXT.socket(zmq.REQ)
        socket.setsockopt(zmq.SNDTIMEO, 1000)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.setsockopt(zmq.LINGER, 0)

        socket.connect(self._server)

        message_b = [component.encode() for component in message]

        try:
            socket.send_multipart(message_b)
            result_b = socket.recv_multipart()
        except zmq.error.Again:
            return None
        finally:
            socket.close()

        result = [component.decode() for component in result_b]

        return result

    def _send_message_until_ok(self, message, timeout):
        start_timestamp = time.time()

        while start_timestamp + timeout > time.time():
            result = self._send_message(message)

            if result is not None and result[0] == "OK":
                return result

            time.sleep(1)

        return None

    def acquire(self, semaphore, secret, timeout=60):
        '''
        Acquire lock on semaphore

        * returns lock_id if successful, otherwise None
        '''

        message = [semaphore, 'acquire', secret]

        result = self._send_message_until_ok(message, timeout)

        if result is not None:
            return result[1]

        return None

    def refresh(self, semaphore, lock_id, timeout=60):
        '''
        Refresh lock on semaphore

        * returns True if successful, False otherwise
        '''

        message = [semaphore, 'refresh', lock_id]

        result = self._send_message_until_ok(message, timeout)

        return (result is not None)

    def release(self, semaphore, lock_id, holddown_period=None, timeout=60):
        '''
        Release lock on semaphore (applying optional server-side holddown)

        * returns True if successful, otherwise False
        '''

        message = [semaphore, 'release', lock_id]
        if holddown_period:
            message.append(str(holddown_period))

        result = self._send_message_until_ok(message, timeout)

        return (result is not None)


class CommandLineApplication:
    def __init__(self):
        self.parse_args()

        self.process()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="Trivial Remote Semaphore client",
            epilog=(
                "If action is successful, return code is 0, else 1.  "
                "The acquired lock_id is printed to stdout (acquire only)."
                ))
        parser.add_argument(
            '--server', default="tcp://localhost:6415",
            help="Server to connect to (default: %(default)s)")
        parser.add_argument(
            '--timeout', type=int, default=60,
            help="Timeout (seconds)")
        parser.add_argument('semaphore', help="Semaphore name")
        parser.add_argument(
            'action', choices=['acquire', 'refresh', 'release'],
            help="Action to perform")
        parser.add_argument(
            'secret', help=(
                "Semaphore secret (for acquire) or lock_id (for "
                "refresh/release)"))
        parser.add_argument(
            'holddown_period', nargs='?', type=int, default=0,
            help="Optional holddown period (release only)")

        self.args = parser.parse_args()

    def process(self):
        trs_client = Client(self.args.server)

        if self.args.action == "acquire":
            lock_id = trs_client.acquire(
                self.args.semaphore, self.args.secret, self.args.timeout)

            if lock_id is None:
                sys.exit(1)

            print(lock_id)
            sys.exit(0)

        if self.args.action == "refresh":
            success = trs_client.refresh(
                self.args.semaphore, self.args.secret, self.args.timeout)

            if success:
                sys.exit(0)
            sys.exit(1)

        if self.args.action == "release":
            success = trs_client.release(
                self.args.semaphore, self.args.secret,
                self.args.holddown_period, self.args.timeout)

            if success:
                sys.exit(0)
            sys.exit(1)


def run():
    CommandLineApplication()
