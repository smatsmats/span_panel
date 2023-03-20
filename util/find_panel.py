#!/usr/bin/python3

import subprocess

# could certainly be extended to iterate through other octets of address

first3 = '10.141.39.'
fourth_start = 1
fourth_stop = 255

for n in range(fourth_start, fourth_stop):
    ip = "{}{}".format(first3, n)
#    print(ip)
    command = "curl -s -w '%{{http_code}}\n' -o /dev/null --request GET --url 'http://{}/api/v1/status'".format(ip)
    proc = subprocess.run(command, capture_output=True, shell=True)
    s_code = proc.stdout.decode('UTF-8').rstrip()
    if s_code == '200':
        print('{} is a span panel ({})'.format(ip, s_code))
    elif s_code == '401':
        print('{} might be a span panel you\'re not authorized for ({})'.format(ip, s_code))
    elif s_code == '404':
        print('{} is something other than a span panel ({})'.format(ip, s_code))
