import sys

from _fib import lib


if __name__ == '__main__':
    print(lib.fib(int(sys.argv[1])))
