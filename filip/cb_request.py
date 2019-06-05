import requests

"""
Helper functions for HTTP requests
"""

HEADER_ACCEPT_JSON = {'Accept': 'application/json'}
HEADER_ACCEPT_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT_JSON = {'Content-Type': 'application/json'}
HEADER_CONTENT_PLAIN = {'Content-Type': 'text/plain'}



def pretty_print_request(req):
    print('{}\n{}\n{}\n\nBODY:{}\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        '---------------------------'
    ))

def check_response_ok(response, request_type):
    """checks if HTTP response code is less than 400"""
    if not response.ok:
        msg = str(request_type) + " request returned error status '" \
              + str(response.status_code) + " (" + str(response.reason) + ")'"
        print (msg)
        print ("request content:")
        pretty_print_request(response.request)
        return False
    else:
        print (str(request_type) + " ok")
        return True

def post(url, head, body, autho=None, return_headers=False):
    response = requests.post(url, headers=head, auth=autho, data=body)
#    pretty_print_request(response.request)
    check_response_ok(response, "POST")
    if return_headers:
        return response.headers

def put(url, head=None, data=None, autho=None):
    response = requests.put(url, headers=head,auth=autho, data=data)
    check_response_ok(response, "PUT")

def get(url, head, parameters=None, autho=None):
    response  = requests.get(url, headers=head,auth=autho, params=parameters)
#    pretty_print_request(response.request)
    if check_response_ok(response, "GET"):
        return response.text

def patch(url, head, body, autho):
    response = requests.patch(url, data=body, headers=head, auth=autho)
    check_response_ok(response, "PATCH")

def delete(url, head, autho=None):
    response = requests.delete(url, headers=head, auth=autho)
#    pretty_print_request(response.request)
    check_response_ok(response, "DELETE")
