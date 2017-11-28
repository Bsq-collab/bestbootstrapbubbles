import threading
from threading import RLock

import requests

from util.oop import override

lock = threading.RLock()  # type: RLock


@override(requests)
def request(_super, method, url, **kwargs):
    # NOT WORKING
    """Only allow request when lock is free."""
    print('waiting to request {}'.format(url))
    # with lock:
    print('requesting {}'.format(url))
    response = _super(method, url, **kwargs)
    print('requested {}'.format(url))
    return response
