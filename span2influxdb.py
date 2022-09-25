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
from datetime import datetime
from datetime import timedelta

# local stuff
import influx
import span
import myconfig

pp = pprint.PrettyPrinter(indent=4)

session = requests.Session()
verbose = 0
directory_base = "/usr/local/span_panel/"

relay_state_map = {'CLOSED': 1.0,
                   'OPEN': 0.0}
calls = 0


def make_request(method, url, payload=None):
    global dry_run
    global session
    global calls

#    token_string = "Bearer " + acct_info[account]['token']
#    headers = {'authorization': token_string,
#               'content-type': "application/json"}
    headers = {}

    if verbose:
        print("method", method, "url", url,
              "headers", headers, "payload", payload)

    response = None
    c = 0
    max = 10
    while response is None and c < max:
        try:
            response = session.request(method=method,
                                       url=url,
                                       headers=headers,
                                       data=json.dumps(payload))
            calls = calls + 1

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
#            print(f'text: {response.text}')
            if response.status_code == 401:
                sys.exit()
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            if verbose:
                print('Success!')
        if response is None:
            c = c + 1
            wait = c * 20
            print("timed out, going to wait %d second and try again" % (wait))
            time.sleep(wait)

    return response


def main():
    parser = argparse.ArgumentParser(description='populatte influx with span panel data')

