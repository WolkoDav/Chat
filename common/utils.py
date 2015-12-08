import sys
import fcntl
import struct
import termios
import readline
import random
from string import ascii_letters, digits

__all__ = ['Singleton', 'random_string', 'print_']


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Сгенерировать рандомную строку
def random_string(size, chars=ascii_letters + digits):
    return ''.join([random.choice(chars) for _ in range(size)])


# Мего-хак для очистки текущий строки на экране, что бы выводилась нотификации
def blank_current_readline():
    # Next line said to be reasonably portable for various Unixes
    rows, cols = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))
    text_len = len(readline.get_line_buffer())+2
    # ANSI escape sequences (All VT100 except ESC[0G)
    sys.stdout.write('\x1b[2K')                         # Clear current line
    sys.stdout.write('\x1b[1A\x1b[2K'*(text_len // cols))  # Move cursor up and clear line
    sys.stdout.write('\x1b[0G')


# Обёртка над принтом для вывода в консоль с мега хаком
def print_(message):
    blank_current_readline()
    print(message)
    sys.stdout.write('> ' + readline.get_line_buffer())
    sys.stdout.flush()