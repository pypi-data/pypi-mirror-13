import pkgutil
import json
import requests
import modules
import time
from utils import config

# Our loaded modules
loaded_modules = { }

# Our list of requests to send, in case of errors
queued_requests = [ ]

""" Load all our modules """
def load_modules():

    # Get the list of modules we have
    all_modules = pkgutil.iter_modules( modules.__path__ )

    # Get the config
    cfg = config.data

    # Go through the modules in our config
    for m in cfg['modules']:
        loaded_modules[m] = False

    # Now try to load the ones we have
    for loader, name, _ in all_modules:
        if m in loaded_modules:
            loaded_modules[name] = loader.find_module( name ).load_module( name )

    # Now go through all modules again, and make sure we warn about missing ones
    for k, v in loaded_modules.iteritems():
        if v is False:
            print "Couldn't find module " + k

""" Do the main ticks """
def tick():

    # Build the list of samples to send to the api
    data = [ ]

    # And the config
    cfg = config.data

    # Get all the data from our modules
    for name, m in loaded_modules.iteritems():
        data += m.tick()

    # We now have to replace all variables in the names
    # instance_id
    # instance_group
    for i in data:
        for k, v in cfg['variables'].iteritems():
            i['metric'] = i['metric'].replace( '{' + k + '}', v )

    # Build the full data
    data = {
            'auth_token': cfg['api_token'],
            'data': data,
            'timestamp': time.time()
            }

    # Send this data to the API
    url = cfg['api_endpoint'] + '/api/v1/samples'
    headers = { 'Content-Type': 'application/json' }

    # Add this request to the list of samples to send
    queued_requests.append( data )

    # Now iterate through all requests
    for v in queued_requests[:]:

        # Try to send this off to the api
        try:
            res = requests.post( url, data = json.dumps( v ), headers = headers )

            # If it worked, we can remove it from the queue
            if res.status_code >= 200 and res.status_code < 300:
                queued_requests.remove( v )

            print res.headers
            print res.status_code
            print res.json()

        except requests.exceptions.RequestException as e:
            print e
