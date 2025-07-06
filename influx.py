#!/usr/bin/python3

import pprint
from influxdb import InfluxDBClient

import mylogger
import myconfig

pp = pprint.PrettyPrinter(indent=4)


class InfluxClient:
    def __init__(self):
        self.retpol = myconfig.config["influxdb"]["retention_policy"]
        self.dbclient = InfluxDBClient(
            username=myconfig.config["influxdb"]["username"],
            password=myconfig.config["influxdb"]["password"],
            host=myconfig.config["influxdb"]["host"],
            port=myconfig.config["influxdb"]["port"],
        )
        self.dbclient.switch_database(myconfig.config["influxdb"]["db_name"])

    def query(self, field, measure, whererange=None):

        if whererange is None:
            whererange = "time > now() - 4d"
        query = 'SELECT {} FROM "{}"."{}"."{}" WHERE {}'.format(
            field,
            myconfig.config["influxdb"]["db_name"],
            self.retpol,
            measure,
            whererange,
        )
        mylogger.logger.debug(query)
        print(query)
        qresults = self.dbclient.query(query)
        pp.pprint(qresults)

    def write_points(self, json_body):
        self.json_body = json_body
        self.dbclient.write_points(json_body)


def main():
    exit(0)


if __name__ == "__main__":
    main()
