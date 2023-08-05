"""
Generate a per-site secret key
"""
import contextlib
import fcntl
import os
from time import sleep


__version__ = '0.1'


@contextlib.contextmanager
def umask(mask):
    saved = os.umask(mask)
    try:
        yield
    finally:
        os.umask(saved)


def get_secret(prefix, directory='', count=1024, _retries=10):
    path = os.path.join(directory, '.sitesecret-{}'.format(prefix))
    if os.path.exists(path):
        with open(path, 'rb') as f:
            r = f.read()
            if len(r) == count:
                return r

    r = os.urandom(count)
    with umask(0):
        mode = 0o0600
        flags = os.O_WRONLY | os.O_CREAT
        with os.fdopen(os.open(path, flags, mode), 'w') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                if _retries == 0:
                    raise
                sleep(0.05)
                return get_secret(prefix, directory, count, _retries - 1)
            f.write(r)
        return r
