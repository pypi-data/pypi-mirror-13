import logging
import time

from zymbit.connect.pubsub import PubSubStateMachine, NotConnected
from zymbit.connect.server import ConsoleMessengerServer
from zymbit.util.envelope import parse_buf
from zymbit.util.statemachine import NO_SLEEP
from zymbit.util.time import get_sleep_time, now


class Proxy(object):
    def __init__(self):
        self.pubsub = PubSubStateMachine(raise_exceptions=False, message_handler=self.handle_pubsub_message)
        self.messenger_server = ConsoleMessengerServer(self.handle_console_message)

        self._run = True

    @property
    def logger(self):
        return logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

    def handle_console_message(self, client, buf):
        envelope = parse_buf(buf)

        try:
            self.pubsub.send(envelope)
        except NotConnected as exc:
            self.logger.exception(exc)
            self.logger.error('unable to send pubsub buf={!r}, envelope={}'.format(buf, envelope))

    def handle_pubsub_message(self, buf):
        if not buf.endswith('\n'):
            buf = '{}\n'.format(buf)

        try:
            self.messenger_server.broadcast(buf)
        except Exception as exc:
            self.logger.exception(exc)
            self.logger.error('unable to send messenger_server buf={!r}'.format(buf))

    def run(self):
        while self._run:
            start = now()

            pubsub_result = self.pubsub.loop()
            messenger_result = self.messenger_server.loop(select_timeout=0.01)

            if NO_SLEEP in (pubsub_result, messenger_result):
                continue

            time.sleep(get_sleep_time(1.0, start))
