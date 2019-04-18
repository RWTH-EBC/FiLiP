import requests


def pretty_print_request(req):
    print('{}\n{}\n{}\n\nBODY:{}\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        '---------------------------'
    ))

def check_response_ok(response, request_type):
    if not response.ok:
        msg = str(request_type) + " request returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'"
        print (msg)
        print ("request content:")
        pretty_print_request(response.request)
        return False
    else:
        print (str(request_type) + " ok")
        return True

def post(url, head, body, autho=None, return_headers=False):
    response = requests.post(url, headers=head, auth=autho, data=body)
    check_response_ok(response, "POST")
    if return_headers:
        return response.headers

def put(url, head=None, data=None, autho=None):
    response = requests.put(url, headers=head,auth=autho, data=data)
    check_response_ok(response, "PUT")

def get(url, head, parameters=None, autho=None):
    response  = requests.get(url, headers=head, params=parameters)
    if check_response_ok(response, "GET"):
        return response.text

def patch(url, head, body, autho):
    response = requests.patch(url, data=body, headers=head, auth=autho)  # TODO: check if 'data' should be replaced with 'json'
    check_response_ok(response, "PATCH")
