import requests
import json

# The API heart
API_URL = "http://localhost:3000"

""" A utility to post data to an API endpoint """
def post_data( data, endpoint ):

    print " > post_data to {}\n{}".format( endpoint, data )

    ## XXX We are testing
    return
    resp = requests.post(
            url = API_URL + endpoint,
            data = json.dumps( data ),
            headers = {
                'content-type': 'application/json'
                }
            )

    # resp.status_code
    # resp.headers['content-type']
    # resp.encoding
    # resp.text
    # resp.json() # xform into a dict

    # Build something to send back
    return { 'code': resp.status_code, 'data': resp.json() }
