#!/bin/env python3
import threading


class Loop:
    """Makes it easy for one function to go into an infinite loop
    some built in error handling
    """

    def __init__(self, target,
                 args=(), kwargs={},
                 on_stop=lambda: None):

        self.function = target
        self.args = args
        self.kwargs = kwargs
        self.on_stop = on_stop

        self._stop_signal = False

        self._lock = threading.Event()
        self._lock.set()

        self.loop_thread = None

    def _loop(self, *args, **kwargs):

        try:
            while not self._stop_signal:
                self.function(*args, **kwargs)

        finally:
            self._lock.set()
            self.on_stop()

    def start(self, subthread=True):
        if self.is_running():
            raise RuntimeError('Mainloop is already running')
        elif subthread:
            self._stop_signal = False
            self.loop_thread = threading.Thread(target=self._loop,
                                                args=self.args,
                                                kwargs=self.kwargs)
            self._lock.clear()
            self.loop_thread.start()
        else:
            self._stop_signal = False
            self._lock.clear()
            self._loop(*self.args, **self.kwargs)

    def stop(self):
        self._stop_signal = True
        self._lock.wait()

    def send_stop_signal(self):
        self._stop_signal = True

    def restart(self):
        self.stop()
        self.__init__(self.function, self.args, self.kwargs, self.on_stop)
        self.start()

    def is_running(self):
        return not self._lock.is_set()

