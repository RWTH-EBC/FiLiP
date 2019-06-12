import filip.orion as orion
import filip.config as config
import sys

def create_entities(orion_cb):
    room1_a1 = orion.Attribute('temperature', 11, 'Float')
    room1_a2 = orion.Attribute('pressure', 111, 'Integer')
    attributes1 = room1_a1, room1_a2
    room1 = orion.Entity('Room1', 'Room', attributes1)

    orion_cb.post_entity(room1)

    room2_a1 = orion.Attribute('temperature', 22, 'Float')
    room2_a2 = orion.Attribute('pressure', 222, 'Integer')
    attributes2 = room2_a1, room2_a2
    room2 = orion.Entity('Room2', 'Room', attributes2)

    orion_cb.post_entity(room2)

    room3_a1 = orion.Attribute('temperature', 33, 'Float')
    room3_a2 = orion.Attribute('pressure', 333, 'Integer')
    attributes3 = room3_a1, room3_a2
    room3 = orion.Entity('Room3', 'Room', attributes3)

    orion_cb.post_entity(room3)

    dog_a1 = orion.Attribute('smell', 'bad', 'String')
    dog_a2 = orion.Attribute('number_of_legs', 4, 'Integer')
    dog = orion.Entity('Bello', 'Dog', [dog_a1, dog_a2])

    orion_cb.post_entity(dog)

    return room1, room2, room3, dog


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
    attr_list = []
    for attr in entity.attributes:
        attr_list.append(attr.name)
    print (attr_list)
    print (orion_cb.get_entity_attribute_list(name, attr_list))
    print ()

    print ("check: get attributes in reverse:")
    reversed_list = list(reversed(attr_list))
    print (reversed_list)
    print (orion_cb.get_entity_attribute_list(name, reversed_list))
    print ()

    print ("get entity attributes in JSON format")
    for attr in entity.attributes:
        print ("attribute name: " + attr.name)
        print (orion_cb.get_entity_attribute_json(name, attr.name))
    print ()

    print ("get entity attribute value:")
    for attr in entity.attributes:
        print ("entity name: " + name + ", attribute name: " + attr.name)
        print ("value: " + str(orion_cb.get_entity_attribute_value(name, attr.name)))

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
    for entity in entities:
        ORION_CB.delete(entity.id)
