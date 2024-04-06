#!/usr/bin/python3

import yaml
import logging
import logging.config
import argparse
import pprint

verbose = 0
directory_base = "/usr/local/span_panel/"
pp = pprint.PrettyPrinter(indent=4)


class Config:
    def __init__(self, config_file):
        self.file = config_file
        with open(self.file, "r") as stream:
            try:
                self.c = yaml.load(stream, Loader=yaml.SafeLoader)

            except yaml.YAMLError as exc:
                print(exc)

    def getConfig(self):
        return self.c


# c = Config(directory_base + "/config/" + args.config_file)
c = Config(directory_base + "/config/" + "config.yml")
config = c.getConfig()


def main():
    parser = argparse.ArgumentParser(
        description="populatte influx with span panel data"
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

    pp.pprint(config)

    verbose = config["verbose"]
    if args.verbose:
        verbose = args.verbose

    with open(config["logging"]["log_config"], "rt") as f:
        lconfig = yaml.load(f.read(), Loader=yaml.SafeLoader)
    logging.config.dictConfig(lconfig)

    # create logger
    logger = logging.getLogger(config["logging"]["logger_name"])
    logger.debug(pp.pformat(config))
    logger.debug(pp.pformat(lconfig))


if __name__ == "__main__":
    main()