#    parser.add_argument('--query',
#                        dest='query',
#                        action='store_true',
#                        default=False,
#                        required=False,
#                        help='query')
#    parser.add_argument('--push2influxdb',
#                        dest='push2infoxdb',
#                        action='store_true',
#                        default=False,
#                        required=False,
#                        help='push to influxdb')
    parser.add_argument('--get_current',
                        dest='get_current',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--dump_circuits',
                        dest='dump_circuits',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--do_panel',
                        dest='do_panel',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--dump_panel',
                        dest='dump_panel',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--list_tabs_id_mapping',
                        dest='list_tabs_id_mapping',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--list_names_id_mapping',
                        dest='list_names_id_mapping',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--list_tabs_name_mapping',
                        dest='list_tabs_name_mapping',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
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

    c = myconfig.Config(directory_base + "/config/" + args.config_file)
    config = c.getConfig()

    verbose = config['verbose']
    if args.verbose:
        verbose = args.verbose

    with open(config['logging']['log_config'], 'rt') as f:
        lconfig = yaml.load(f.read(), Loader=yaml.SafeLoader)
    logging.config.dictConfig(lconfig)

    # create logger
    logger = logging.getLogger(config['logging']['logger_name'])
    logger.debug(pp.pformat(config))
    logger.debug(pp.pformat(lconfig))

    ic = influx.InfluxClient(config)

    # this could be a lot quicker if we called panel to get
    # the instantjconsumption for all of the circuits
    panel = span.Panel(host=config['span']['host'],
                       extra_tab_pairs=config['span']['extra_tab_pairs'])

    if args.list_tabs_id_mapping:
        panel.list_tabs_id_mapping()

    if args.list_names_id_mapping:
        panel.list_names_id_mapping()

    if args.list_tabs_name_mapping:
        panel.list_tabs_name_mapping()

    if args.dump_circuits:
        c = panel.get_circuits()
        pp.pprint(c)

    if args.dump_panel:
        p = panel.get_panel()
        pp.pprint(p)

    if args.get_current:
        circuit_list = panel.list_circuits()
        for circuit_id in circuit_list:
            # print(circuit_id)
            # instantw = panel.get_instantw(circuitid='5585e4754180409a8222f69b61142469')
            # consumedenergywh = panel.get_consumedenergywh(circuitid='5585e4754180409a8222f69b61142469')
            # nom = panel.get_name(circuitid='5585e4754180409a8222f69b61142469')
            circuit = panel.get_circuits(circuitid=circuit_id)

            # try twice?
            if circuit is None:
                time.sleep(45)
                circuit = panel.get_circuits(circuitid=circuit_id)
                if circuit is None:
                    print("error from getting circuits, bailing")
                    logger.debug("error from getting circuits, bailing")
                    sys.exit()

            # tabs = ' '.join(str(c) for c in circuit['tabs'])
            data2push = {}
            for arg in circuit:
                value = circuit[arg]
                if arg in ['id',
                           'name',
                           'is_user_controllable',
                           'priority',
                           'is_sheddable',
                           'is_never_backup',
                           'tabs']:
                    continue

                # some stupid conversions
                if arg == 'relayState':
                    value = relay_state_map[value]
                if arg == 'instantPowerW':
                    value = - value

                data2push[arg] = value

                # add an extra frield for tabs as a string
                if arg == 'tabs':
                    arg = 'tabs_str'
                    value = ','.join(value)

                data2push[arg] = value

# id b74f5a75fe544b07a11a50d6948568e2
# name Disposal, kitchen outlet, front hall
# relayState CLOSED
# instantPowerW 0.0
# instantPowerUpdateTimeS 1663431256
# producedEnergyWh 39.83546447753906
# consumedEnergyWh 50.25605773925781
# energyAccumUpdateTimeS 1663431250
# tabs [28]
# priority NON_ESSENTIAL
# is_user_controllable True
# is_sheddable False
# is_never_backup False

            try:
                tabs = ','.join(str(c) for c in circuit['tabs'])
                tabs_word = "tabs-{}".format(tabs)
                json_body = [
                    {
                        "measurement": circuit['name'],
                        "tags": {
                            "circuit_name": circuit['name'],
                            "circuit_id": circuit['id'],
                            "tabs": tabs,
                        },
                        # we really should use the time from the call, but whatever
                        # "time": datetime.utcfromtimestamp(int(data['ts'])).isoformat(),
                        "time": datetime.utcnow().isoformat(),
                        "fields": data2push
                        }
                ]
                json_body_tabs = [
                    {
                        "measurement": tabs_word,
                        "tags": {
                            "circuit_name": circuit['name'],
                            "circuit_id": circuit['id'],
                            "tabs": tabs,
                        },
                        # we really should use the time from the call, but whatever
                        # "time": datetime.utcfromtimestamp(int(data['ts'])).isoformat(),
                        "time": datetime.utcnow().isoformat(),
                        "fields": data2push
                        }
                ]
            except KeyError:
                print("not everything is in the circuit definition")
                pp.pprint(circuit)
            else:
                logger.debug(pp.pformat(json_body))
                logger.debug("Point Json:")
                ic.write_points(json_body)
                logger.debug(pp.pformat(json_body_tabs))
                logger.debug("Point Json:")
                ic.write_points(json_body_tabs)

    if args.do_panel:
        # read panel
        data2push = {}
        panel_dict = panel.get_panel()
        for panelarg in panel_dict:

            # for now skip branches
            if panelarg == 'branches':
                continue
            value = panel_dict[panelarg]

            if panelarg == 'feedthroughEnergy' or panelarg == 'mainMeterEnergy':
                panelarg_save = panelarg
                for conpro in panel_dict[panelarg_save]:
                    value = panel_dict[panelarg_save][conpro]
                    panelarg = '{}_{}'.format(panelarg_save, conpro)
                    data2push[panelarg] = value
            elif panelarg == 'mainRelayState':
                if panel_dict[panelarg] == 'CLOSED':
                    value = True
                else:
                    value = False
                panelarg = 'mainRelayState_bool'
            elif panelarg == 'currentRunConfig':
                if panel_dict[panelarg] == 'PANEL_ON_GRID':
                    value = True
                else:
                    value = False
                panelarg = 'currentRunConfig_bool'
            elif panelarg == 'dsmGridState':
                if panel_dict[panelarg] == 'DSM_GRID_UP':
                    value = True
                else:
                    value = False
                panelarg = 'dsmGridState_bool'
            elif panelarg == 'dsmState':
                if panel_dict[panelarg] == 'DSM_ON_GRID':
                    value = True
                else:
                    value = False
                panelarg = 'dsmState_bool'

            data2push[panelarg] = value

        json_body = [
            {
                "measurement": 'panel',
                "tags": {
                    # "circuit_name": circuit['name'],
                    # "circuit_id": circuit['id'],
                },
                # we really should use the time from the call, but whatever
                # "time": datetime.utcfromtimestamp(int(data['ts'])).isoformat(),
                "time": datetime.utcnow().isoformat(),
                "fields": data2push
            }
        ]
        logger.debug(pp.pformat(json_body))
        logger.debug("Point Json:")
        ic.write_points(json_body)


if __name__ == "__main__":
    main()
