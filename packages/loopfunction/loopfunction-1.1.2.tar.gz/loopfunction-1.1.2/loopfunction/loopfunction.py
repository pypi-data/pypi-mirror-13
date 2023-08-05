#!/bin/env python3
import threading

class Loop:
    """Makes it easy for one function to go into an infinite loop
    """

    def __init__(self, target,
                 args=(), kwargs={},
                 on_start=lambda: None,
                 on_start_args=(), on_start_kwargs={},
                 on_stop=lambda: None,
                 on_stop_args=(), on_stop_kwargs={}):
        """The initialization of the Loop class

        :param target: The target function
        :param args: Arguments to be used when calling target function
        :param kwargs: Keyword arguments to be used when calling target function
        :param on_start: Function to run when the loop starts together with on_start_args and on_start_kwargs
        :param on_start_args: See on_start
        :param on_start_kwargs: See on_start
        :param on_stop: Function to run when the loop stops together with on_stop_args and on_stop_kwargs
        :param on_stop_args: See on_stop
        :param on_stop_kwargs: See on_stop
        """

        self.target = target
        self.args = args
        self.kwargs = kwargs

        self.on_start = on_start
        self.on_start_args = on_start_args
        self.on_start_kwargs = on_start_kwargs

        self.on_stop = on_stop
        self.on_stop_args = on_stop_args
        self.on_stop_kwargs = on_stop_kwargs

        self._stop_signal = False

        self._lock = threading.Event()
        self._lock.set()

        self._loop_thread = None

        self._in_subthread = None

    def _loop(self, *args, **kwargs):
        """Loops the target function

        :param args: The args specified on initiation
        :param kwargs: The kwargs specified on initiation
        """
        self.on_start(*self.on_start_args, **self.on_start_kwargs)
        try:
            while not self._stop_signal:
                self.target(*args, **kwargs)
        finally:
            self.on_stop(*self.on_stop_args, **self.on_stop_kwargs)
            self._stop_signal = False
            self._lock.set()

    def start(self, subthread=True):
        """Starts the loop

        Tries to start the loop. Raises RuntimeError if the loop is currently running.

        :param subthread: True/False value that specifies whether or not to start the loop within a subthread. If True
        the threading.Thread object is found in Loop._loop_thread.
        """
        if self.is_running():
            raise RuntimeError('Loop is currently running')
        else:
            self._lock.clear()
            self._in_subthread = subthread
            if subthread:
                self._loop_thread = threading.Thread(target=self._loop,
                                                    args=self.args,
                                                    kwargs=self.kwargs)
                self._loop_thread.start()
            else:
                self._loop(*self.args, **self.kwargs)

    def stop(self, silent=False):
        """Sends a stop signal to the loop thread and waits until it stops

        A stop signal is sent using Loop.send_stop_signal(silent) (see docs for Loop.send_stop_signal)

        :param silent: True/False same parameter as in Loop.send_stop_signal(silent)
        """
        self.send_stop_signal(silent)
        self._lock.wait()

    def send_stop_signal(self, silent=False):
        """Sends a stop signal to the loop thread

        :param silent: True/False value that specifies whether or not to raise RuntimeError if the loop is currently not
        running
        :return:
        """
        if self.is_running():
            self._stop_signal = True
        elif not silent:
            raise RuntimeError('Loop is currently not running')

    def restart(self, subthread=None):
        """Restarts the loop function

        Tries to restart the loop thread using the current thread. Raises RuntimeError if a previous call to Loop.start
        was not made.

        :param subthread: True/False value used when calling Loop.start(subthread=subthread). If set to None it uses the
        same value as the last call to Loop.start.
        """
        if self._in_subthread is None:
            raise RuntimeError('A call to start must first be placed before restart')
        self.stop(silent=True)
        if subthread is None:
            subthread = self._in_subthread
        self.__init__(self.target, self.args, self.kwargs, self.on_stop)
        self.start(subthread=subthread)

    def is_running(self):
        """Used to check if the loop is currently running

        :return: Returns True/False specifying whether ot not the loop is currently running.
        """
        return not self._lock.is_set()

