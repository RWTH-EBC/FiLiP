from examples import quantum_leap_example
import streamlit as st
from filip import config
from filip import orion
import inspect
import json
import src.shared_components as shared_components
from filip import orion, timeseries as ts
import time

# helper function to call the tutorial from app.py
def write():
    st.header("This is the tutorial for Quantum Leap.")

    st.text("Explanation about Quantum Leap.")

    st.subheader("Creating an Instance of the Context Broker.")
    st.text("The first step is to create an instance of the Context Broker."
            "This requires a previously set configuration.")


    # load config
    # Read Config
    # Check Functionality

    CONFIG = config.Config('config.json')
    ORION_CB = orion.Orion(CONFIG)
    ORION_CB.sanity_check()


    # create an example entity
    oak = quantum_leap_example.create_entity(ORION_CB)
    entity_code = st.checkbox("Would you like to display the code for creating an example entity?", value=False)
    if entity_code:
        shared_components.display_code(quantum_leap_example.create_entity)

    # create an instance of Quantumleap
    quantum = ts.QuantumLeap(CONFIG)

#    quantum.fiware_service = None


     # create a subscription and register it with the Orion Context Broker
    notify_url = "http://quantumleap:8668/v2/notify"
    sub_id = quantum_leap_example.create_subscription(ORION_CB, quantum, oak, notify_url)
    print("subscription created, id is: " + str(sub_id))
    print(ORION_CB.get_subscription(sub_id))

    subscription_list = ORION_CB.get_subscription_list()
    print(subscription_list)


    # test update attributes
    # once with the function and once directly with the Context Broker
    quantum_leap_example.update_attribute(orion_cb=ORION_CB, entity=oak, attribute_name="height")
    ORION_CB.update_attribute(oak.id, "leaves", "brown")

    # query historical data
    valuesonly = bool(True)
    params = {"lastN": 10}

    print(quantum.get_health())
    print(quantum.get_version())
    print(quantum.get_entity_data(oak.id))
    print(quantum.get_entity_data(oak.id, "height", params = params))
    print(quantum.get_timeseries(oak.id))
    print(quantum.get_entity_data(oak.id, "height", valuesonly))
    print(quantum.get_entity_type_data("Tree", "height"))
    print(quantum.get_entity_type_data("Tree", "height", valuesonly))



    #dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)
    #print(dataframe)

    # delete entity in orion
    timeout = 3
    print("deleting test entity in " + str(timeout) + " seconds")
    for j in range(0, timeout):
        time.sleep(1)
        print("...")

    ORION_CB.delete(oak.id)

    # delete entity in crate DB
    quantum.delete_entity(oak.id)

    # delete subscription, so that the entity is not posted several times
    # by multiple subscriptions
    #
    ORION_CB.delete_subscription(sub_id)

    ORION_CB.delete_all_subscriptions()



if __name__=="__main__":
    write()
