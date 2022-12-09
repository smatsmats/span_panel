#!/usr/bin/python3

import requests
import pprint
import time
import json
import math
from requests.exceptions import HTTPError

import myconfig
import mylogger

pp = pprint.PrettyPrinter(indent=4)


session = requests.Session()
verbose = 0

calls = 0


def flatten_json(nested_json):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out


def make_request(method, url, payload=None):
    global dry_run
    global session
    global calls

    token_string = "Bearer " + myconfig.config['span']['auth']['token']
    headers = {'authorization': token_string,
               'accept': "application/json",
               'content-type': "application/json"}

#    mylogger.logger.debug("payload {}".format(json.dumps(payload)))
    if verbose:
        pp.pprint("method", method, "url", url,
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
            # print(f'HTTP error occurred: {http_err}')
            # print(f'text: {response.text}')
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


class Panel:
    def __init__(self, host, extra_tab_pairs=None):
        self.host = host
        self.api_version = 'api/v1'
        self.pop_id_mappings()
        self.extra_tab_pairs = extra_tab_pairs
        # the solar stuff is not included in circuts, so we have
        # to add it ourselves
        if self.extra_tab_pairs is not None:
            for pair in self.extra_tab_pairs:
                self.tab_pairs.append(pair)

    def get_status(self, flatten=False):
        method = 'GET'
        url_stub = 'status'
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        r = make_request(method, url, payload=None)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            print(r.status_code)
            print(r.reason)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        s = r.json()
        if flatten:
            return(flatten_json(s))
        else:
            return(s)

    def get_panel(self):
        method = 'GET'
        url_stub = 'panel'
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        r = make_request(method, url, payload=None)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            print(r.status_code)
            print(r.reason)
#            return(None)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        return(r.json())

    def is_panel_on_grid(self):
        p = self.get_panel()
        if p['currentRunConfig'] == 'PANEL_ON_GRID':
            return True
        else:
            return False

    def panel_instantgridpowerw(self):
        p = self.get_panel()
        return(p['instantGridPowerW'])

    def get_branches(self):
        b_dict = {}
        p = self.get_panel()
        for branch in p['branches']:
            b_dict[branch['id']] = branch
        return(b_dict)

    def combine_branches(self, branch_a, branch_b):
        branch_out = branch_a
        for arg in ['exportedActiveEnergyWh',
                    'importedActiveEnergyWh',
                    'instantPowerW']:
            branch_out[arg] = branch_a[arg] + branch_b[arg]
        branch_out['ids'] = [branch_a['id'], branch_b['id']]
        return(branch_out)

    def get_branches_combo(self):
        b_dict = {}
        p = self.get_panel()
        # first populate brances to new dickt
        for branch in p['branches']:
            b_dict[branch['id']] = branch
        keys_to_pop = []
        for branchid in b_dict:
            # dupe id into ids for non-combined branches
            b_dict[branchid]['ids'] = [branchid]
            for pair in self.tab_pairs:
                if branchid in pair:
                    a = b_dict[int(pair[0])]
                    b = b_dict[int(pair[1])]
                    if 'combined' in a.keys() or 'combined' in b.keys():
                        continue
                    combined = self.combine_branches(a, b)
                    combined['combined'] = True
                    b_dict[pair[0]] = combined
                    keys_to_pop.append(pair[1])
        ukeys_to_pop = list(set(keys_to_pop))
        for k in ukeys_to_pop:
            b_dict.pop(k)
        return(b_dict)

# not the branch part:
#    'currentRunConfig': 'PANEL_ON_GRID',
#    'dsmGridState': 'DSM_GRID_UP',
#    'dsmState': 'DSM_ON_GRID',
#    'feedthroughEnergy': {   'consumedEnergyWh': -170847.5076028611,
#                             'producedEnergyWh': 100396.91888427734},
#    'feedthroughPowerW': 185.8552309796214,
#    'gridSampleEndMs': 2321461,
#    'gridSampleStartMs': 2321447,
#    'instantGridPowerW': -2474.18359375,
#    'mainMeterEnergy': {   'consumedEnergyWh': 166966.03515625,
#                           'producedEnergyWh': 253956.8828125},
#    'mainRelayState': 'CLOSED'}

    def get_circuits(self, circuitid=None):
        method = 'GET'
        url_stub = 'circuits'
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        if circuitid is not None:
            url = url + '/' + circuitid
        r = make_request(method, url, payload=None)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            return(None)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        return(r.json())

    def get_circuit_by_tab(self, tab):
        ret = self.get_circuits(self.tabs_id_mapping[tab])
        return(ret)

    def get_circuit_by_name(self, name):
        ret = self.get_circuits(self.names_id_mapping[name])
        return(ret)

    def pop_id_mappings(self):
        self.tabs_id_mapping = {}
        self.names_id_mapping = {}
        self.tabs_name_mapping = {}
        self.circuit_list = []
        self.tab_pairs = []
        spaces = self.get_circuits()
        for space in spaces:
            for circuit in spaces[space]:
                c = spaces[space][circuit]
                self.circuit_list.append(c['id'])
                tab_string = ','.join(str(c) for c in c['tabs'])
                self.tabs_name_mapping[tab_string] = c['name']
                if len(c['tabs']) > 1:
                    self.tab_pairs.append(c['tabs'])
                    tab_string = ','.join(str(c) for c in c['tabs'])
                for n in c['tabs']:
                    self.tabs_id_mapping[n] = c['id']
                    self.names_id_mapping[c['name']] = c['id']

    def list_tabs_id_mapping(self):
        for n in sorted(self.tabs_id_mapping.keys()):
            print(n, '--', self.tabs_id_mapping[n])

    def get_tabs_id_mapping(self):
        return(self.tabs_id_mapping)

    def list_names_id_mapping(self):
        for name in sorted(self.names_id_mapping.keys()):
            print(name, '--', self.names_id_mapping[name])

    def get_names_id_mapping(self):
        return(self.names_id_mapping)

    # names_first is easier for human to read instead of tab order
    def list_tabs_name_mapping(self, names_first=False):
        for str_tab in self.tabs_name_mapping:
            if names_first:
                print(self.tabs_name_mapping[str_tab], '--', str_tab)
            else:
                print(str_tab, '--', self.tabs_name_mapping[str_tab])

    def get_tabs_name_mapping(self):
        return(self.tabs_name_mapping)

    def list_circuits(self):
        return(self.circuit_list)

    def get_instantw(self, circuitid):
        circuit = self.get_circuits(circuitid=circuitid)
        return(circuit['instantPowerW'])

    def get_consumedenergywh(self, circuitid):
        circuit = self.get_circuits(circuitid=circuitid)
        return(circuit['consumedEnergyWh'])

    def get_name(self, circuitid):
        circuit = self.get_circuits(circuitid=circuitid)
        return(circuit['name'])

    def get_tab_pairs(self):
        return(self.tab_pairs)

    def get_clients(self, client=None):
        method = 'GET'
        url_stub = 'auth/clients'
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        if client is not None:
            url = url + '/' + client
        r = make_request(method, url, payload=None)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            print(r.status_code)
            print(r.reason)
            return(None)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        s = r.json()
        return(s)

    def add_clients(self, client, desc):
        method = 'POST'
        url_stub = 'auth/register'
        data = {"name": client, "description": desc}
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        r = make_request(method, url, payload=data)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            print(r.status_code)
            print(r.reason)
            return(None)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        s = r.json()
        return(s)

    def delete_clients(self, client):
        method = 'DELETE'
        url_stub = 'auth/clients'
        url = 'http://{}/{}/{}'.format(self.host, self.api_version, url_stub)
        url = url + '/' + client
        r = make_request(method, url, payload=None)

        # see if the return code is 2XX
        if math.trunc(r.status_code / 100) != 2:
            print(r.status_code)
            print(r.reason)
            return(None)

        if verbose and r.status_code != 204:
            pp.pprint(r)

        if verbose:
            pp.pprint(r.json())

        s = r.json()
        return(s)


def main():
    host = myconfig.config['span']['host']
    panel = Panel(host=host, extra_tab_pairs=[[30, 32]])
#    s = panel.get_status()
#    pp.pprint(s)
#    p = panel.get_panel()
#    pp.pprint(p)
#    pf = flatten_json(p)
#    pp.pprint(pf)
#    on_grid = panel.is_panel_on_grid()
#    pp.pprint(on_grid)
#    juice = panel.panel_instantgridpowerw()
#    print(juice)
#    c = panel.get_circuits()
#    pp.pprint(c)
#    c = panel.get_circuits(circuitid='5585e4754180409a8222f69b61142469')
#    pp.pprint(c)
#    panel.list_tabs_id_mapping()
#    panel.list_names_id_mapping()
#    cl = panel.list_circuits()
#    pp.pprint(cl)
#    c = panel.get_circuit_by_tab(13)
#    pp.pprint(c)
#    c = panel.get_circuit_by_name('Laundry room outlets')
#    pp.pprint(c)
#    juice = panel.get_instantw(circuitid='5585e4754180409a8222f69b61142469')
#    pp.pprint(juice)
#    juice =
# panel.get_consumedenergywh(circuitid='5585e4754180409a8222f69b61142469')
#    pp.pprint(juice)
#    nom = panel.get_name(circuitid='5585e4754180409a8222f69b61142469')
#    pp.pprint(nom)
#    tp = panel.get_tab_pairs()
#    pp.pprint(tp)
#    br = panel.get_branches()
#    pp.pprint(br)
#    brc = panel.get_branches_combo()
#    pp.pprint(brc)

    print("get_clients()")
    clients = panel.get_clients()
    pp.pprint(clients)

    print("add_clients()")
    client = panel.add_clients('bib_api_user', 'bib api user')
    pp.pprint(client)

    print("get_clients()")
    clients = panel.get_clients()
    pp.pprint(clients)

    print("get_clients('bib_api_user')")
    clients = panel.get_clients('bib_api_user')
    pp.pprint(clients)
    print("get_clients('dashboard')")
    clients = panel.get_clients('dashboard')
    pp.pprint(clients)


if __name__ == "__main__":
    main()
