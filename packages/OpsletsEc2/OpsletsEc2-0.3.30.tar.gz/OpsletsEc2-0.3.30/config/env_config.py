import os
import ConfigParser, argparse, pprint

from config import EnvConfig

config_search_path = [
    os.getcwd(), os.getenv("HOME"), os.getenv("VIRTUAL_ENV")
]
CONF_LOCATION = ".opsletsls/config"
DEFAULT_SECTION="DEFAULT"

def update_conf_from_dict(conf, the_dict):
    conf.aws_access_key = the_dict.get('aws_access_key', None)
    conf.aws_secret_key = the_dict.get('aws_secret_key', None)
    conf.aws_region = the_dict.get('aws_region', None)
    key_path = the_dict.get('key_path', None)
    ssh_user = the_dict.get('ssh_username', None)
    if None not in [key_path, ssh_user]:
        conf.user_key_pairs = lambda a, b, c, d: (key_path, ssh_user)
    if 'key_pair_lambda' in the_dict:
        import imp
        for base_path in config_search_path:
            py_script_file = os.path.join(base_path, the_dict['key_pair_lambda'])
            if os.path.isfile(py_script_file):
                the_module = imp.load_source('user_keypair', py_script_file)
                conf._user_key_pairs = the_module.user_keypair_lambda
                break
        else:
            raise SystemError("Could not load file (%s) from any of the locations: (%s)" % (
                the_dict['key_pair_lambda'], config_search_path))

    return conf


def update_conf_from_cli(conf, parser=argparse.ArgumentParser(add_help=False)):
    parser.add_argument('-aws-reg', '--aws-region', help='region', required=False)
    parser.add_argument('-aws-id', '--aws-access-key', help='aws access key id', required=False)
    parser.add_argument('-aws-secret', '--aws-secret-key', help='aws secret key', required=False)
    args, argv = parser.parse_known_args()
    conf = update_conf_from_dict(conf, args.__dict__)
    return conf


def update_conf_from_file(conf, paths=config_search_path, section=DEFAULT_SECTION):
    for base_path in [p for p in paths if p is not None]:
        cfg_file = os.path.join(base_path, CONF_LOCATION)
        if os.path.isfile(cfg_file):
            cfg_fl = ConfigParser.SafeConfigParser()
            cfg_fl.read(cfg_file)
            the_dict = dict(cfg_fl.items(DEFAULT_SECTION if section is None else section))
            conf = update_conf_from_dict(conf, the_dict)
            return conf
    return conf


def update_conf_from_env_vars(conf=EnvConfig()):
    conf.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    conf.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    conf.aws_region = os.getenv('AWS_REGION')
    return conf


def initialize_config(conf=EnvConfig(), section=None, parser=argparse.ArgumentParser(add_help=False)):
    """
    initializes the configuration, in the following order:
    ENV_VARS, then overrides with
    FILE SEARCH PATH, then overrides with
    CLI args

    :param conf: initial configuration settings
    :return: updated configuration
    """
    conf = update_conf_from_file(conf, section=section)
    conf = update_conf_from_env_vars(conf)
    conf = update_conf_from_cli(conf, parser)
    return conf


def prompt_user(msg, default=None, can_delete=True):
    val = raw_input(msg % {'default': default}).strip()

    if val == '-':
        if can_delete:
            return None
        else:
            return default
    elif len(val) > 0:
        return val
    else:
        return default


def create_config_by_user(conf):
    print("Creating default configuration file")

    curr_config = ConfigParser.SafeConfigParser()
    user_key_pair = conf.user_key_pairs(None, None, None, None)
    options_map = dict([(o, conf.__getattribute__(o)) for o in ['aws_access_key', 'aws_secret_key', 'aws_region']])
    options_map['key_path'] = user_key_pair[0]
    options_map['ssh_username'] = user_key_pair[1]

    print("Current configuration is: \n%s\n" % pprint.pformat(options_map))

    for opt in options_map.keys():
        curr_val = options_map[opt]
        val = raw_input(
                "pls enter value for field:%s, [press ENTER to keep current:'%s', chose minus('-'), to clear value]: " % (
                    opt, curr_val)).strip()
        if val == '-':
            del options_map[opt]
        elif len(val) > 0:
            options_map[opt] = val
        else:
            options_map[opt] = curr_val
    section = prompt_user("Which section do you want to use, current: %(default)s]: ", DEFAULT_SECTION,
                          can_delete=False)
    if section != DEFAULT_SECTION:
        curr_config.add_section(section)
    for opt in options_map.keys():
        curr_config.set(section=section, option=opt, value=options_map[opt])
    print "\tThanks. Here is the resulting file content:"
    curr_config.write(os.sys.stdout)


    out_base_path = os.getenv('VIRTUAL_ENV')
    if out_base_path is not None:
        val = raw_input("Write the file to ($VIRTUAL_ENV: %s/.opsletsls/config) [yes/no]? :" % out_base_path)
        dest_location = None
        if val.lower() == 'yes':
            dest_location = os.path.join(out_base_path, ".opsletsls")
        if dest_location is not None:
            if not os.path.isdir(dest_location):
                os.mkdir(dest_location)
            curr_config.read(os.path.join(dest_location, "config"))
            curr_config.write(open(os.path.join(dest_location, "config"), "w+"))
    return curr_config
