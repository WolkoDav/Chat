# coding: utf-8

import random
from string import ascii_letters, digits


CHARS = ascii_letters + digits


def random_string(size, chars=CHARS):
    return ''.join([random.choice(chars) for _ in range(size)])


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]