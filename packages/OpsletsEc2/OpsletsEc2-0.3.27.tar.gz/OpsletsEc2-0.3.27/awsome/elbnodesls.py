#!/usr/bin/env python

# attempt to import the following libraries
try:
    import argparse, sys, os
    import boto3
    import time
    from datetime import datetime
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


def get_all_elbs(conf):
    """
    Function to retrieve all ELBs and their attributes
    :param conf: elbls configuration file (elbls --configure)
    :return: list of ELC nodes on the current connection
    """
    session = Session(aws_access_key_id=conf.aws_access_key, aws_secret_access_key=conf.aws_secret_key,
                      region_name=conf.aws_region)

    client = session.client('elb')
    elbs = client.describe_load_balancers()

    resource = session.resource('ec2')

    result = list()  # list to hold all attributes of an instance

    for node in elbs['LoadBalancerDescriptions']:
        instances = list()
        sg_names = list()
        zones = list()

        # reformat the creation date-time
        dt = datetime.strptime(str(node['CreatedTime']), "%Y-%m-%d %H:%M:%S.%f+%U:%W")
        launch_time = dt.strftime("%d-%m-%Y %H:%M:%S")

        # if the node has a VPC ID, retrieve it otherwise set to None
        if node.has_key('VPCId'):
            vpc_id =  node['VPCId']
        else:
            vpc_id = None

        last = ""  # variable to track last availability zone string
        # retrieve availability zones per node
        for zone in node['AvailabilityZones']:

            # if substring excluding zone number exists in the last iteration string, then take only the zone number
            # otherwise take the entire availability zone but replace the last '-' with ':'
            if zone[:-2] in last:
                zones.append(str(zone[-2:]))
            else:
                temp = zone[:-3] + ":" + zone[-2:]
                zones.append(temp)
            last = zone  # update last string tracker

        # retrieve name of each instance per node
        for inst in node['Instances']:
            for in_name in inst.keys():
                instances.append(str(inst[in_name]))

        # retrieve name of each security group per node
        for policy in node['SecurityGroups']:
            secgrp = resource.SecurityGroup(policy)
            sg_names.append(secgrp.group_name)

        # build node object to store its attributes
        temp = (ElbNode(launch_time, node['LoadBalancerName'], vpc_id, zones, node['Scheme'],
                        instances, sg_names))

        # build list of node objects
        result.append(temp)

    return result


def elblisting(conf):
    # if user selected -v option, print related info
    if awsome.VERBOSITY > 0:
        print("Using region:%s  Access:key:%s  Secret key:%s" % (
            conf.aws_region, conf.aws_access_key, conf.aws_secret_key))

    # get_all_elbs(conf)
    result = get_all_elbs(conf) # get all ELB nodes and their attributes

    # if nodelist isn't empty, process it
    if len(result) > 0:
        result.sort(cmp=lambda x, y: cmp(x.date.lower(), y.date.lower()))

        # print table header
        print "\n%-22s%-19s%-15s%-25s%-18s%-49s%-25s" % (
            "Creation Time", "Name", "VPC ID", "Zones", "Scheme", "Instances", "Security Groups")
        print "%-22s%-19s%-15s%-25s%-18s%-49s%-25s" % (
            "-------------", "----", "------", "-----", "------", "---------", "---------------")
        for node in result:
            # format security groups into a string to remove list brackets
            secgroups = ", ".join(str(x) for x in node.sgname)
            instances = ", ".join(str(x) for x in node.inst)
            zones = ", ".join(str(x) for x in node.zone)
            print "%-22s%-19s%-15s%-25s%-18s%-49s%-25s" % (
                node.date, node.name, node.vpcid, zones, node.scheme, instances, secgroups)
    else:
        sys.exit("Error: no nodes returned from request.")
