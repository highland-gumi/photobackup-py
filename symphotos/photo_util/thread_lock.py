import threading

lock = threading.Lock()


class Lock():
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def acquire(self, blocking=False):
        return lock.acquire(blocking=blocking)

    def release(self):
        return lock.release()

    def is_locked(self):
        ret = self.acquire(blocking=False)
        if ret:
            lock.release()
        return ret


def locking(func):
    def wrapper(*args, **kwargs):
        lock.acquire()
        func(*args, **kwargs)
        lock.release()

    return wrapper
