"""
A module to get the load average on the current system
"""

""" Get the module name """
def get_name():
    return 'Load Average'

""" Where does this module fit in to the metrics? """
def get_metric_path():
    return 'instances/{instance_group}/{instance_id}/loadavg'

""" Do the work """
def tick():

    ret = [ ]

    # Full metric path name
    path = get_metric_path() + '/'

    # Open the file
    with open( '/proc/loadavg' ) as f:
        line = f.read().split()
        ret.append({ 'metric': path + '1min', 'value': float( line[0] ) })
        ret.append({ 'metric': path + '5min', 'value': float( line[1] ) })
        ret.append({ 'metric': path + '10min', 'value': float( line[2] ) })

    return ret
