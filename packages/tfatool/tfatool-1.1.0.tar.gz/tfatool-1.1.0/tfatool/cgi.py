import logging
import requests
from collections import namedtuple
from enum import Enum


logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)


##################################
# FlashAir API request formatting


URL = "http://flashair"
DEFAULT_DIR = "/DCIM/100__TSB"


class Op(Enum):
    list_files = 100
    count_files = 101


def make_cmd(op, **params):
    extras = _pairs(params) if params else ""
    cmd = "{url}/command.cgi?op={op:d}{extras}".format(
        url=URL, op=op.value, extras=extras)
    return cmd.encode("UTF-8")


def _pairs(keyvals):
    pairs = "&".join("{}={}".format(key, val)
                     for key, val in keyvals.items())
    return "&" + pairs


##########################
# FlashAir API functions


def list_files(*filters, remote_dir=DEFAULT_DIR):
    response = _cgi_cmd(Op.list_files, DIR=remote_dir)
    files = _split_file_list(response.text)
    return (f for f in files if all(filt(f) for filt in filters))


def count_files(remote_dir=DEFAULT_DIR):
    response = _cgi_cmd(Op.count_files, DIR=remote_dir)
    return int(response.text)


#############################
# API implementation details


def _cgi_cmd(op, **extras):
    cmd = make_cmd(op, **extras)
    logger.debug("Request: {}".format(cmd))
    response = requests.get(cmd)
    logger.debug("Response: {}".format(response))
    return response


_fields = ["directory", "filename", "size", "attribute", "date", "time"]
FileInfo = namedtuple("FileInfo", _fields)


def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            d, f, size, a, date, time = groups
            yield FileInfo(d, f, int(size), a, int(date), int(time))


if __name__ == "__main__":
    print(list_files())
    print(count_files())

