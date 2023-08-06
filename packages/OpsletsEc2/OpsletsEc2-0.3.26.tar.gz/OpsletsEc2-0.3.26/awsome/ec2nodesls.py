#!/usr/bin/env python

import argparse, sys, os
import logging

logger = logging.getLogger(__file__)

try:
    import boto, boto.ec2, boto.rds
    import dateutil.parser
    from boto3.session import Session
# otherwise print an error on failure
except ImportError as e:
    print "Error in installation.\n\t%s\n\nPlease fix and resume." %(e)
    sys.exit(2)

import awsome
from resultClass import *  # import the AWS results class


def keypair_caller(name, env, role, region):
    key_path = os.getenv("SSH_KEY_FILE", 'Please set the keyfile.')
    username = os.getenv("SSH_USER_NAME", 'Please set the user name.')
    return (key_path, username)


def get_all_instances(ec2conn, conf):
    """
    function to print all relevant AWS EC2 instances to command line

    :param ec2conn: EC2 connection object
    :param conf: ec2ls configuration file (ec2ls --configure)
    :return: list of EC2 instances on the current connection
    """

    instances = ec2conn.get_only_instances()  # get all instances from AWS
    result = list()  # list to hold all attributes of an instance

    for inst in instances:
        tag_name = conf.name(inst.tags)  # set
        tag_env = conf.env(inst.tags)   # tag
        tag_role = conf.role(inst.tags)  # values
        sg_names = list()  # list of secgroup names based on above IDs for an instance

        the_ip = inst.ip_address  # instance public IP addr
        if the_ip is None or '-i' in sys.argv:  # fallback to private IP
            the_ip = inst.private_ip_address

        # retrieve name of each security group per instance
        for policy in inst.groups:
            sg_names.append(str(policy.name))

        # build instance object to store its attributes
        temp = Ec2Inst(inst.id, the_ip, tag_name, tag_env, inst.launch_time, inst.state, tag_role,
                          inst.private_ip_address, sg_names, inst.key_name)

        # build list of instance objects
        result.append(temp)

    return result

def ec2listing(conf):
    """
    function to print all relevant AWS EC2 instances to command line
    :param conf: ec2ls configuration file (ec2ls --configure)
    :return: none
    """

    # create, add, and parse argument for filter option
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-s', '--section', help='--place-holder--', required=False, default=None)
    parser.add_argument('filter', nargs='?', default=None)
    args, argv = parser.parse_known_args()

    logger.debug(
        "Using region:%s, access:key:%s secret,key:%s" % (conf.aws_region, conf.aws_access_key, conf.aws_secret_key))
    logger.debug("Config is: %s" % conf.__dict__)

    # establish EC2 connection with AWS
    ec2conn = boto.ec2.connect_to_region(conf.aws_region, aws_access_key_id=conf.aws_access_key,
                                         aws_secret_access_key=conf.aws_secret_key)

    # if the connection failed, raise an error
    if ec2conn is None:
        raise ValueError("Cannot connect to AWS, connection is None.")

    # retrieve all instances from the AWS EC2 connection
    the_instances = get_all_instances(ec2conn=ec2conn, conf=conf)

    # pass user-entered filter argument to local variable
    filtered_env = args.filter

    # sort list of instances based upon launch time
    the_instances.sort(cmp=lambda x, y: cmp(x.ltime.lower(), y.ltime.lower()))

    commands = list()  # list to hold SSH commands

    # if instance list isn't empty, process it
    if len(the_instances) > 0:
        cmd_to_copy = None
        inst_to_copy = None
        logger.debug("%-20s%-10s\t%s\t%-10s\t%-35s==> \t%s\n" % (
            "Launch time", "Env (tag)", "Aws-Id   ", "State", "Name", "Command"))

        # sort the list of instances a second time, where stopped and terminated ones come first
        the_instances.sort(cmp=lambda a, b: a.ltime > b.ltime)
        sorted_insts = filter(lambda x: 'running' not in x.state.lower(), the_instances)
        sorted_insts.extend(filter(lambda x: 'running' in x.state.lower(), the_instances))
        the_instances = sorted_insts

        # print table header
        print "\n%-17s%-11s%-13s%-13s%-33s%-40s%-12s  ==>   %-50s" % (
            "Launch time", "Env (tag)", "Aws-Id", "State", "Name (tag)", "Security Groups", "KP Name", "Command")
        print "%-17s%-11s%-13s%-13s%-33s%-40s%-12s  ---   %-50s\n" % (
            "-----------", "---------", "------", "-----", "----------", "---------------", "-------", "-------")

        # process each instance
        for item in the_instances:
            (key_path, username) = conf.user_key_pairs(item.name, item.env, item.role, conf.aws_region)

            # if no filters set, print all - else print only those instances with matching env, name, and/or secgroup
            # strings to that of the user-entered filter
            if (filtered_env is None) or (filtered_env.lower() in item.env.lower()) or (filtered_env.lower() in
                item.name.lower()) or any(sgn for sgn in item.sgname if filtered_env.lower() in sgn.lower()):

                # build the SSH command
                cmd_str = "ssh -i %s %s@%s" % (key_path, username, item.ip) if item.state == 'running' else ""

                # reformat the launch time output
                ts = dateutil.parser.parse(item.ltime)
                launch_time = ts.strftime("%m-%d %H:%M:%S")

                # format security groups into a string to remove list brackets
                secgroups = ", ".join(str(x) for x in item.sgname)

                # print relevant instance attributes
                print "%-17s%-11s%-13s%-13s%-33s%-40s%-12s  ==>   %-50s\n" % (
                    launch_time, item.env, item.id, item.state, item.name, secgroups, item.kpname, cmd_str)

                # add elements to SSH command list
                commands.append(cmd_str)
                commands.append(cmd_str)

                # copy SSH command which is running to temp variable (only last one will be kept)
                if item.state == 'running':
                    cmd_to_copy = cmd_str
                    inst_to_copy = item.name

        # if user entered a filter, and the SSH command list and copied-command variable aren't empty then copy the
        # command to clipboard for user's use
        if filtered_env is not None and len(commands) >= 1 and cmd_to_copy is not None:
            #cmd = "echo %s | tr -d \"\n\" | pbcopy" % (cmd_to_copy)  #on mac OSX
            cmd = "echo \"%s\" | xclip -selection clipboard" % (cmd_to_copy)  # on linux ubuntu
            os.system(cmd)
            print "\n... put this in clipboard:  %s  ===> > >  %s " % (inst_to_copy, cmd_to_copy)