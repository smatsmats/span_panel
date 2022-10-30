# span_panel
my span panel

Uses information from:
https://gist.github.com/hyun007/c689fbed10424b558f140c54851659e3

What:

Pulls from a span panel and pushes to a db.  In this case InfluxDB.

Stuff:
<UL>
<LI>circuits - info on the circuit, does not include 220v circuit for solar in
<LI>branches - info from branches, does not include the second tab in a doubled branch
<LI>panel - information about the panel and grid status
<LI>status - information about the system and it's status
</UL>

TODO:
<UL>
<LI>Finish register new client, it's not working currently
<LI>Return capability to use other config files
</ul>
