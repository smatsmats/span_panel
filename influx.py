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

pp = pprint.PrettyPrinter(indent=4)

directory_base = "/usr/local/weatherlink2influxdb/"


class InfluxClient:
    def __init__(self):
        self.retpol = myconfig.config['influxdb']['retention_policy']
        self.dbclient = InfluxDBClient(username=myconfig.config['influxdb']['username'],
                                       password=myconfig.config['influxdb']['password'],
                                       host=myconfig.config['influxdb']['host'],
                                       port=myconfig.config['influxdb']['port'])
        self.dbclient.switch_database(myconfig.config['influxdb']['db_name'])

# qresults = dbclient.query('SELECT "temp_in" FROM "sc6_wx"."autogen"."289367" WHERE time > now() - 4d')
#                            SELECT "time_in" FROM "sc6_wx_test"."autogen"."289367" WHERE time > now() - 4d
    def query(self, field, measure, whererange=None):

        if whererange is None:
            whererange = "time > now() - 4d"
        query = "SELECT {} FROM \"{}\".\"{}\".\"{}\" WHERE {}".format(
            field, myconfig.config['influxdb']['db_name'], self.retpol,
            measure, whererange)
        mylogger.logger.debug(query)
        print(query)
        qresults = self.dbclient.query(query)
        pp.pprint(qresults)

    def write_points(self, json_body):
        self.json_body = json_body
        self.dbclient.write_points(json_body)


def main():
    parser = argparse.ArgumentParser(description='influx client.')
    parser.add_argument('--query',
                        dest='query',
                        action='store_true',
                        default=False,
                        required=False,
                        help='query')
    parser.add_argument('--config_file',
                        dest='config_file',
                        default='config.yml',
                        required=False,
                        help='name of config file')
    parser.add_argument('--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='should we be really verbose, huh, should we?')
    args = parser.parse_args()

    c = Config(directory_base + "/config/" + args.config_file)
    config = c.getConfig()

    verbose = config['verbose']
    if args.verbose:
        verbose = args.verbose

    ic = InfluxClient(config)

    if args.query:
        ic.query('time_in', '289367')


if __name__ == "__main__":
    main()
