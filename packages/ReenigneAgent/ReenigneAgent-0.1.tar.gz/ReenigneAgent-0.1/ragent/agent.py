""" The main agent entry point """
import sys
import argparse
import module
import time
import threading
from utils import config

##
## Some simple constants
##

## Tick rate is set to 60 seconds here; the API does not handle data more often
## than one sample per metric per minute.  If one sample for a metric is sent,
## followed by another, the latter will overwrite the first.
TICK_RATE = 60

""" Main loop """
def loop():
    while True:

        # Get the current time
        start = time.time()

        # Do our ticks
        module.tick()

        # Sleep for up to 60 sec
        end = time.time()
        time.sleep( max( TICK_RATE - end - start, TICK_RATE ) )

""" Entry point by the reenigne-monitoring-agent script """
def main():

    # Read the arguments
    parser = argparse.ArgumentParser( description = 'Parse arguments' )

    # Config file
    parser.add_argument( '--config', '-c',
            action = 'store',
            default = '/etc/reenigne-monitoring-agent.json',
            help = 'path to the configuration file to use'
    )

    # Print version
    parser.add_argument( '--version', '-v',
            action = 'store_true',
            help = 'print version info and exit'
    )

    # The args
    args = parser.parse_args()

    # Verison and exit?
    if args.version:
        print "Hello!"
        return

    # Read the config
    config.read_config( args.config )

    # Get the config data, check for api token
    if config.data['api_token'] == '':
        print "API Token is not set, please set it in the " + args.config
        return

    # Load modules
    module.load_modules()

    # Do the loop
    loop()

""" Entry point """
if __name__ == '__main__':
    main()
