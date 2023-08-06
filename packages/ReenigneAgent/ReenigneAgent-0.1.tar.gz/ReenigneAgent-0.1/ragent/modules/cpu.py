"""
A module to get the CPU stats of the current system
"""

import re

# We have a global for the last stat - since we average over ticks
last_tick = None

""" Get the module name """
def get_name():
    return 'CPU Usage'

""" Where does this module fit in to the metrics? """
def get_metric_path():
    return 'instances/{instance_group}/{instance_id}/cpu_usage'

""" Get all the CPU time data """
def cpu_times():

    # Open the file, read our stats
    with open( '/proc/stat' ) as f:
        data = f.read()

        # We don't want the "cpu " line, which is the aggregate of all
        # We'd rather report/store the things we can aggregate on our own
        stats = re.findall( 'cpu\d? .*', data )

    # Our return value
    ret = [ ]

    # Now for each, we want to split them into their groups
    for i in stats:

        # Split them by space, we'll get the individual stats
        args = i.split()

        # Build this tuple
        info = {
                'name': get_metric_path() + '/' + args.pop( 0 ),
                'user': int( args.pop( 0 ) ),
                'nice': int( args.pop( 0 ) ),
                'system': int( args.pop( 0 ) ),
                'idle': int( args.pop( 0 ) ),
                'iowait': int( args.pop( 0 ) ),
                'irq': int( args.pop( 0 ) ),
                'softirq': int( args.pop( 0 ) )
                }

        # Is there more info?
        if len( args ):
            info['steal'] = int( args.pop( 0 ) )

        if len( args ):
            info['guest'] = int( args.pop( 0 ) )

        if len( args ):
            info['guest_nice'] = int( args.pop( 0 ) )

        # Append this
        ret.append( info )

    return ret

""" Get all the CPU percentage data """
def cpu_percent():

    # We'll set the last tick here
    global last_tick

    # Get the CPU times
    times = cpu_times()

    # If we have no last tick, we can only report zeros or average since boot
    if last_tick is None:
        last_tick = times

    # Now lets figure out the differences in each
    diffs = [ ]

    for i in range( 0, len( times ) ):

        # Convenience
        cur = times[i]
        old = last_tick[i]

        # Calculate totals
        cur_total = 0
        old_total = 0

        # And diffs
        diff = { }

        for meter in [ 'user', 'nice', 'system',
                'idle', 'iowait', 'irq', 'softirq',
                'steal', 'guest', 'guest_nice' ]:
            if meter in cur:
                diff[meter] = cur[meter] - old[meter]
                old_total += old[meter]
                cur_total += cur[meter]

        # Now how much usage was there?
        old_used = old_total - old['idle']
        cur_used = cur_total - cur['idle']

        # And differences again
        diff_idle = cur['idle'] - old['idle']
        diff_total = cur_total - old_total
        diff_usage = 100 * ( diff_total - diff_idle ) / float( diff_total if diff_total > 0 else 1 )

        diffs.append({ 'metric': cur['name'], 'value': diff_usage })

    # Set the last tick
    last_tick = times
    return diffs

""" Actual work is done in here """
def tick():

    # Get the percent data
    return cpu_percent()
