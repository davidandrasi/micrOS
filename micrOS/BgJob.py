import _thread
from time import sleep


class BgTask:
    __instance = None

    def __new__(cls, delay=1, loop=False):
        """
        Singleton design pattern
        __new__ - Customize the instance creation
        cls     - class
        """
        if cls.__instance is None:
            # SocketServer singleton properties
            cls.__instance = super().__new__(cls)
            cls.__loop = loop
            cls.__lock = None
            cls.__isbusy = False
            cls.__lock = _thread.allocate_lock()
            cls.__ret = ''
            cls.__call_ret = None
            cls.__taskid = 0
        return cls.__instance

    def __enter__(cls):
        cls.__lock.acquire()

    def __exit__(cls, exc_type, exc_val, exc_tb):
        cls.__lock.release()

    def __th_task(cls, lm_core, arglist, delay=1):
        cls.__isbusy = True
        while True:
            # Set delay
            sleep(delay) if delay > 0 else sleep(0.1)
            # Check thread lock - wait until release
            if cls.__lock.locked():
                continue
            # RUN CALLBACK
            cls.__call_ret = lm_core(arglist, msgobj=cls.msg)
            # Exit thread
            if not cls.__loop:
                break
        cls.__isbusy = False

    def msg(cls, msg):
        if len(msg) > 80:
            cls.__ret = msg[0:80]
            return
        cls.__ret = msg

    def run(cls, lm_core, arglist, loop=None, delay=None):
        # Return if busy - single job support
        if cls.__isbusy:
            return False, cls.__taskid
        # Set thread params
        cls.__ret = ''
        cls.__call_ret = None
        cls.__taskid += -50 if cls.__taskid > 50 else 1
        cls.__loop = cls.__loop if loop is None else loop
        # Start thread
        _thread.start_new_thread(cls.__th_task, (lm_core, arglist, delay))
        return True, cls.__taskid

    def stop(cls):
        if cls.__isbusy or cls.__loop:
            cls.__loop = False
            return '[BgJob] Stop {}'.format(cls.__taskid)
        return '[BgJob] Already stopped {}'.format(cls.__taskid)

    def info(cls):
        return {'isbusy': cls.__isbusy, 'state': cls.__call_ret,
                'taskid': cls.__taskid, 'out': cls.__ret}
