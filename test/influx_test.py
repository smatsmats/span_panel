#!/usr/bin/python3

import json
import pprint
from influxdb import InfluxDBClient
from datetime import datetime
from datetime import timedelta
import logging
import logging.config

import myconfig
import mylogger
import influx

pp = pprint.PrettyPrinter(indent=4)

directory_base = "/usr/local/weatherlink2influxdb/"


def main():
    parser = argparse.ArgumentParser(description="influx client.")
    parser.add_argument(
        "--query",
        dest="query",
        action="store_true",
        default=False,
        required=False,
        help="query",
    )
    parser.add_argument(
        "--config_file",
        dest="config_file",
        default="config.yml",
        required=False,
        help="name of config file",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="should we be really verbose, huh, should we?",
    )
    args = parser.parse_args()

    c = Config(directory_base + "/config/" + args.config_file)
    config = c.getConfig()

    verbose = config["verbose"]
    if args.verbose:
        verbose = args.verbose

    ic = InfluxClient(config)

    if args.query:
        ic.query("time_in", "289367")


if __name__ == "__main__":
    main()
