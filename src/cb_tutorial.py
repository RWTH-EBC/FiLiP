from examples import orion_example
import streamlit as st
from filip import config
from filip import orion
import inspect
import json
import src.shared_components as shared_components



def create_CB():

    CONFIG = config.Config('config.json')
    ORION_CB = orion.Orion(CONFIG)
    st.write(ORION_CB.sanity_check())
    return CONFIG, ORION_CB


# The write function is necessary to be called from the main module
def write():

    st.header("Context Broker Tutorial")
    st.write("Welcome to the Context Broker Tutorial. Further explanations and so on. ")


    st.subheader("Creating an Instance of the Context Broker.")
    st.text("The first step is to create an instance of the Context Broker."
            "This requires a previously set configuration.")


    # load config
    # Read Config
    # Check Functionality

    with open("config.json") as f:
        json_data = json.load(f)
    st.json(json_data)


    CONFIG = config.Config('config.json')
    ORION_CB = orion.Orion(CONFIG)
    ORION_CB.sanity_check()

    st.subheader("Creating Entities")
    st.text("An Entity represents an virtual or real object, process or something else.")
    st.markdown("First we have to create some Entities.")
    entities = orion_example.create_entities(ORION_CB)
    create_code = st.checkbox("Display Code?", value=False)
    if create_code:
        shared_components.display_code(orion_example.create_entities)

    shared_components.display_code(orion_example.create_entities)
    st.write("These are the entities:", [entity.id for entity in entities])

    st.subheader("Now we can query the entities.")
    st.write("Use the function get_all_entities to get all entities and their data.")
    entities_json = ORION_CB.get_all_entities()
    shared_components.pretty_print_json(entities_json)
    get_code = st.checkbox("Display the code for getting all entities?", value=False)
    if get_code:
        shared_components.display_code(ORION_CB.get_all_entities)


    type_list = [entity["type"] for entity in json.loads(entities_json)]
    st.write("Get all entities of a type.")
    query_type = st.selectbox("Select a type.", type_list)
    if query_type:
        type_data = ORION_CB.get_all_entities("type", query_type)
        shared_components.pretty_print_json(type_data)
    query_code = st.checkbox("Display the code for querying the entities by type?", value=False)
    if query_code:
        shared_components.display_code(ORION_CB.get_all_entities)

    st.text("Get All entities get all entities with idPattern '^Room[2-5]' (regular expression to filter out 'Room2 to Room5')"
            " or query all entities with temperature > 22")
    regex_strings = ["^Room[2-5]", "temperature>22"]
    regex_query = st.selectbox("Select an example query expression.", regex_strings)
    if regex_query == "^Room[2-5]":
        regex_data = ORION_CB.get_all_entities("idPattern",regex_query)
        shared_components.pretty_print_json(regex_data)
    if regex_query == "temperature>22":
        regex_data = ORION_CB.get_all_entities("q", "temperature>22")
        shared_components.pretty_print_json(regex_data)

    for entity in entities:
        st.write(orion_example.query_entity(ORION_CB, entity))
        shared_components.display_code(orion_example.query_entity)

    st.text("Text querying an entity that was not created.")
    ORION_CB.get_entity("Room5")

    st.text("Test getting an attribute that does not exist.")
    ORION_CB.get_entity_attribute_value("Room1", "humidity")

    st.subheader("Now we can try querying a specific entity.")

    entitiy_to_query = st.selectbox("Which one would you like to try?", entities)

    st.subheader("To finish this tutorial you now have to delete the entities.")
    delete_yes = st.checkbox("Delete Entities?", value=False)
    if delete_yes:
        for entity in entities:
            ORION_CB.delete(entity.id)






if __name__=="__main__":
    write()
