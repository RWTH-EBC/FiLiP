from examples import iot_example
from filip import orion, iot, config
import streamlit as st
from src import shared_components

def write():

    shared_components.title_EBC()

    st.header("This is a tutorial for the IoT Agent")
    st.text("Explanation about IoT-Agent")

    st.subheader("Reading the Config and creating an Instance of the Context Broker")

    CONFIG = iot_example.read_config()


    ORION_CB = iot_example.create_cb()

    st.text("Check whether the context Broker works: {}".format(ORION_CB.sanity_check()))

    ORION_CB.sanity_check()

    st.text("The next step is to change the service path.")


    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iota")
    ORION_CB.set_service(fiware_service)
    res = fiware_service.get_header()

    shared_components.pretty_print_json(res)


    iot_example.create_device()



    st.subheader("Creating an Instant of the IoT-Agent in the Json-Version")
    IOTA_JSON = iot.Agent("iota_json", CONFIG)




    # Creating an Instance of the IoT-Agent in the UL-Version
    IOTA_UL = iot.Agent("iota_ul", CONFIG)




    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iota")
    ORION_CB.set_service(fiware_service)
    res = fiware_service.get_header()


    # create a device

    device_1 = iot_example.create_device()

    # create a device group

    cb_host = "http://orion:1026"

    iot_agent = "iota_ul"

    device_group = iot_example.create_device_group(fiware_service=fiware_service, cb_host=cb_host,
                                       devices=[device_1])

    # Test the device group
    device_group.test_apikey()

    IOTA_JSON.post_group(device_group)

    IOTA_JSON.post_device(device=device_1, device_group=device_group)

    st.subheader("Deleting the subscriptions.")
    st.text("To avoid posting duplicate entries the subscriptions have to be deleted.")
    delete_all = st.checkbox("Delete the subscriptions?", value=False)
    if delete_all:
        ORION_CB.delete_all_subscriptions()


    delete_Code = st.checkbox("Would you like to see the respective code?", value=False)
    if delete_Code:
        shared_components.display_code(ORION_CB.delete_all_subscriptions)

if __name__ == "__main__":
    write()
