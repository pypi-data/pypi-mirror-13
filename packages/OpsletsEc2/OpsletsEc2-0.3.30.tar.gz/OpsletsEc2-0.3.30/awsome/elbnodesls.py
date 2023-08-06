#!/usr/bin/env python

try:
    import argparse, sys, os
    import boto3
    from datetime import datetime
    from boto3.session import Session
    import logging
    from jinja2 import Template
    import awsome
    from resultClass import *
    from jinjaTemplate import *
except ImportError as e:
    print "Error in installation.\n\t%s\n\nPlease fix and resume." % (e)
    sys.exit(2)


# define the printing templates
myElbTemplate = Template(elb_template)
myEc2Template = Template(ec2_template)
# define the logger
logger = logging.getLogger(__file__)


def keypair_caller(name, env, role, region):
    """
    Function to retrieve the PGP keypath and SSH username
    :param name: AWS instance SSH username
    :param env: AWS environment
    :param role: AWS role
    :param region: AWS region
    :return: SSH credentials
    """
    key_path = os.getenv("SSH_KEY_FILE", 'Please set the keyfile.')
    username = os.getenv("SSH_USER_NAME", 'Please set the user name.')
    return key_path, username


def get_all_elbs(session):
    """
    Function to retrieve all ELBs and their attributes.
    :param session: elbls session information/credentials
    :return: list of ELB nodes on the current connection
    """
    client = session.client('elb')  # create ELB client for the session
    elbs = client.describe_load_balancers()  # get ELB attributes

    resource = session.resource('ec2')  # create EC2 resource for the session (for sec-grps)

    result = list()  # list to hold all attributes of an instance

    # process each ELB node
    for num, node in enumerate(elbs['LoadBalancerDescriptions']):
        instances = list()
        sg_names = list()
        zones = list()

        # reformat the creation date-time
        dt = datetime.strptime(str(node['CreatedTime']), "%Y-%m-%d %H:%M:%S.%f+%U:%W")
        launch_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # if the node has a VPC ID, retrieve it otherwise set to None
        if node.has_key('VPCId'):
            vpc_id = node['VPCId']
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
        temp = (ElbNode(num, launch_time, node['LoadBalancerName'], vpc_id, zones, node['Scheme'],
                        instances, sg_names))

        # build list of node objects
        result.append(temp)

    return result


def elblisting(conf):
    """
    Function which lists all ELB nodes requested by a user, including filter via cmd-line argument.
    For nodes displayed, the user can print associated instances.
    :param conf: ec2ls configuration file (ec2ls --configure)
    :return: none
    """
    # create, add, and parse argument for filter option
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-s', '--section', help='--place-holder--', required=False, default=None)
    parser.add_argument('filter', nargs='?', default=None)
    args, argv = parser.parse_known_args()

    # log a debug-level message
    logger.debug(
        "Using region:%s, access:key:%s secret,key:%s" % (conf.aws_region, conf.aws_access_key, conf.aws_secret_key))
    logger.debug("Config is: %s" % conf.__dict__)

    # pass user-entered filter argument to local variable
    user_filt = args.filter

    # if user selected -v option, print related info
    if awsome.VERBOSITY > 0:
        print("Using region:%s  Access:key:%s  Secret key:%s" % (
            conf.aws_region, conf.aws_access_key, conf.aws_secret_key))

    # define session parameters for the connection
    session = Session(aws_access_key_id=conf.aws_access_key, aws_secret_access_key=conf.aws_secret_key,
                      region_name=conf.aws_region)

    result = get_all_elbs(session)  # get all ELB nodes and their attributes

    # if node list isn't empty, process it
    if len(result) > 0:
        # result.sort(cmp=lambda x, y: cmp(x.date.lower(), y.date.lower()))  # sort nodes by date of creation

        filt_nodes = list()  # list to track which elb nodes were filtered in

        # process each ELB node
        for node in result:
            # if no filters set, print all - else print only those instances with matching name, and/or secgroup
            # strings to that of the user-entered filter
            if (user_filt is None) or (user_filt.lower() in node.name.lower()) or \
                    any(sgn for sgn in node.sgname if user_filt.lower() in sgn.lower()):
                filt_nodes.append(node.__dict__)  # add a dictionary of each node object to the filtered list

        # print the results via template
        print myElbTemplate.render(nodes=filt_nodes, flds=elb_flds, pres=elbPres_meta)  # print table of results

        # get user input regarding operations
        node_sel = raw_input("Would you like to view a node's instances? (Y: node #, N: other key) ")

        # extract filtered nodes' list number
        num_filt = [node['num'] for node in filt_nodes]

        # only allow nodes from those printed
        if node_sel.isdigit() and (int(node_sel) in num_filt):
            client = session.client('ec2')  # connect with AWS EC2 client

            # extract relevant instances
            for node in filt_nodes:
                if int(node_sel) == node['num']:
                    ec2s = client.describe_instances(InstanceIds=node['inst'])  # get relevant instance info

            ec2_inst = list()  # list to track ec2 instances

            # process each EC2 instance
            for inst in ec2s['Reservations']:
                for attr in inst['Instances']:
                    # retrieve user created tags for name and environment
                    for tag_dict in attr['Tags']:
                        if tag_dict['Key'] == "Name":
                            inst_name = tag_dict['Value']
                        if tag_dict['Key'] == "Env":
                            inst_env = tag_dict['Value']
                        if tag_dict['Key'] == "Role":
                            inst_role = tag_dict['Value']
                        else:
                            inst_role = None

                    # set key path and username for ssh command
                    (key_path, username) = conf.user_key_pairs(inst_name, inst_env, inst_role, conf.aws_region)

                    # get public IP
                    if attr.has_key('PublicIpAddress'):
                        ip_addr = attr['PublicIpAddress']
                    # otherwise fall back to private IP
                    elif attr.has_key('PrivateIpAddress') or '-i' in sys.argv:
                        ip_addr = attr['PrivateIpAddress']

                    # get list of security group names
                    sec_grps = [str(sg['GroupName']) for sg in attr['SecurityGroups']]

                    # reformat the creation date-time
                    dt = datetime.strptime(str(attr['LaunchTime']), "%Y-%m-%d %H:%M:%S+%U:%W")
                    launch_time = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # build the SSH command
                    cmd_str = "ssh -i %s %s@%s" % (key_path, username, ip_addr) \
                        if attr['State']['Name'] == 'running' else ""

                    # build current instance object
                    cur_inst = Ec2Inst(attr['InstanceId'], ip_addr, inst_name, inst_env, launch_time,
                                       attr['State']['Name'], inst_role, attr['PrivateIpAddress'], sec_grps,
                                       attr['KeyName'], cmd_str)

                    ec2_inst.append(cur_inst.__dict__)  # add a dictionary of each instance object to the filtered list

            print myEc2Template.render(insts=ec2_inst, flds=ec2_flds, pres=ec2Pres_meta)  # print table of results
        else:
            sys.exit("\nExiting system.")
    else:
        sys.exit("Error: no nodes returned from request.")
