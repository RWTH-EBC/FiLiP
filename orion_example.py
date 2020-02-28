import filip.orion as orion
import filip.config as config
import sys

def create_entities(orion_cb:object):
    """
    Function creates Test Entities for the Context Broker
    :param orion_cb: Instance of an Orion Context Broker
    :return: The Entities used for Testing

    """

    room1 = {"id": "Room1",
             "type": "Room",
             "temperature" : { "value" : 11,
                              "type" : "Float" },
            "pressure" : {"value": 111,
                        "type": "Integer"}
            }

    room2 = {"id": "Room2",
             "type": "Room",
             "temperature" : { "value" : 22,
                            "type" : "Float" },
             "pressure" : {"value": 222,
                          "type": "Integer" }
            }

    room3 = {"id": "Room3",
             "type": "Room",
             "temperature" : { "value" : 33,
                            "type" : "Float" },
            "pressure" : {"value": 333,
                         "type": "Integer" }
            }

    room1_json = orion.Entity(room1)

    room2_json = orion.Entity(room2)

    room3_json = orion.Entity(room3)

    orion_cb.post_json(room1_json.get_json())

    orion_cb.post_json_key_value(room2_json.get_json())

    orion_cb.post_json_key_value(room3_json.get_json())

    # Test
    dog =  {"id": "Bello",
             "type": "Dog",
             "smell" : { "value" : "bad",
                        "type" : "String" },
             "number_of_legs" : {"value": 4,
                                "type": "Integer" }
            }


    dog_json = orion.Entity(dog)

    orion_cb.post_json_key_value(dog_json.get_json())

    return room1_json, room2_json, room3_json, dog_json


def query_entity(orion_cb, entity):
    print ("---- ---- ---- ---- ----")
    name = entity.id
    print ("query entity '" + name + "':")
    print (orion_cb.get_entity(name))
    print ()

    print ("get key values of entity '" + name + "':")
    print (orion_cb.get_entity_keyValues(name))
    print ()

    print ("get attributes of entity '" + name + "':")
    # ToDo check the importance of getting attribute names
    # Possible implementation through list comprehension
    # attr_names = [attr_name for attr_name in entity.get_json().keys() if attr_name not in ["id", "type"]]
    attr_list = entity.get_attributes()
    print (attr_list)
    print (orion_cb.get_entity_attribute_list(name, attr_list))
    print ()

    print ("check: get attributes in reverse:")
    reversed_list = list(reversed(attr_list))
    print (reversed_list)
    print (orion_cb.get_entity_attribute_list(name, reversed_list))
    print ()

    print ("get entity attributes in JSON format")
    for attr in attr_list:
        print ("attribute name: " + attr)
        print (orion_cb.get_entity_attribute_json(name, attr))
    print ()

    print ("get entity attribute value:")
    for attr in attr_list:
        print ("entity name: " + entity.id + ", attribute name: " + attr)
        print ("value: " + str(orion_cb.get_entity_attribute_value(name, attr)))

    print ("---- ---- ---- ---- ----")


if __name__=="__main__":
    CONFIG = config.Config('config.json')
    ORION_CB = orion.Orion(CONFIG) 
    ORION_CB.sanity_check()

    print ("++++ create entities ++++")
    entities = create_entities(ORION_CB)

    print ("++++ get all entities from Orion Context Broker ++++")
    print (ORION_CB.get_all_entities())
    print ()

    print ("++++ get all entities of type 'Room' ++++")
    print (ORION_CB.get_all_entities("type", "Room"))
    print ()

    print ("++++ get all entities of type 'Dog' ++++")
    print (ORION_CB.get_all_entities("type", "Dog"))
    print ()

    print ("++++ get all entities with idPattern '^Room[2-5]' (regular expression to filter out 'Room2 to Room5') ++++")
    print (ORION_CB.get_all_entities("idPattern", "^Room[2-5]"))
    print ()

    print ("++++ query all entities with temperature > 22 ++++")
    print (ORION_CB.get_all_entities("q", "temperature>22"))
    print ()


    print ("++++ query entities ++++")
    for entity in entities:
        query_entity(ORION_CB, entity)
    print ()

    print ("++++ test querying an entity that was not created ++++")
    print (ORION_CB.get_entity("Room5"))
    print ()

    print ("++++ test querying an attribute that doesn't exist ++++")
    print (ORION_CB.get_entity_attribute_value("Room1", "humidity"))
    print ()

    print ("++++ delete all entities ++++")
    #for entity in entities:
        #ORION_CB.delete(entity.id)
