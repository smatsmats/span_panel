#!/usr/bin/python3

import requests
import pprint
import time
import json
import math
import sys
from requests.exceptions import HTTPError

import logging
import logging.config
import argparse
import yaml

# local stuff
import myconfig

pp = pprint.PrettyPrinter(indent=4)

session = requests.Session()
verbose = 0
directory_base = "/usr/local/span_panel/"

with open(myconfig.config["logging"]["log_config"], "rt") as f:
    lconfig = yaml.load(f.read(), Loader=yaml.SafeLoader)
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger(myconfig.config["logging"]["logger_name"])


def main():
    print("hi")


if __name__ == "__main__":
    main()
