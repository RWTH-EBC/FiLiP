"""
Test the endpoint for subscription related task of NGSI-LD for ContextBrokerClient
"""
import json
import unittest

from pydantic import ValidationError
import threading 
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.context import \
    ContextProperty, \
    NamedContextProperty, \
    ContextLDEntity
from filip.models.ngsi_ld.subscriptions import \
    Endpoint, \
    NotificationParams, \
    Subscription
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings
from random import randint


class TestSubscriptions(unittest.TestCase):
    """
    Test class for context broker models
    """

    def cleanup(self):
        """
        Cleanup test subscriptions
        """
        sub_list = self.cb_client.get_subscription_list()
        for sub in sub_list:
            if sub.id.startswith('urn:ngsi-ld:Subscription:test_sub'):
                self.cb_client.delete_subscription(sub.id)

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        FIWARE_SERVICE = "service"
        FIWARE_SERVICEPATH = "/"
        self.fiware_header = FiwareLDHeader(
            service=FIWARE_SERVICE,
            service_path=FIWARE_SERVICEPATH)
        # self.mqtt_url = "mqtt://test.de:1883"
        # self.mqtt_topic = '/filip/testing'
        # self.notification =  {
        #     "attributes": ["filling", "controlledAsset"],
        #     "format": "keyValues",
        #     "endpoint": {
        #     "uri": "http://test:1234/subscription/low-stock-farm001-ngsild",
        #     "accept": "application/json"
        #     }
        # }
        #self.mqtt_url = TestSettings.MQTT_BROKER_URL
        self.mqtt_topic = ''.join([FIWARE_SERVICE, FIWARE_SERVICEPATH])
        self.MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
        self.MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
        self.endpoint_mqtt = Endpoint(**{
            "uri": "mqtt://my.host.org:1883/my/test/topic",
            "accept": "application/json",  # TODO check whether it works
        })
        self.cb_client = ContextBrokerLDClient(url=settings.LD_CB_URL, fiware_header=self.fiware_header)
        self.endpoint_http = Endpoint(**{
            "uri": "http://137.226.248.246:1027/ngsi-ld/v1/subscriptions",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
     )
        self.cleanup()

    def tearDown(self) -> None:
        self.cleanup()


    def test_post_subscription_http(self):
        """
        Create a new HTTP subscription.
        Args:
            - Request body: required
        Returns:
            - (201) successfully created subscription
        Tests:
            - Create a HTTP subscription and post it
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub0"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_list = [x for x in self.cb_client.get_subscription_list() 
                    if x.id == 'urn:ngsi-ld:Subscription:test_sub0']
        self.assertEqual(len(sub_list),1)

    def test_post_subscription_http_check_broker(self):
        """
        Create a new HTTP subscription and check whether messages are received.
        Args:
            - Request body: required
        Returns:
            - (201) successfully created subscription 
        Tests:
            - Create a subscription and post something from this subscription 
                to see if the subscribed broker gets the message.
            - Create a subscription twice to one message and see if the message is 
                received twice or just once.
        """
        pass

    def test_get_subscription(self):
        """
        Returns the subscription if it exists.
        Args:
            - subscriptionId(string): required
        Returns: 
            - (200) subscription or empty list if successful 
            - Error Code
        Tests:
            - Get Subscription and check if the subscription is the same as the one posted
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub0"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_get = self.cb_client.get_subscription(subscription_id=id)
        self.assertEqual(sub.entities, sub_get.entities)
        self.assertEqual(sub.notification.attributes, sub_get.notification.attributes)
        self.assertEqual(sub.notification.endpoint.uri, sub_get.notification.endpoint.uri)

    def test_get_subscription_list(self):
        """
        Get a list of all current subscriptions the broker has subscribed to.
        Args:
            - limit(number($double)): Limits the number of subscriptions retrieved
        Returns:
            - (200) list of subscriptions
        Tests for get subscription list:
            - Create list of subscriptions and get the list of subscriptions -> compare the lists
            - Set a limit for the subscription number and compare the count of subscriptions
        """
        sub_post_list = list()
        for i in range(10):
            attr_id = "attr" + str(i)
            id = "urn:ngsi-ld:Subscription:" + "test_sub" + str(i)
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
            sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
            sub_post_list.append(sub)
            self.cb_client.post_subscription(sub)

        sub_list = self.cb_client.get_subscription_list()
        sub_id_list = [sub.id for sub in sub_list]

        for sub in sub_post_list:
            self.assertIn(sub.id, sub_id_list)

        sub_limit = 5
        sub_list2 = self.cb_client.get_subscription_list(limit=sub_limit)
        self.assertEqual(len(sub_list2), sub_limit)


    def test_delete_subscription(self):
        """
        Cancels subscription. 
        Args: 
            - subscriptionID(string): required
        Returns:
            - Successful: 204, no content 
        Tests:
            - Post and delete subscription then get all subscriptions and check whether deleted subscription is still there.
        """
        for i in range(10): 
            attr_id = "attr" + str(i)
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
            id = "urn:ngsi-ld:Subscription:" + "test_sub" + str(i)
            sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])

            if i == 0: 
                del_sub = sub
                del_id = id
            self.cb_client.post_subscription(sub)
        
        sub_list = self.cb_client.get_subscription_list(limit=10)
        sub_id_list = [sub.id for sub in sub_list]
        self.assertIn(del_sub.id, sub_id_list)

        self.cb_client.delete_subscription(subscription_id=del_id)
        sub_list = self.cb_client.get_subscription_list(limit=10)
        sub_id_list = [sub.id for sub in sub_list]
        self.assertNotIn(del_sub.id, sub_id_list)

        for sub in sub_list:
            self.cb_client.delete_subscription(subscription_id=sub.id)
            
    def test_update_subscription(self):
        """
        Update a subscription.
        Only the fields included in the request are updated in the subscription.
        Args:
            - subscriptionID(string): required
            - body(body): required
        Returns:
            - Successful: 204, no content
        Tests: 
            - Patch existing subscription and read out if the subscription got patched.
            - Try to patch non-existent subscriptions.
            - Try to patch more than one subscription at once.
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub77"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list()
        self.assertEqual(len(sub_list), 1)

        sub_changed = Subscription(id=id, notification=notification_param, entities=[{"type": "House"}])

        self.cb_client.update_subscription(sub_changed)

        # Try to patch non-existent subscriptions.
        # TODO
        #Try to patch more than one subscription at once.
        # TODO

class TestSubsCheckBroker(unittest.TestCase):
    entity_dict = {
        'id':'urn:ngsi-ld:Entity:test_entity03',
        'type':'Room',
        'temperature':{
            'type':'Property',
            'value':30
        }
    }
    
    sub_dict = {
        'description':'Test Subscription',
        'id':'urn:ngsi-ld:Subscription:test_sub25',
        'type':'Subscription',
        'entities':[
            {
                'type':'Room'
            }
        ],
        'watchedAttributes':[
            'temperature'
        ],
        'q':'temperature<30',
        'notification':{
            'attributes':[
                'temperature'
            ],
            'format':'normalized',
            'endpoint':{
                'uri':'mqtt://mosquitto:1883/my/test/topic', # change uri
                'Accept':'application/json'
            },
            'notifierInfo':[
                {
                    "key":"MQTT-Version",
                    "value":"mqtt5.0"
                }
            ]
        }
    }

    def cleanup(self):
        """
        Cleanup test subscriptions
        """
        sub_list = self.cb_client.get_subscription_list()
        for sub in sub_list:
            if sub.id.startswith('urn:ngsi-ld:Subscription:test_sub'):
                self.cb_client.delete_subscription(sub.id)
        entity_list = self.cb_client.get_entity_list()
        for entity in entity_list:
            if entity.id.startswith('urn:ngsi-ld:Entity:test_entity'):
                self.cb_client.delete_entity_by_id(entity_id=entity.id)

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        FIWARE_SERVICE = "service"
        FIWARE_SERVICEPATH = "/"
        self.fiware_header = FiwareLDHeader(
            service=FIWARE_SERVICE,
            service_path=FIWARE_SERVICEPATH)
        self.cb_client = ContextBrokerLDClient(url=settings.LD_CB_URL, 
                                               fiware_header=self.fiware_header)
        self.mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        #on_message callbacks differ from test to test, but on connect callbacks dont
        def on_connect_fail(client,userdata):
            self.fail("Test failed due to broker being down")

        def on_connect(client,userdata,flags,reason_code,properties):
            self.mqtt_client.subscribe("my/test/topic")

        self.mqtt_client.on_connect_fail = on_connect_fail
        self.mqtt_client.on_connect = on_connect
        self.cleanup()
        #posting one single entity to check subscription existence/triggers
        self.cb_client.post_entity(entity=ContextLDEntity(**self.entity_dict))


    def tearDown(self) -> None:
        self.cleanup()


    def test_post_subscription_mqtt(self):
        """
        Tests:
            - Subscribe using an mqtt topic as endpoint and see if notification is received
        """
        #Declare timer function, mqtt message callback and a check variable(test_res)
        #Variable is in list because python threads get copies of primitive objects (e.g bool)
        #but not of iterables
        test_res = [True]
        def timeout_func(x):
            #The timer changes the variable when it runs out
            x[0] = False
        
        def on_message(client,userdata,msg):
            #the callback cancels the timer if a message comes through
            timeout_proc.cancel()
            updated_entity = self.entity_dict.copy()
            updated_entity.update({'temperature':{'type':'Property','value':25}})
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            #extra sanity check on the contents of the notification(in case we are 
            #catching a rogue one)
            self.assertEqual(updated_entity,
                             json.loads(msg.payload.decode())['body']['data'][0])

        #adjust timeout here as needed
        timeout_proc = threading.Timer(5,timeout_func,args=[test_res])
        self.mqtt_client.on_message = on_message
        
        self.mqtt_client.connect("localhost",1883,60)
        self.mqtt_client.loop_start()
        #post subscription then start timer
        self.cb_client.post_subscription(subscription=Subscription(**self.sub_dict))
        timeout_proc.start()
        #update entity to (ideally) get a notification
        self.cb_client.update_entity_attribute(entity_id='urn:ngsi-ld:Entity:test_entity03',
                                            attr=NamedContextProperty(type="Property",
                                                                        value=25,
                                                                        name='temperature'),
                                            attr_name='temperature')
        #this loop is necessary otherwise the test does not fail when the time runs out
        while(timeout_proc.is_alive()):
            continue
        #if all goes well, the callback is triggered, and cancels the timer before
        #it gets to change the test_res variable to False, making the following assertion true
        self.assertTrue(test_res[0])
    
    def test_update_subscription_check_broker(self):
        """
        Update a subscription and check changes in received messages.
        Args:
            - subscriptionID(string): required
            - body(body): required
        Returns:
            - Successful: 204, no content
        Tests:
            - Patch existing subscription and read out if the subscription got patched.
        """
        pass

    def test_delete_subscription_check_broker(self):
        """
        Cancels subscription and checks on subscribed values.
        Args:
            - subscriptionID(string): required
        Returns:
            - Successful: 204, no content
        Tests:
            - Post and delete subscription then see if the broker still gets subscribed values.
        """
        pass

    def test_get_subscription_check_broker(self):
        """
        Returns the subscription if it exists.
        Args:
            - subscriptionId(string): required
        Returns:
            - (200) subscription or empty list if successful
            - Error Code
        Tests:
            - Subscribe to a message and see if it appears when the message is subscribed to
            - Choose a non-existent ID and see if the return is an empty array
        """
        pass
