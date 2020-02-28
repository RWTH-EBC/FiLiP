from examples import subscription_example
import streamlit as st
from src import shared_components
import time


def write():

    st.header("This is the tutorial for creating Subscriptions")

    st.subheader("Creating an instance of the Context Broker")
    st.text("First we have to create an Instance of the Context Broker."
            " This again requires to load a config.")
    ORION_CB = subscription_example.create_cb()
    cb_code = st.checkbox("Would you like to see how to create an instance of the Context Broker?", value=False)
    if cb_code:
        shared_components.display_code(subscription_example.create_cb)


    st.subheader("Creating the body for a subscription")



    body = subscription_example.API_Walkthrough_subscription()
    st.text("This is the subscription body.")
    shared_components.pretty_print_json(body)
    body_code = st.checkbox("Would you like to see how to create an example body for a subscription?", value=False)
    if body_code:
        shared_components.display_code(subscription_example.API_Walkthrough_subscription)

    sub_id1 = ORION_CB.create_subscription(body)
    st.text("Now it has to be registered with the Context Broker, which generates a subscription id: {}".format(sub_id1))
    sub_1_code = st.checkbox("Would you like to see how to register the subscription?", value=False)
    if sub_1_code:
        shared_components.display_code(ORION_CB.create_subscription)



    st.subheader("Create a Subscripiton with reduced scope.")

    body_2 = subscription_example.Step_By_Step_reducing_scope_with_expression()
    shared_components.pretty_print_json(body)

    sub_id2 = ORION_CB.create_subscription(body_2)
    st.text("Now it has to be registered with the Context Broker, which generates a subscription id: {}".format(sub_id2))
    body_code_2 = st.checkbox("Would you like to see how to create an example body for a reduced subscription?", value=False)
    if body_code_2:
        shared_components.display_code(subscription_example.API_Walkthrough_subscription)


    st.subheader("Creating an http subscription.")

    body_3 = subscription_example.http_custom_subscription()
    shared_components.pretty_print_json(body_3)

    sub_id3 = ORION_CB.create_subscription(body_3)
    st.text("Now it has to be registered with the Context Broker, which generates a subscription id: {}".format(sub_id3))
    body_code_3 = st.checkbox("Would you like to see how to create an example body for a HTTP subscription?", value=False)
    if body_code_3:
        shared_components.display_code(subscription_example.http_custom_subscription)



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
