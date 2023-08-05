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
import configparser
import errno
import logging
import signal
import time
import uuid

LOGGING_FORMATTER = "%(asctime)s\t%(levelname)s\t%(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER)

import zmq

CONFIG_DEFAULTS = {
    # Maximum number of concurrent acquired locks on this semaphore
    'max-concurrency': '1',

    # Locks are valid for this many seconds before expiring
    'lock-period': '60',
}


class CommandLineApplication:
    def __init__(self):
        self.parse_args()

        self.process()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="Trivial Remote Semaphore server",
            epilog="Will reload configuration file on SIGHUP")
        parser.add_argument(
            'config', help="path to configuration file")
        parser.add_argument(
            '--port', type=int, default="6415",
            help="TCP port to listen on (default: %(default)s)")

        self.args = parser.parse_args()
        self.load_config()

        signal.signal(signal.SIGHUP, self.reload_config)

    def load_config(self):
        self.config = configparser.ConfigParser(defaults=CONFIG_DEFAULTS)
        self.config.read_file(open(self.args.config))

    def reload_config(self, signum, frame):
        logging.info("Reloading configuration")
        try:
            self.load_config()
        except Exception:
            logging.exception("Exception during configuration reload")

    def process(self):
        self.semaphores = {}  # semaphore_name: {lock_id: timestamp}

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        bind_addr = "tcp://*:{}".format(self.args.port)
        socket.bind(bind_addr)

        self.start_timestamp = int(time.time())

        last_clean_time = None

        msg = "Trivial Remote Semaphore server starting on {!r}"
        logging.info(msg.format(bind_addr))

        while True:
            try:
                message_b = socket.recv_multipart()
            except zmq.error.ZMQError as e:
                # Retry on interrupted syscall (eg from reload signal)
                if e.errno == errno.EINTR:
                    continue

            timestamp = int(time.time())

            if last_clean_time != timestamp:
                last_clean_time = timestamp
                self.clean_semaphores(timestamp)

            try:
                message = [component.decode() for component in message_b]
                result = self.process_message(message, timestamp)
            except:
                logging.exception("Process message failed")
                result = ["ERROR"]

            result_b = [component.encode() for component in result]
            socket.send_multipart(result_b)

    def clean_semaphores(self, timestamp):
        for (semaphore_name, semaphore) in self.semaphores.items():
            lock_ids_to_remove = []

            for (lock_id, expiry) in semaphore.items():
                if expiry < timestamp:
                    lock_ids_to_remove.append(lock_id)

            for lock_id in lock_ids_to_remove:
                del semaphore[lock_id]

                max_concurrency = self.config.getint(
                    semaphore_name, 'max-concurrency')
                msg = "Expired lock {!r} on {!r} (concurrency = {} of {})"
                logging.info(msg.format(
                    lock_id, semaphore_name, len(semaphore), max_concurrency))

    def process_message(self, message, timestamp):
        # [semaphore_name, action, auth/lock_id, (optional release holddown)]
        if len(message) < 3 or len(message) > 4:
            msg = "Message {!r} has incorrect length"
            logging.warning(msg.format(message))
            return ["ERROR"]

        (semaphore_name, action, auth) = message[:3]

        release_holddown_period = None
        if len(message) == 4 and action == "release":
            release_holddown_period = int(message[3])

        if semaphore_name not in self.semaphores:
            self.semaphores[semaphore_name] = {}

        semaphore = self.semaphores[semaphore_name]

        if action == 'acquire':
            secret = self.config.get(semaphore_name, 'secret', fallback=None)
            if auth != secret:
                msg = "Rejected request on semaphore {!r} - secret mismatch"
                logging.info(msg.format(semaphore_name))
                return ["ERROR"]

            lock_period = self.config.getint(semaphore_name, 'lock-period')

            if self.start_timestamp + lock_period >= timestamp:
                msg = (
                    "Rejected acquire request on semaphore {!r} - within "
                    "startup lock period")
                logging.info(msg.format(semaphore_name))
                return ["FULL"]

            max_concurrency = self.config.getint(
                semaphore_name, 'max-concurrency')

            if len(semaphore) >= max_concurrency:
                msg = (
                    "Rejected acquire request on semaphore {!r} - at maximum "
                    "concurrency")
                logging.info(msg.format(semaphore_name))
                return ["FULL"]

            lock_id = str(uuid.uuid4())
            semaphore[lock_id] = timestamp + lock_period

            msg = "Acquired lock {!r} on {!r} (concurrency = {} of {})"
            logging.info(msg.format(
                lock_id, semaphore_name, len(semaphore), max_concurrency))
            return ["OK", lock_id]

        if action == 'refresh':
            lock_id = auth

            if lock_id not in semaphore:
                msg = (
                    "Rejected refresh lock {!r} request on semaphore {!r} "
                    "(lock expired?)")
                logging.info(msg.format(lock_id, semaphore_name))
                return ["ERROR"]

            lock_period = self.config.getint(semaphore_name, 'lock-period')

            semaphore[lock_id] = timestamp + lock_period

            max_concurrency = self.config.getint(
                semaphore_name, 'max-concurrency')

            msg = "Refreshed lock {!r} on {!r} (concurrency = {} of {})"
            logging.info(msg.format(
                lock_id, semaphore_name, len(semaphore), max_concurrency))
            return ["OK"]

        if action == 'release':
            lock_id = auth

            if lock_id not in semaphore:
                msg = (
                    "Rejected release lock {!r} request on semaphore {!r} "
                    "(lock expired?)")
                logging.info(msg.format(lock_id, semaphore_name))
                return ["ERROR"]

            del semaphore[lock_id]

            lock_period = self.config.getint(semaphore_name, 'lock-period')

            if release_holddown_period:
                if release_holddown_period > lock_period:
                    msg = (
                        "Capping release holddown period {} to "
                        "lock period {}")
                    logging.info(msg.format(
                        release_holddown_period, lock_period))
                    release_holddown_period = lock_period

                holddown_lock_id = str(uuid.uuid4())
                msg = (
                    "Releasing lock {!r} on {!r} spawned holddown lock {!r} "
                    "for {} second(s)")
                logging.info(msg.format(
                    lock_id, semaphore_name, holddown_lock_id,
                    release_holddown_period))

                semaphore[holddown_lock_id] = (
                    timestamp + release_holddown_period)

            max_concurrency = self.config.getint(
                semaphore_name, 'max-concurrency')

            msg = "Released lock {!r} on {!r} (concurrency = {} of {})"
            logging.info(msg.format(
                lock_id, semaphore_name, len(semaphore), max_concurrency))
            return ["OK"]

        msg = "Unknown action in message {!r}"
        logging.warning(msg.format(message))
        return ["ERROR"]


def run():
    CommandLineApplication()
