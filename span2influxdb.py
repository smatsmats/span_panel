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


def push_data(measurement, data, tags={}):
    json_body = [
        {
            "measurement": measurement,
            "tags": tags,
            # we really should use the time from the call, but whatever
            # "time": datetime.utcfromtimestamp(int(data['ts'])).isoformat(),
            "time": datetime.utcnow().isoformat(),
            "fields": data
        }
    ]
    logger.debug(pp.pformat(json_body))
    logger.debug("Point Json:")
    ic.write_points(json_body)


def main():
    global logger
    global ic

    parser = argparse.ArgumentParser(description='populatte influx with span panel data')
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
                        help='get all circuits, branches, branches combined, and panel')
    parser.add_argument('--do_status',
                        dest='do_status',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get panel status')
    parser.add_argument('--do_circuits',
                        dest='do_circuits',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get all circuits')
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
    parser.add_argument('--do_branches',
                        dest='do_branches',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current branch conditions')
    parser.add_argument('--dump_branches',
                        dest='dump_branches',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current conditions')
    parser.add_argument('--dump_status',
                        dest='dump_status',
                        action='store_true',
                        default=False,
                        required=False,
                        help='get current status')
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
    parser.add_argument('-c', '--get_circuit',
                        dest='get_circuit',
                        nargs='+',
                        type=int,
                        default=None,
                        required=False,
                        help='get a circuit by tab slot, use both numbers if a dual breaker')
    parser.add_argument('-b', '--get_branch',
                        dest='get_branch',
                        type=int,
                        default=None,
                        required=False,
                        help='get a branch by tab slot, only returns singles or halves of dual breakers')
    parser.add_argument('-bc', '--get_branch_combo',
                        dest='get_branch_combo',
                        type=int,
                        default=None,
                        required=False,
                        help='get a branch by tab slot, use first tab slow for dual breakers')
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

    # create influx client
    ic = influx.InfluxClient(config)

    # this could be a lot quicker if we called panel to get
    # the instantjconsumption for all of the circuits
    panel = span.Panel(host=config['span']['host'],
                       extra_tab_pairs=config['span']['extra_tab_pairs'])

    if args.get_current is True:
        args.do_circuits = True
        args.do_panel = True
        args.do_branches = True
        args.do_status = True

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

    if args.dump_branches:
        b = panel.get_branches_combo()
        pp.pprint(b)

    if args.dump_status:
        s = panel.get_status()
        pp.pprint(s)

    if args.get_circuit is not None:
        circuits = panel.get_circuits()
        for circuit in circuits['circuits']:
            if circuits['circuits'][circuit]['tabs'] == args.get_circuit:
                pp.pprint(circuits['circuits'][circuit])

    if args.get_branch is not None:
        panel_dict = panel.get_panel()
        for branch in panel_dict['branches']:
            if branch['id'] == args.get_branch:
                pp.pprint(branch)

    if args.get_branch_combo is not None:
        branches = panel.get_branches_combo()
        pp.pprint(branches[args.get_branch_combo])

    if args.do_circuits:
        circuit_list = panel.list_circuits()
        for circuit_id in circuit_list:
            circuit = panel.get_circuits(circuitid=circuit_id)

            # try twice?
            if circuit is None:
                time.sleep(15)
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

            tabs = ','.join(str(c) for c in circuit['tabs'])
            tabs_word = 'tabs-' + tabs
            tags = {"circuit_name": circuit['name'],
                    "circuit_id": circuit['id'],
                    "tabs": tabs}
            push_data(circuit['name'], data2push, tags)
            push_data(tabs_word, data2push, tags)

    if args.do_status:
        fs = panel.get_status(flatten=True)
        push_data('panel_status', fs, tags={})

    if args.do_panel:
        # read panel
        data2push = {}
        panel_dict = panel.get_panel()
        for panelarg in panel_dict:

            value = panel_dict[panelarg]
            measurement = 'panel'

            # branches
            if panelarg == 'branches':
                for branch in panel_dict['branches']:
                    branchdata = {}
                    for brancharg in branch:
                        value = branch[brancharg]
                        if brancharg == 'relayState':
                            brancharg = 'relayState_bool'
                            if branch['relayState'] == 'CLOSED':
                                value = True
                            else:
                                # is the main relay state closed.
                                pp.pprint(panel_dict)
                                value = False
                        branchdata[brancharg] = value
                    b_measurement = 'branch-' + str(branch['id'])
                    push_data(b_measurement, branchdata, {})
# {   'exportedActiveEnergyWh': 314.5014953613281,
#     'id': 32,
#     'importedActiveEnergyWh': 283336.21875,
#     'instantPowerW': 2359.495849609375,
#     'relayState': 'CLOSED'}
            elif panelarg == 'feedthroughEnergy' or panelarg == 'mainMeterEnergy':
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

        push_data(measurement, data2push, {})

    if args.do_branches:
        # read panel combo
        branches = panel.get_branches_combo()

        for branchid in branches:
            branch = branches[branchid]

            # mess around with some values
            branch['instantPowerW'] = branch['instantPowerW'] * -1
            if branch['relayState'] == 'CLOSED':
                branch['relayState_bool'] = True
            else:
                branch['relayState_bool'] = False

            # create stuff for tags and measurements
            id_str = ','.join(str(c) for c in branch['ids'])
            measurement = 'branch-' + id_str
            tags = {'ids': id_str}

            # clean out some fields that will break influx
            branch.pop('ids', None)
            branch.pop('relayState', None)

            push_data(measurement, branch, tags)

# normal
# {   'exportedActiveEnergyWh': 314.5014953613281,
#     'id': 32,
#     'importedActiveEnergyWh': 283336.21875,
#     'instantPowerW': 2359.495849609375,
#     'relayState': 'CLOSED'}
# from branches_combo
#   30: {   'exportedActiveEnergyWh': 1917.3850708007812,
#            'id': 30,
#            'ids': [30, 32],
#            'importedActiveEnergyWh': 917139.03125,
#            'instantPowerW': -9.544904947280884,
#            'relayState': 'CLOSED'}}


if __name__ == "__main__":
    main()
