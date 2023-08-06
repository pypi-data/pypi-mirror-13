"""
A module to get the memory stats of the current system
"""

""" Get the module name """
def get_name():
    return 'Memory Usage'

""" Where does this module fit in to the metrics? """
def get_metric_path():
    return 'instances/{instance_group}/{instance_id}/memory'

""" Get memory """
def get_mem():

    # Defaults
    total = free = buffers = cached = active = inactive = 0
    swap_total = swap_free = 0

    # Read the file
    with open( '/proc/meminfo' ) as f:
        for line in f:
            if line.startswith( 'MemTotal:' ):
                total = int( line.split()[1] )

            elif line.startswith( 'MemFree:' ):
                free = int( line.split()[1] )

            elif line.startswith( 'Buffers:' ):
                buffers = int( line.split()[1] )

            elif line.startswith( 'Cached:' ):
                cached = int( line.split()[1] )

            elif line.startswith( 'Active:' ):
                active = int( line.split()[1] )

            elif line.startswith( 'Inactive:' ):
                inactive = int( line.split()[1] )

            elif line.startswith( 'SwapFree:' ):
                swap_total = int( line.split()[1] )

            elif line.startswith( 'SwapTotal:' ):
                swap_free = int( line.split()[1] )

    # Build the dict
    return {
            'total': total,
            'avail': free + buffers + cached,
            'used': total - free,
            'free': free,
            'active': active,
            'inactive': inactive,
            'buffers': buffers,
            'cached': cached,

            'swap_free': swap_free,
            'swap_total': swap_total,
            'swap_used': swap_total - swap_free
            }

""" Actual work is done in here """
def tick():

    # Get the data
    mem = get_mem()

    # The full metric path name
    path = get_metric_path() + '/'

    # Build some return data
    ret = [
            { 'metric': path + 'total', 'value': mem['total'] },
            { 'metric': path + 'available', 'value': mem['avail'] },
            { 'metric': path + 'used', 'value': mem['used'] },
            { 'metric': path + 'free', 'value': mem['free'] },
            { 'metric': path + 'cached', 'value': mem['cached'] },

            { 'metric': path + 'swap_total', 'value': mem['swap_total'] },
            { 'metric': path + 'swap_used', 'value': mem['swap_used'] },
            { 'metric': path + 'swap_free', 'value': mem['swap_free'] },
            ]

    return ret
