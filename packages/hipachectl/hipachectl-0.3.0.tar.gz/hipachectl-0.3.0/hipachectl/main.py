#!/usr/bin/env python
# Module:   main
# Date:     1st November 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Command Line Tool to Manage hipache"""


from __future__ import print_function

from os import environ
from argparse import ArgumentParser


from .api import Hipache


def add_virtualhost(hipache, args):
    hipache.add(args.id, args.host, args.ip, args.port)


def delete_virtualhost(hipache, args):
    hipache.delete(args.id, args.host, args.ip, args.port)


def list_virtualhosts(hipache, args):
    for i, data in enumerate(hipache):
        print("{0:d}. {1:s} {2:s} {3:s}".format(i, data["host"], data["id"], data["url"]))


def parse_args():
    parser = ArgumentParser(description=__doc__)

    parser.add_argument(
        "-u", "--url", dest="url", metavar="URL", type=str,
        default=environ.get("REDIS_PORT", environ.get("URL", "tcp://redis:6379")),
        help="hipache Redis URL",
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        description="Available Commands",
        help="Description"
    )

    # add
    add_parser = subparsers.add_parser(
        "add",
        help="Add VirtualHost"
    )
    add_parser.set_defaults(func=add_virtualhost)

    add_parser.add_argument(
        "-i", "--ip", dest="ip", default=None, metavar="IP", type=str,
        help="IP Address"
    )

    add_parser.add_argument(
        "-p", "--port", dest="port", default=80, metavar="PORT", type=int,
        help="HTTP Listening Port"
    )

    add_parser.add_argument(
        "id", metavar="ID", type=str,
        help="Container Name or CID"
    )

    add_parser.add_argument(
        "host", metavar="HOST", type=str,
        help="Application Hostname"
    )

    # delete
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete VirtualHost"
    )
    delete_parser.set_defaults(func=delete_virtualhost)

    delete_parser.add_argument(
        "id", metavar="ID", type=str,
        help="Container Name or CID"
    )

    delete_parser.add_argument(
        "host", metavar="HOST", type=str,
        help="Application Hostname"
    )

    delete_parser.add_argument(
        "-i", "--ip", dest="ip", default=None, metavar="IP", type=str,
        help="IP Address"
    )

    delete_parser.add_argument(
        "-p", "--port", dest="port", default=80, metavar="PORT", type=int,
        help="HTTP Listening Port"
    )

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List VirtualHosts"
    )
    list_parser.set_defaults(func=list_virtualhosts)

    return parser.parse_args()


def main():
    args = parse_args()

    hipache = Hipache(args.url)

    args.func(hipache, args)


if __name__ == "__main__":
    main()
