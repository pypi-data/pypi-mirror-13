class Ec2Inst:
    """
    Class which stores AWS EC2 instance attributes for easier access and readability.
    """
    def __init__(self, in_id, in_ip, in_name, in_env, in_launch, in_state, in_role, in_pip, in_sgname, in_kpname):
        """
        New class object initialization method
        :param in_id: instance's ID
        :param in_ip: instance public IP address
        :param in_name: instance's name
        :param in_env: instance's working environment
        :param in_launch: instance's launch time
        :param in_state: instance's current working state
        :param in_role: instance's role
        :param in_pip: instance's private IP address
        :param in_sgname: instance's security group memberships
        :param in_kpname: instance's key-pair name
        :return: N/A
        """
        self.id = in_id
        self.ip = in_ip
        self.name = in_name
        self.env = in_env
        self.ltime = in_launch
        self.state = in_state
        self.role = in_role
        self.pip = in_pip
        self.sgname = in_sgname
        self.kpname = in_kpname

    def __str__(self):
        """
        Method to format object's data into human readable string.
        :return: formatted object string
        """
        return ("Instance information -\nID: %s\nPublic IP: %s\nName: %s\nEnvironment: %s\nLaunch Time: %s\nState: %s\n"
                "Role: %s\nPrivate IP: %s\nSecGrp Name: %s\nKeyPair Name: %s") % (self.id, self.ip, self.name, self.env,
                self.ltime, self.state, self.role, self.pip, self.sgname, self.kpname)


class ElbNode:
    """
    Class which stores AWS ELB node attributes for easier access and readability.
    """
    def __init__(self, nd_date, nd_name, nd_vpcid, nd_zone, nd_scheme, nd_inst, nd_sgname):
        """

        :param nd_date: node's creation date
        :param nd_name: node's name
        :param nd_vpcid: node's VPC ID
        :param nd_zone: node's availability zone
        :param nd_scheme: node's scheme/type
        :param nd_inst: node's instances
        :param nd_sgname: node's security group names
        :return: N/A
        """
        self.date = nd_date
        self.name = nd_name
        self.vpcid = nd_vpcid
        self.zone = nd_zone
        self.scheme = nd_scheme
        self.inst = nd_inst
        self.sgname = nd_sgname


    def __str__(self):
        """
        Method to format object's data into human readable string.
        :return: formatted object string
        """
        return ("Node information -\nDate Created: %s\nName: %s\nVPC ID: %s\nAvailability Zone: %s\nScheme: %s\n"
                "Instances:%s\nSecGrp Name: %s") % (self.date, self.name, self.vpcid, self.zone, self.scheme, self.inst,
                self.sgname)