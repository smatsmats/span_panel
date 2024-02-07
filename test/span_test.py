#!/usr/bin/python3

import requests
import pprint
import time
import json
import math
import sys
from requests.exceptions import HTTPError

import myconfig
import mylogger
import span

pp = pprint.PrettyPrinter(indent=4)

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
