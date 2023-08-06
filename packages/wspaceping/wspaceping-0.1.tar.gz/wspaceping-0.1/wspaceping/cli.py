#!/usr/bin/env python
import argparse

from twisted.internet import reactor

from wspaceping.browser import SiggyBrowser
from wspaceping.poller import SiggyPoller

from anoikis.static.systems import system_name


# XXX add multiple mapping tools
parser = argparse.ArgumentParser(
    description='Watch a Siggy map for new connections'
)
parser.add_argument('systems', metavar='SYSTEMS', type=str, nargs='+',
                    help='Systems to target.')
parser.add_argument('--username', dest='username',
                    help='Username for Siggy',
                    required=True)
parser.add_argument('--password', dest='password',
                    help='Password for Siggy',
                    required=True)


def notify(target, state, distance=0):
    print ','.join([system_name(target), state, str(distance)])


def main():
    # XXX support multiple mapping tools
    args = parser.parse_args()

    browser = SiggyBrowser(
        args.username,
        args.password
    )

    SiggyPoller(
        browser,
        systems=args.systems,
        notify_callback=notify
    )

    reactor.run()


if __name__ == '__main__':
    main()
