#!/usr/bin/python3

import subprocess

# could certainly be extended to iterate through other octets of address

first3 = '10.141.39.'
fourth_start = 1
fourth_stop = 255
print_dots = True

for n in range(fourth_start, fourth_stop):
    ip = "{}{}".format(first3, n)
    if print_dots:
        if n % 10 == 0:
            print(n, end='', flush=True)
        else:
            print('.', end='', flush=True)
        # add a newline after 50 (but not at the beginning or near the end)
        if (n-1) % 50 == 0 and n > 1 and n < 249:
            print()
#    print(ip)
    command = "curl -s -w '%{{http_code}}\n' -o /dev/null --request GET --url 'http://{}/api/v1/status'".format(ip)
    proc = subprocess.run(command, capture_output=True, shell=True)
    s_code = proc.stdout.decode('UTF-8').rstrip()
    if print_dots and s_code != '000':
        print()
    if s_code == '200':
        print('{} is a span panel ({})'.format(ip, s_code))
    elif s_code == '401':
        print('{} might be a span panel you\'re not authorized for ({})'.format(ip, s_code))
    elif s_code == '404':
        print('{} is something other than a span panel ({})'.format(ip, s_code))

print()
