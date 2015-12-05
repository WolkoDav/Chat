# coding: utf-8

import random
from string import ascii_letters, digits


CHARS = ascii_letters + digits


def random_string(size, chars=CHARS):
    return ''.join([random.choice(chars) for _ in range(size)])
