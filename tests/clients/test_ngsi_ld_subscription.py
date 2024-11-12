"""
Test the endpoint for subscription related task of NGSI-LD for ContextBrokerClient
"""
import json
import time
import urllib.parse
from unittest import TestCase
import threading
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt
from requests import RequestException
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.context import \
    NamedContextProperty, \
    ContextLDEntity, ActionTypeLD
from filip.models.ngsi_ld.subscriptions import \
    Endpoint, \
    NotificationParams, \
    SubscriptionLD
from tests.config import settings
from filip.utils.cleanup import clear_context_broker_ld


class TestSubscriptions(TestCase):
    """
    Test class for context broker models
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                               url=settings.LD_CB_URL)
        clear_context_broker_ld(cb_ld_client=self.cb_client)

        self.mqtt_topic = ''.join([settings.FIWARE_SERVICE,
                                   settings.FIWARE_SERVICEPATH])
        self.endpoint_mqtt = Endpoint(**{
            "uri": str(settings.LD_MQTT_BROKER_URL) + "/my/test/topic",
            "accept": "application/json",
        })
        self.endpoint_http = Endpoint(**{
            "uri": urllib.parse.urljoin(str(settings.LD_CB_URL),
                                        "/ngsi-ld/v1/subscriptions"),
            "accept": "application/json"
        })

    def tearDown(self) -> None:
        clear_context_broker_ld(cb_ld_client=self.cb_client)
        self.cb_client.close()

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
        sub = SubscriptionLD(id=id, notification=notification_param, entities=[{"type": "Room"}])
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
        sub = SubscriptionLD(id=id, notification=notification_param, entities=[{"type": "Room"}])
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
            sub = SubscriptionLD(id=id, notification=notification_param, entities=[{"type": "Room"}])
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
            notification_param = NotificationParams(
                attributes=[attr_id], endpoint=self.endpoint_http)
            id = "urn:ngsi-ld:Subscription:" + "test_sub" + str(i)
            sub = SubscriptionLD(id=id,
                                 notification=notification_param,
                                 entities=[{"type": "Room"}]
                                 )

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
        sub = SubscriptionLD(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list()
        self.assertEqual(len(sub_list), 1)
        print(self.endpoint_http.model_dump())
        sub_changed = SubscriptionLD(id=id, notification=notification_param, entities=[{"type": "House"}])
        self.cb_client.update_subscription(sub_changed)
        u_sub= self.cb_client.get_subscription(subscription_id=id)
        self.assertNotEqual(u_sub,sub_list[0])
        self.maxDiff = None
        self.assertDictEqual(sub_changed.model_dump(),
                             u_sub.model_dump())
        non_sub = SubscriptionLD(id="urn:ngsi-ld:Subscription:nonexist",
                                 notification=notification_param,
                                 entities=[{"type":"house"}])
        with self.assertRaises(Exception):
            self.cb_client.update_subscription(non_sub)


class TestSubsCheckBroker(TestCase):
    """
    These tests are more oriented towards testing the actual broker.
    Some functionality in Orion LD may not be consistent at times.
    """
    def timeout_func(self):
            self.last_test_timeout =[False]

    def cleanup(self):
        """
        Cleanup test subscriptions
        """
        sub_list = self.cb_client.get_subscription_list()
        for sub in sub_list:
            if sub.id.startswith('urn:ngsi-ld:Subscription:test_sub'):
                self.cb_client.delete_subscription(sub.id)
        try:
            entity_list = True
            while entity_list:
                entity_list = self.cb_client.get_entity_list(limit=100)
                self.cb_client.entity_batch_operation(action_type=ActionTypeLD.DELETE,
                                                      entities=entity_list)
        except RequestException:
            pass

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.entity_dict = {
            'id': 'urn:ngsi-ld:Entity:test_entity03',
            'type': 'Room',
            'temperature': {
                'type':  'Property',
                'value': 30
            }
        }
        
        self.sub_dict = {
            'description': 'Test Subscription',
            'id': 'urn:ngsi-ld:Subscription:test_sub25',
            'type': 'Subscription',
            'entities': [
                {
                    'type': 'Room'
                }
            ],
            'watchedAttributes': [
                'temperature'
            ],
            'q': 'temperature<30',
            'notification':  {
                'attributes': [
                    'temperature'
                ],
                'format': 'normalized',
                'endpoint': {
                    'uri':  f'mqtt://'  # change uri
                          f'{settings.LD_MQTT_BROKER_URL_INTERNAL.host}:'
                          f'{settings.LD_MQTT_BROKER_URL_INTERNAL.port}/my/test/topic',
                    'Accept': 'application/json'
                },
                'notifierInfo': [
                    {
                        "key": "MQTT-Version",
                        "value": "mqtt5.0"
                    }
                ]
            }
        }
        self.fiware_header = FiwareLDHeader(
            ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(url=settings.LD_CB_URL, 
                                               fiware_header=self.fiware_header)
        # initial tenant
        self.cb_client.post_entity(ContextLDEntity(id="Dummy:1", type="Dummy"),
                                   update=True)
        self.cb_client.delete_entity_by_id("Dummy:1")
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

        #All broker tests rely on awaiting a message. This timer helps with:
        #   -Avoiding hang ups in the case of a lost connection
        #   -Avoid ending the tests early, in the case a notification takes longer

        self.timeout = 5 # in seconds
        self.last_test_timeout = [True]
        self.timeout_proc = threading.Timer(self.timeout,
                                            self.timeout_func)

    def tearDown(self) -> None:
        self.cleanup()
        self.cb_client.close()

    def test_post_subscription_mqtt(self):
        """
        Tests:
            - Subscribe using an mqtt topic as endpoint and see if notification is received
        """
        def on_message(client,userdata,msg):
            #the callback cancels the timer if a message comes through
            self.timeout_proc.cancel()
            updated_entity = self.entity_dict.copy()
            updated_entity.update({'temperature':{'type':'Property','value':25}})
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            #extra sanity check on the contents of the notification(in case we are 
            #catching a rogue one)
            self.assertEqual(updated_entity,
                             json.loads(msg.payload.decode())['body']['data'][0])

        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect(settings.LD_MQTT_BROKER_URL.host,
                                 settings.LD_MQTT_BROKER_URL.port,
                                 60)
        self.mqtt_client.loop_start()
        #post subscription then start timer
        self.cb_client.post_subscription(subscription=SubscriptionLD(**self.sub_dict))
        self.timeout_proc.start()
        #update entity to (ideally) get a notification
        self.cb_client.update_entity_attribute(entity_id='urn:ngsi-ld:Entity:test_entity03',
                                            attr=NamedContextProperty(type="Property",
                                                                        value=25,
                                                                        name='temperature'),
                                            attr_name='temperature')
        #this loop is necessary otherwise the test does not fail when the time runs out
        while(self.timeout_proc.is_alive()):
            continue
        #if all goes well, the callback is triggered, and cancels the timer before
        #it gets to change the timeout variable to False, making the following assertion True
        self.assertTrue(self.last_test_timeout[0],"Operation timed out")
    
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
        Steps:
            - Create Subscription with q = x
            - Update entity to trigger sub with valid condition x
            - Update subscription to q = x̄ 
            - Update entity to trigger sub with opposite condition x̄
        """
        current_vals = [25,33]

        #re-assigning a variable inside an inline function does not work => hence generator
        def idx_generator(n):
            while(n<2):
                yield n
                n+=1
    
        gen = idx_generator(0)

        def on_message(client,userdata,msg):
            idx = next(gen)
            self.timeout_proc.cancel()
            print(json.loads(msg.payload.decode())
                             ['body']['data'][0]['temperature']['value'])
            self.assertEqual(current_vals[idx],
                             json.loads(msg.payload.decode())
                             ['body']['data'][0]['temperature']['value'])

        self.mqtt_client.on_message = on_message
        
        self.mqtt_client.connect(settings.LD_MQTT_BROKER_URL.host,
                                 settings.LD_MQTT_BROKER_URL.port,
                                 60)
        self.mqtt_client.loop_start()
        self.cb_client.post_subscription(subscription=SubscriptionLD(**self.sub_dict))
        self.timeout_proc.start()

        self.cb_client.update_entity_attribute(entity_id='urn:ngsi-ld:Entity:test_entity03',
                                                attr=NamedContextProperty(type="Property",
                                                                            value=current_vals[0],
                                                                            name='temperature'),
                                                attr_name='temperature')
        while(self.timeout_proc.is_alive()):
            continue
        self.assertTrue(self.last_test_timeout[0],
                        "Operation timed out")

        self.last_test_timeout = [True]
        self.timeout_proc = threading.Timer(self.timeout,self.timeout_func)
        
        self.sub_dict.update({'q':'temperature>30'})
        self.cb_client.update_subscription(subscription=SubscriptionLD(**self.sub_dict))
        time.sleep(5)
        updated = self.cb_client.get_subscription(self.sub_dict['id'])
        self.assertEqual(updated.q,'temperature>30')
        self.timeout_proc.start()
        self.cb_client.update_entity_attribute(entity_id='urn:ngsi-ld:Entity:test_entity03',
                                            attr=NamedContextProperty(type="Property",
                                                                        value=current_vals[1],
                                                                        name='temperature'),
                                            attr_name='temperature')
        while(self.timeout_proc.is_alive()):
            continue
        self.assertTrue(self.last_test_timeout[0],
                        "Operation timed out")
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

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
