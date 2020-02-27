from examples import quantum_leap_example as qle
from filip import config, orion, timeseries as ts
from src import shared_components

import inspect
import json
import time
import streamlit as st


PROTECTED_KEYS = ["id", "type"]

# helper function to call the tutorial from app.py
def write():

    st.header("This is the tutorial for QuantumLeap.")

    st.text("Explanation about Quantum Leap.")

    st.subheader("Creating an Instance of the Context Broker.")

    st.text("The first step is to create an instance of the Context Broker."
            "This requires a previously set configuration.")


    # load config
    # Read Config
    # Check Functionality

    ORION_CB = qle.create_cb()
    cb_code = st.checkbox("Would you like to see the code for creating an Context Broker Instance?", value=False)
    if cb_code:
        shared_components.display_code(qle.create_cb)


    """ Creating an Instance of QLE"""
    st.subheader("Creating an Instance of QuantumLeap")

    st.text("Explenation")
    QUANTUM = qle.create_ql()
    qle_code = st.checkbox("Would you like to see the code for creating an QuantumLeap Instance?", value=False)
    if qle_code:
        shared_components.display_code(qle.create_ql)




    # create an example entity
    st.subheader("Creating an Entity")
    oak = qle.create_entity(ORION_CB)
    entity_code = st.checkbox("Would you like to display the code for creating an example entity?", value=False)
    if entity_code:
        shared_components.display_code(qle.create_entity)




    # Creating a subscription
    st.subheader("Creating a Subscription.")
    st.text("Create a Subscription and register it with the Orion Context Broker")
    notify_url = "http://quantumleap:8668/v2/notify"
    sub_id = qle.create_subscription(ORION_CB, QUANTUM, oak, notify_url)
    subscription_code = st.checkbox("Display the code to create a subscription?", value=False)
    if subscription_code:
        shared_components.display_code(qle.create_subscription)



    st.text("Verify the Subscription with the Context Broker.")
    verify_sub = ORION_CB.get_subscription(sub_id)
    st.text(verify_sub)

    st.text("Get all subscriptions from the Context Broker.")
    subscription_list = ORION_CB.get_subscription_list()
    st.text("These are the existing subscriptions: {}".format(subscription_list))
    subscription_list_code = st.checkbox("Display the code to get a list of the subscriptions?", value=False)
    if subscription_list_code:
        shared_components.display_code(ORION_CB.get_subscription_list)


    st.subheader("Updating the attributes.")
    entity_json = json.loads(ORION_CB.get_entity(oak.id))
    attributes =  [attr for attr in entity_json.keys() if attr not in PROTECTED_KEYS]
    attr_to_update = st.selectbox("Select one attribute to upgrade:", attributes)

    # cache needed to prevent continously updating of attributes
    @st.cache()
    def update(ORION_CB, oak, attr_to_update):
        return qle.update_attribute(ORION_CB, oak, attr_to_update)

    update(ORION_CB, oak, attr_to_update)

    update_code = st.checkbox("Display the code to update an attribute?", value=False)
    if update_code:
        shared_components.display_code(qle.update_attribute)




    st.subheader("Querying the data.")



    # query historical data
    valuesonly = bool(True)
    params = {"lastN": 10}

    st.write("Use the function get_all_entities to get all entities and their data.")
    entities_json = ORION_CB.get_all_entities()
    shared_components.pretty_print_json(entities_json)
    get_code = st.checkbox("Display the code for getting all entities?", value=False)
    if get_code:
        shared_components.display_code(ORION_CB.get_all_entities)


    st.text("We can acess historical data via QuantumLeaps timeseries function.")

    # ToDo implement as Switch?

    st.text(QUANTUM.get_entity_data(oak.id))
    st.text(QUANTUM.get_entity_data(oak.id, "height", params = params))
    st.text(QUANTUM.get_timeseries(oak.id))
    st.text(QUANTUM.get_entity_data(oak.id, "height", valuesonly))
    st.text(QUANTUM.get_entity_type_data("Tree", "height"))
    st.text(QUANTUM.get_entity_type_data("Tree", "height", valuesonly))
    """

    #dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)
    #print(dataframe)
    
    """

    st.subheader("Displaying timeseries data")
    st.text("Timeseries data can also be displayed.")

    #ToDo implement shared componontes timeseries here

    st.subheader("Finally ...")

    st.text("Before finishing this tutorial we have to delete the Entities and Subscriptions."
            "the Entities need to be deleted in quantum. Deleting the subscription's prevents "
            "the entities from being posted multiple times.")
    # delete entity in orion

    delete_all = st.checkbox("Delete the entity?", value=False)
    if delete_all:
        ORION_CB.delete(oak.id)
        QUANTUM.delete_entity(oak.id)
        ORION_CB.delete_all_subscriptions()

    delete_Code = st.checkbox("Would you like to see the respective code?", value=False)
    if delete_Code:
        shared_components.display_code(ORION_CB.delete)
        shared_components.display_code(QUANTUM.delete_entity)
        shared_components.display_code(ORION_CB.delete_subscription)



if __name__=="__main__":
    write()
