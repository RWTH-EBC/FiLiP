import logging
import json
from pydantic import BaseModel, AnyHttpUrl

"""
Helper functions for HTTP requests
"""

HEADER_ACCEPT_JSON = {'Accept': 'application/json'}
HEADER_ACCEPT_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT_JSON = {'Content-Type': 'application/json'}
HEADER_CONTENT_PLAIN = {'Content-Type': 'text/plain'}

log = logging.getLogger(__name__)

class UrlValidator(BaseModel):
    url: AnyHttpUrl


def validate_url(url):
    """
    Function checks whether the host has "http" added in case of http as protocol.
    :param url: the url for the host / port
    :return: url - if necessary updated
    """
    UrlValidator(url=url)



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


def response_ok(response) -> (bool, str):
    status = response.status_code
    ok = False
    retstr = ""
    if status == 200:
        ok = True
        retstr = "[INFO]: HTTP request OK"
    elif status == 201:
        ok = True
        retstr = "[INFO]: Created"
    elif status == 204:
        ok = True
        retstr = "[INFO]: HTTP request successfully processed"
    elif status == 405:
        retstr = "[INFO]: HTTP error - method not allowed"
    elif status == 411:
        retstr = "[INFO]: HTTP error - content length required"
    elif status == 413:
        retstr = "[INFO]: HTTP error - request entity too large"
    elif status == 415:
        retstr = "[INFO]: HTTP error - unsupported media type"
    elif status == 422:
        retstr = "[INFO]: HTTP error - unprocessable entity"
    else:
        retstr = "[INFO]: HTTP response: " + response.text
    return ok, retstr

def logging_switch(response):
    status = response.status_code
    ok, retstr = response_ok(response)
    category = str(status)[0]
    text = json.loads(response.text)
    keys = [key for key in text.keys()]
    level = {
        "1": "INFO",
        "2": "INFO",
        "3": "WARNING",
        "4": "ERROR",
        "5": "ERROR",
            }.get(category, "INFO")
    response_text = f"The request was: {text[keys[0]]}, because: {text[keys[1]]} "
    return level, response_text



"""
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
"""
