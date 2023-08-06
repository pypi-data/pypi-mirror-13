"""
aws utils fit for a chimp

Utilities:

  manage_creds:

    Allows you to refer to AWS profiles from both ~/.aws/credentials and
    ~/.aws/config files.

    Search order is:
      ~/.aws/credentials
      ~/.aws/config

    First match wins.

    For role profiles you can call get_temp_keys() and it will fetch temporary
    keys form STS and cache them in a dot file in your home directory.

    For more info on creating role profiles in ~/.aws/config:
    http://docs.aws.amazon.com/cli/latest/userguide/cli-roles.html
"""
from awschimp.awscreds import AwsCreds

__version__ = "0.0.1"
__author__ = "Matt Schurenko <matt.schurenko@gmail.com>"


def manage_creds(*args):
    '''
    Instantiates AwsCreds for you because it looks nicer

    Arguments:
      profile: your AWS profile defined in either ~/.aws/credentials or
      ~/.aws/config
      prog_name(optional): used to label the cache file in your home dir so
      that multiple programs can have uniqure temporary keys.
    '''
    return AwsCreds(*args)
