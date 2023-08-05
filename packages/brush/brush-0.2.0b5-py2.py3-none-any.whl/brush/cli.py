"""Command-line interface for brush."""

from __future__ import print_function

import os.path as osp
import logging
import json
from argparse import ArgumentParser

from tornado import log
from tornado.ioloop import IOLoop

from .comb import FrequencyComb, DummyFrequencyComb
from .sweep import Sweep

logger = logging.getLogger('brush')


def datatypes(comb, args):
    """Show all available data keys."""
    print(
        'Available data types:\n\n' + '\n'.join(sorted(comb.keys())))


def get(comb, args):
    """Get a single data point and exit."""
    keys = args.keys.split(',')
    for key in keys:
        print(key)
        result = comb.get_data([key])[key]
        dtype = comb.metadata[key]['type']
        desc = comb.metadata[key]['description']
        print(key, '=', result)
        if dtype:
            print('Type: ' + dtype)
        if desc:
            print('Description: ' + desc)
        print()


def read_config_file(args):
    """Open a configuration file and return it as a dict."""
    path = osp.abspath(osp.expanduser(args.config))
    if args.config == '~/.brush.json' and not osp.exists(path):
        config = {
            'xmlrpc': {
                'host': args.xmlrpc_server,
                'port': args.xmlrpc_port,
                'user': args.xmlrpc_user,
                'password': args.xmlrpc_password
            }
        }
        if config['xmlrpc']['host'] is None and not args.offline:
            raise RuntimeError("You must specify a hostname.")
    else:
        with open(path, 'r') as fp:
            config = json.load(fp)
        if 'port' not in config['xmlrpc']:
            config['xmlrpc']['port'] = args.xmlrpc_port
        if 'user' not in config['xmlrpc']:
            config['xmlrpc']['user'] = args.xmlrpc_user
        if 'password' not in config['xmlrpc']:
            config['xmlrpc']['password'] = args.xmlrpc_password
    return config


def parse_command_line():
    parser = ArgumentParser(
        description='Log data from a Menlo frequency comb')
    parser.add_argument(
        '--offline', action='store_true', help="Run in offline (debug) mode")
    parser.add_argument(
        '--config', default='~/.brush.json', help='Configuration file to use')
    parser.add_argument(
        '--xmlrpc-server', type=str, help='XMLRPC server hostname')
    parser.add_argument(
        '--xmlrpc-port', type=int, default=8123, help='XMLRPC server port')
    parser.add_argument(
        '-u', '--xmlrpc-user', default=None, help='XMLRPC server user name')
    parser.add_argument(
        '-p', '--xmlrpc-password', default=None, help='XMLRPC server password')
    parser.set_defaults(debug=False)

    subparsers = parser.add_subparsers(metavar='', dest='which')
    sweep_parser = subparsers.add_parser('sweep', help='Poll and record data')
    sweep_parser.add_argument(
        '--keys', default='counter0.freq',
        help='Data keys to record (comma separated)')
    sweep_parser.add_argument(
        '--uri', default=None, help='SQL URI specifier (overrides config file)')
    sweep_parser.add_argument(
        '--port', default=8090, help='Port to serve on (default: 8090)')
    sweep_parser.add_argument(
        '--prefix', default=None, help='URL prefix', type=str)

    get_parser = subparsers.add_parser('get', help='Get data once')
    get_parser.add_argument('keys', help='Data keys to get')

    subparsers.add_parser(
        'datatypes', help='List available data types')  # , aliases=['dtypes'])

    return parser.parse_args()


def main():
    """Command-line interface entry point."""
    args = parse_command_line()
    config = read_config_file(args)

    if args.offline:
        comb = DummyFrequencyComb()
        args.debug = True
    else:
        xmlrpc = config['xmlrpc']
        comb = FrequencyComb(
            xmlrpc['host'], xmlrpc['port'], xmlrpc['user'], xmlrpc['password'])

    if args.which == 'get':
        get(comb, args)
    elif args.which in ('datatypes', 'dtypes'):
        datatypes(comb, args)
    elif args.which == 'sweep':
        log.enable_pretty_logging()
        sweep = Sweep(comb, config, args)
        IOLoop.instance().run_sync(lambda: sweep.run())

if __name__ == "__main__":
    main()
