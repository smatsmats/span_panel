# span_panel
my span panel

Uses information from:
https://gist.github.com/hyun007/c689fbed10424b558f140c54851659e3

What:

Pulls from a span panel and pushes to a db.  in this case InfluxDB.

Stuff:

circuits - info the circuit, does not include 220v circuit for solar in
branches - info from branches, does not include the second tab in a doubled branch
panel - information about the panel and grid status
status - information about they system and it's status

TODO:

return capability to use other config files
finish register new client, it's not working currently
