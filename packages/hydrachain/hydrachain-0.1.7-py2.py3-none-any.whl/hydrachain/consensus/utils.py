from sha3 import sha3_256
from ethereum.utils import big_endian_to_int


def sha3(seed):
    return sha3_256(bytes(seed)).digest()

# colors

FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def DEBUG(*args, **kargs):
    print(FAIL + repr(args) + repr(kargs) + ENDC)

colors = ['\033[9%dm' % i for i in range(0, 7)]
colors += ['\033[4%dm' % i for i in range(1, 8)]
num_colors = len(colors)


def cstr(num, txt):
    if isinstance(num, bytes):
        num = big_endian_to_int(num)
    return '%s%s%s' % (colors[num % len(colors)], txt, ENDC)


def cprint(num, txt):
    print cstr(num, txt)


def phx(x):
    return x.encode('hex')[:8]

if __name__ == '__main__':
    for i in range(len(colors)):
        cprint(i, 'test')
