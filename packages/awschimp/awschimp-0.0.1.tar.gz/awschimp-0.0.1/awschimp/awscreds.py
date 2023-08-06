'''
So far AwsCreds is the only class. More to be added later (maybe).
'''
import boto3
import botocore
import ConfigParser
import os
import pickle
import time


class ProfileError(Exception):
    pass


class ConfigError(Exception):
    pass


class IamError(Exception):
    pass


class StsError(Exception):
    pass


class AwsCreds():
    """
    Hunts for profiles in ~/.aws/credentials and ~/.aws/config.
    Gets tempoary keys from STS service and caches in
     ~/.prog_name_profile.cache for assume_role_expiration seconds.
    Sets RoleSessionName to IAM user name for cloudtrail purposes.
    """

    def __init__(self, profile, prog_name="awschimp"):
        self.profile = profile
        self.prog_name = prog_name
        self.assume_role_expiration = 900
        try:
            self.assume_role_cache = os.path.join("{}/.{}_{}.cache"
                                                  .format(os.environ["HOME"],
                                                          prog_name, profile))
        except Exception:
            raise KeyError("could not find HOME env variable")
        self.iam_user = self.get_iam_user()

    def get_from_creds(self, profile):
        creds = ConfigParser.ConfigParser()
        try:
            creds.read(os.path.join(os.environ["HOME"], ".aws/credentials"))
        except Exception as e:
            raise ConfigError(e.message)

        if profile in creds.sections():
            options = creds.options(profile)
            for option in options:
                if option == "aws_access_key_id":
                    key = creds.get(profile, option)
                elif option == "aws_secret_access_key":
                    secret = creds.get(profile, option)
            return key, secret
        else:
            return None

    def get_from_config(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(os.path.join(os.environ["HOME"], ".aws/config"))
        except Exception as e:
            raise ConfigError(e.message)
        config._sections.pop("default", default=None)
        if self.profile in map(lambda s: s.split('profile ')[-1],
                               config.sections()):
            options = config.options('profile ' + self.profile)
            for option in options:
                if option == "role_arn":
                    role = config.get('profile ' + self.profile, option)
                elif option == "source_profile":
                    source_profile = config.get('profile ' + self.profile,
                                                option)
                    key, secret = self.get_from_creds(source_profile)
        else:
            raise ProfileError("profile {} was not found".format(self.profile))

        return key, secret, role

    def get_from_profile(self):
        '''
        this can be used to fetch access_key/secret key from credentials file
        '''
        resp = self.get_from_creds(self.profile)
        if resp:
            return resp
        else:
            return self.get_from_config()

    def get_iam_user(self):
        '''
        this is used to set the RoleSessionName
        '''
        creds = self.get_from_profile()
        iam_client = boto3.client("iam", aws_access_key_id=creds[0],
                                  aws_secret_access_key=creds[1])
        try:
            return iam_client.get_user()["User"]["UserName"]
        except Exception as e:
            raise IamError(e.message)

    def get_sts(self):
        '''
        only profile names that assume a role will work here
        '''
        creds = self.get_from_profile()
        sts_client = boto3.client("sts", aws_access_key_id=creds[0],
                                  aws_secret_access_key=creds[1])
        if len(creds) != 3:
            raise ProfileError("No role arn found for {}".format(self.profile))
        try:
            assumed_role_object = sts_client.assume_role(
                RoleArn=creds[2],
                DurationSeconds=self.assume_role_expiration,
                RoleSessionName=self.get_iam_user()
            )
        except Exception as e:
            raise StsError(e.message)

        pickle.dump(assumed_role_object["Credentials"],
                    open(self.assume_role_cache, "w"))
        return assumed_role_object["Credentials"]

    def get_temp_keys(self):
        '''
        pickle results from sts service
        '''
        if os.path.isfile(self.assume_role_cache):
            sts_d = pickle.load(open(self.assume_role_cache))
            expiration_time = int(sts_d["Expiration"].strftime("%s"))
            current_time = int(time.mktime(time.gmtime()))
            if expiration_time - current_time <= 1:
                credentials = self.get_sts()
            else:
                credentials = sts_d
        else:
            credentials = self.get_sts()

        return credentials
