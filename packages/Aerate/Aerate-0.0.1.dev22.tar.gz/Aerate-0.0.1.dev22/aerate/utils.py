from datetime import datetime
from aerate.config import config

# makes an instance of the Config helper class available to all the modules
# importing aerate.utils.


def str_to_date(string):
    """ Converts a date string formatted as defined in the configuration
        to the corresponding datetime value.
    :param string: the RFC-1123 string to convert to datetime value.
    """
    return datetime.strptime(string, config.DATE_FORMAT) if string else None
