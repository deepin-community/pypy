#!/usr/bin/env python
from cffi import FFI


ffibuilder = FFI()
ffibuilder.set_source('_fib',
    """
    int fib(int n) {
       if (n < 0) {
           return -1; // Raise
       }
       if (n < 2) {
           return 1;
       }
       return fib(n - 1) + fib(n - 2);
    }
    """,
    libraries=[])
ffibuilder.cdef("""
    int fib(int n);
""")


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
