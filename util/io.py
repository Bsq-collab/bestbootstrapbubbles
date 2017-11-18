import os

import errno

from typing import AnyStr


def mkdir_if_not_exists(dir_path):
    # type: (str) -> None
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def sanitize_filename(filename):
    # type: (AnyStr) -> str
    # TODO
    pass