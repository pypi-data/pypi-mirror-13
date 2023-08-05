from __future__ import absolute_import

import inspect
import logging
import time

from .time import now, get_sleep_time

NO_SLEEP = '-- NO SLEEP --'


class StateMachine(object):
    transitions = {}

    def __init__(self, raise_exceptions=True):
        self._run = True
        self._state = self.start

        self.raise_exceptions = raise_exceptions
        self.loop_sleep_time = 1.0

        self.last_exception = None

        self._setup_transitions()
        self.logger.debug('transitions={}'.format(self.transitions))

    def _setup_transitions(self):
        # convert the transition functions into bound methods
        _transitions = {}
        for k, v in list(self.transitions.items()):
            bound_method = getattr(self, k.__name__)
            t_transitions = dict([(kk, getattr(self, vv.__name__)) for kk, vv in list(v.items())])

            _transitions[bound_method] = t_transitions

        self.transitions = _transitions

    @property
    def logger(self):
        return logging.getLogger(__name__)

    def loop(self):
        result = None

        try:
            result = self._state()
        except Exception as exc:  # global exception catcher here to use for state transitions
            self.last_exception = exc

            result = exc
            if not inspect.isclass(exc):
                result = exc.__class__

            if self.raise_exceptions:
                raise
            else:
                self.logger.exception(exc)
        else:
            self.last_exception = None
        finally:
            transitions = self.transitions.get(self._state, {})

            for _result, _state in list(transitions.items()):
                if _result == result or inspect.isclass(_result) and inspect.isclass(result) and issubclass(result, _result):
                    self._state = _state

        return result

    def quit(self):
        self._run = False

    def run(self):
        while self._run:
            start = now()

            current_state = self._state
            result = self.loop()

            # only sleep when there is no state transition
            if current_state == self._state and result != NO_SLEEP:
                sleep_time = get_sleep_time(self.loop_sleep_time, start)
                # self.logger.debug('loop_sleep_time={}, sleep_time={}'.format(self.loop_sleep_time, sleep_time))
                time.sleep(sleep_time)

    def start(self):
        return True
