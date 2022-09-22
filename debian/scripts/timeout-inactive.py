#!/usr/bin/python2

import argparse
import re
import signal
import subprocess
import sys
import threading


def main():
    p = argparse.ArgumentParser(
        description='Run a program, and kill it if it is silent for too long.'
                    'After the arguments, specify the program to run prefixed '
                    'with -- .')
    p.add_argument('--timeout', type=parse_timeout,
                   help='Timeout (in seconds, if no unit specified')

    our_args = sys.argv[1:]
    cmd = []
    if '--' in our_args:
        index = our_args.index('--')
        cmd = our_args[index + 1:]
        our_args = our_args[:index]

    args = p.parse_args(our_args)
    if not cmd:
        p.error('No command specified')

    run_cmd(cmd, args.timeout)


def parse_timeout(arg):
    m = re.match(r'(\d+) *(s(ec(ond)?s?)?|m(in(ute)?s?)?|h((ou)?rs?)?)?', arg)
    if not m:
        raise argparse.ArgumentTypeError('Un-parseable time')
    value = int(m.group(1))
    unit = m.group(2)
    if unit:
        unit = unit[0]
        if unit == 'm':
            return value * 60
        if unit == 'h':
            return value * 60 * 60
    return value


def run_cmd(cmd, timeout):
    p = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE)
    watchdog = Watchdog(timeout, p)
    watchdog.start()
    while True:
        line = p.stdout.readline()
        watchdog.event.set()
        sys.stdout.write(line)
        sys.stdout.flush()
        if p.poll() != None:
            sys.exit(p.returncode)


class Watchdog(threading.Thread):
    def __init__(self, timeout, process):
        super(Watchdog, self).__init__()
        self.daemon = True
        self.timeout = timeout
        self.process = process
        self.event = threading.Event()

    def run(self):
        while True:
            ev = self.event.wait(self.timeout)
            if ev is True:
                self.event.clear()
            else:
                sys.stderr.write(
                    '\nTimed out after {} seconds of inactivity...\n'
                    .format(self.timeout))
                sys.stderr.flush()
                self.process.send_signal(signal.SIGINT)
                return


if __name__ == '__main__':
    main()
