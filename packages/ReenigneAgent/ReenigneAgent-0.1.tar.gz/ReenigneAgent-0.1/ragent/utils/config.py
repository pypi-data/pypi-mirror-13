import json
import os.path

# The actual config dict
data = { }

# The default configuration
DEFAULT_CONFIG = {
        'api_token': '',
        'api_endpoint': 'https://monitor.reenigne.net',
        'variables': {
            'instance_group': 'my-group-dc-etc',
            'instance_id': 'my-example-com',
            },
        'modules': [
            'cpu',
            'memory',
            'loadavg',
            'network'
            ]
        }

""" Read the config """
def read_config( path ):

    # We modify the global data
    global data

    # Expand the path
    path = os.path.expanduser( path )

    # First ensure a config exists
    ensure_config( path )

    # And open it
    with open( path ) as f:
        data = json.load( f )

""" Ensure the config file exists, and has basic data """
def ensure_config( path ):

    # Exists?
    if not os.path.isfile( path ):
        with open( path, 'wb' ) as f:
            json.dump( DEFAULT_CONFIG, f, indent = 2, separators = ( ',', ': ' ) )
