"""
A module to get network interface stats
"""

import re
import time

# We have a global for the last stat - since we difference over ticks
last_tick = None
last_tick_time = time.time()

""" Get the module name """
def get_name():
    return 'Network Interface Stats'

""" Where does this module fit in to the metrics? """
def get_metric_path():
    return 'instances/{instance_group}/{instance_id}/net_iface'

""" Do the work """
def tick():

    # Globals
    global last_tick
    global last_tick_time

    curr = { }
    ret = [ ]

    # Open the file
    with open( '/proc/net/dev' ) as f:
        data = f.read()
        stats = re.findall( '.*\: .*', data )

    # Start handling the data
    for stat in stats:

        # Split it up
        cols = stat.split()

        # This full name
        name = get_metric_path() + '/' + cols[0][:-1]

        # If we have no bytes transferred we can skip it
        if cols[1] == '0' and cols[9] == '0':
            continue

        # Get the stats
        curr[name + '/rx_bytes'] = int( cols[1] )
        curr[name + '/rx_pkts'] = int( cols[2] )
        curr[name + '/rx_errs'] = int( cols[3] )
        curr[name + '/rx_drop'] = int( cols[4] )

        curr[name + '/tx_bytes'] = int( cols[9] )
        curr[name + '/tx_pkts'] = int( cols[10] )
        curr[name + '/tx_errs'] = int( cols[11] )
        curr[name + '/tx_drop'] = int( cols[12] )

    # If there is no last tick, set it to current
    if last_tick is None:
        last_tick = curr

    # Time difference
    time_diff = time.time() - last_tick_time

    # Now we will take the current counts, and subtract the previous ones, getting our differences
    for name, cur_val in curr.iteritems():

        # Find this metric, if it exists (we might have a new device)
        try:
            last = last_tick[name]
        except KeyError:
            last = cur_val

        # Skip if not exist
        if last is None:
            continue

        # Otherwise, get the diff
        ret += [{ 'metric': name, 'value': ( cur_val - last ) / time_diff }]

    # Last tick is now this
    last_tick = curr
    last_tick_time = time.time()

    # All done
    return ret
