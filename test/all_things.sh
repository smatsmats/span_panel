#!/usr/bin/python3

import sys
import subprocess

args = [
        '--get_current',
        '--do_status',
        '--do_circuits',
        '--dump_circuits',
        '--do_panel',
        '--dump_panel',
        '--do_branches',
        '--dump_branches',
        '--dump_status',
        '--list_tabs_id_mapping',
        '--list_names_id_mapping',
        '--list_tabs_name_mapping',
        '-c 1',
        '-b 1',
        '-bc 1',
        '--get_clients',
        '--register'
       ]

executable = '/usr/local/span_panel/span2influxdb.py'

for a in args:
    print(a)
    cmd = "{} {}".format(executable, a)

    proc = subprocess.run(cmd, capture_output=True, shell=True)
    print(proc.stdout.decode('UTF-8'))
#    print(proc.stdout.decode('UTF-8').rstrip()
