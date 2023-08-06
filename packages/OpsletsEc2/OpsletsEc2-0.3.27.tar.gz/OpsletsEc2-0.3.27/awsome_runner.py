#!/usr/bin/env python
import argparse, sys
import awsome.ec2nodesls
import awsome.elbnodesls

from config.env_config import initialize_config, create_config_by_user
import awsome


def create_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--configure', help='region', required=False, action='store_true')
    parser.add_argument('--dump', help='dump current configuration', required=False, action='store_true')
    parser.add_argument('-s', '--section', help='select configuration section (from the .ec2ls/config) file',
                        required=False, default=None)
    parser.add_argument('-v', '--verbose', help='verbose', required=False, action='store_true')
    return parser

def run_ec2ls():
    parser = create_parser()
    init_parser = parser
    args, argv = parser.parse_known_args()
    conf = initialize_config(parser=init_parser, section=args.section)

    if args.verbose:
        awsome.VERBOSITY = 1
    if args.dump:
        print "configuration dump: "
        for key in dir(conf):
            if not key.startswith('_') and type(conf.__getattribute__(key)) in [str, list, dict]:
                print "\t%s: [%s]" % (key, conf.__getattribute__(key))
        print "\tKey pair (default) %s: %s" % conf.user_key_pairs(None, None, None, None)



    elif args.configure:
        create_config_by_user(conf)
    elif '-h' in sys.argv:
        print """
ec2ls [FILTER] [-i] [-h]
    -i - select internal addresses only
    -h print help message
    FILTER - filter (case insensitive) of role and node name

        """
        parser.print_help()

    else:
        awsome.ec2nodesls.ec2listing(conf)

def run_elbls():
    parser = create_parser()
    init_parser = parser
    args, argv = parser.parse_known_args()
    conf = initialize_config(parser=init_parser, section=args.section)

    if args.verbose:
        awsome.VERBOSITY = 1
    if args.dump:
        print "configuration dump: "
        for key in dir(conf):
            if not key.startswith('_') and type(conf.__getattribute__(key)) in [str, list, dict]:
                print "\t%s: [%s]" % (key, conf.__getattribute__(key))
        print "\tKey pair (default) %s: %s" % conf.user_key_pairs(None, None, None, None)



    elif args.configure:
        create_config_by_user(conf)
    elif '-h' in sys.argv:
        print """
ec2ls [FILTER] [-i] [-h]
    -i - select internal addresses only
    -h print help message
    FILTER - filter (case insensitive) of role and node name

        """
        parser.print_help()

    else:
        awsome.elbnodesls.elblisting(conf)

if __name__ == '__main__':
    run_ec2ls()
