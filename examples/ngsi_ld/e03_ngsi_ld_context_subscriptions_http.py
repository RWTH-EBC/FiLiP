"""
# Examples for subscriptions
"""

# ## Import packages
import logging
import datetime
import time
import json
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from filip.config import settings
import pprint
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.subscriptions import SubscriptionLD
from filip.models.ngsi_ld.context import (
    DataTypeLD,
    ContextLDEntity,
    ContextProperty,
)
from filip.utils.cleanup import clear_context_broker_ld

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can set the address:
#
# Host address of Context Broker
LD_CB_URL = settings.LD_CB_URL

# You can also change the used Fiware service
# NGSI-LD Tenant
NGSILD_TENANT = "filip"

# Web server URL for receiving notifications
# It has to be accessible from the context broker!
SERVER_URL = "http://172.17.0.1:1995"
# You can replace SERVER_URL with the URL of the web server, where you'd like to receive notifications
# e.g. "http://host.docker.internal:8080/notify/", or if you're not sure how to set up the
# server, create a dummy version via
# https://fiware-orion.rtfd.io/en/master/user/walkthrough_apiv2.html#starting-accumulator-server

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # # 1 Client setup
    #
    # Create the context broker client, for more details view the example: e01_http_clients.py
    fiware_header = FiwareLDHeader(ngsild_tenant=NGSILD_TENANT)
    cb_ld_client = ContextBrokerLDClient(url=LD_CB_URL, fiware_header=fiware_header)
    # Make sure that the database is clean
    clear_context_broker_ld(cb_ld_client=cb_ld_client)

    entities = cb_ld_client.get_entity_list()
    logger.info(entities)

    class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

        def do_POST(self):
            print("Received notification")
            if self.headers["Content-Length"]:
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length)
                if body:
                    pprint.pprint(json.loads(body.decode("utf-8")), compact=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello, world!")

    httpd = HTTPServer(("0.0.0.0", 1995), SimpleHTTPRequestHandler)
    server_thread = Thread(target=lambda: httpd.serve_forever(), args=())
    server_thread.start()
    # # 2 Subscription setup
    #
    # The system is notified every time the "temperature" attribute of the entity (subject)
    # with the id "urn:ngsi-ld:Room:001" changes. The payload of the notification includes
    # only "temperature" attribute. Payload is completely modifiable.
    # The subscription expires after 15 minutes.
    interesting_entity_id = "urn:ngsi-ld:Room:001"
    room1_dictionary = {
        "id": "urn:ngsi-ld:Room:001",
        "type": "Room",
        "temperature": {"value": 11, "type": DataTypeLD.PROPERTY},
    }

    room1_entity = ContextLDEntity(**room1_dictionary)
    cb_ld_client.post_entity(room1_entity)
    sub_example = {
        "description": "Subscription to receive HTTP-Notifications about "
        + interesting_entity_id,
        "entities": [{"type": "Room"}],
        "watchedAttributes": ["temperature"],
        "q": "temperature>30",
        "notification": {
            "attributes": ["temperature"],
            "format": "normalized",
            "endpoint": {
                "uri": SERVER_URL,
                "Accept": "application/json",
            },
        },
        "expires": datetime.datetime.now() + datetime.timedelta(minutes=15),
        "id": "urg:ngsi-ld:Sub:001",
        "type": "Subscription",
    }
    sub = SubscriptionLD(**sub_example)
    # Posting an example subscription for Room1
    sub_id = cb_ld_client.post_subscription(subscription=sub, update=True)

    time.sleep(1)
    cb_ld_client.update_entity_attribute(
        entity_id=interesting_entity_id,
        attr=ContextProperty(value=42, type="Property"),
        attr_name="temperature",
    )

    # # 3 Filter subscriptions
    retrieve_sub = cb_ld_client.get_subscription(sub_id)
    logger.info(retrieve_sub)

    time.sleep(1)

    # # 4 Update subscription
    #
    sub_to_update = cb_ld_client.get_subscription(sub_id)
    # Update expiration time of the example subscription
    sub_to_update = sub_to_update.model_copy(
        update={"expires": datetime.datetime.now() + datetime.timedelta(minutes=15)}
    )
    cb_ld_client.update_subscription(sub_to_update)
    updated_subscription = cb_ld_client.get_subscription(sub_id)
    logger.info(updated_subscription)
    # # 5 Deleting the example subscription
    #

    time.sleep(1)
    httpd.shutdown()
    cb_ld_client.delete_subscription(sub_id)

    # # 6 Clean up (Optional)
    clear_context_broker_ld(cb_ld_client=cb_ld_client)
    # Close client
    cb_ld_client.close()
