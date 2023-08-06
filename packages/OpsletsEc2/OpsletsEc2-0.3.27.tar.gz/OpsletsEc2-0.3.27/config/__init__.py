import os


def none_caller(name, env, role, region):
    key_path = os.getenv("SSH_KEY_FILE", "tbd_key")
    username = os.getenv("SSH_USER_NAME", "tbd_user")
    return (key_path, username)


def tag_fetcher(tags, cordered_vals=[]):
    for key in cordered_vals:
        if key in tags:
            return tags[key]
    return "no_tag"


def _conditional_overrider(new_val, existing_val):
    """
    does not overrider the value if new_val is None
    :return: value to assign
    """
    if new_val is not None or new_val == '':
        return new_val
    return existing_val


class EnvConfig(object):
    def __init__(self):
        self._aws_access_key = None
        self._aws_secret_key = None
        self._aws_region = None
        self.env_tags = ["Env", "env"]
        self.role_tags = ["Role", "role"]
        self.name_tags = ["Name"]
        self._user_key_pairs = none_caller

    @property
    def user_key_pairs(self):
        return self._user_key_pairs

    @user_key_pairs.setter
    def user_key_pairs(self, key_pair_lambda):
        self._user_key_pairs = key_pair_lambda

    @property
    def aws_access_key(self):
        return self._aws_access_key

    @aws_access_key.setter
    def aws_access_key(self, val):
        self._aws_access_key = _conditional_overrider(val, self.aws_access_key)

    @property
    def aws_secret_key(self):
        return self._aws_secret_key

    @aws_secret_key.setter
    def aws_secret_key(self, val):
        self._aws_secret_key = _conditional_overrider(val, self.aws_secret_key)

    @property
    def aws_region(self):
        return self._aws_region

    @aws_region.setter
    def aws_region(self, val):
        self._aws_region = _conditional_overrider(val, self.aws_region)

    def env(self, tags):
        return tag_fetcher(tags, self.env_tags)

    def name(self, tags):
        return tag_fetcher(tags, self.name_tags)

    def role(self, tags):
        return tag_fetcher(tags, self.role_tags)
