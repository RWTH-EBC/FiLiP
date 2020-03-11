from filip import orion, config
import json

def create_store_entities():

    store_dict = [{ "type": "Store",
                    "id": "urn:ngsi-ld:Store:001",
                    "address": {
                        "type": "PostalAddress",
                        "value": {
                            "streetAddress": "Bornholmer Straße 65",
                            "addressRegion": "Berlin",
                            "addressLocality": "Prenzlauer Berg",
                            "postalCode": "10439"
                        }},
                    "location": {
                        "type": "geo:json",
                        "value": {
                            "type": "Point",
                            "coordinates": [13.3986, 52.5547]
                        }
                    },
                    "name": {
                        "type": "Text",
                        "value": "Bösebrücke Einkauf"
                    }},
                  {
                      "type": "Store",
                      "id": "urn:ngsi-ld:Store:002",
                      "address": {
                          "type": "PostalAddress",
                          "value": {
                              "streetAddress": "Friedrichstraße 44",
                              "addressRegion": "Berlin",
                              "addressLocality": "Kreuzberg",
                              "postalCode": "10969"
                          }
                      },
                      "location": {
                          "type": "geo:json",
                          "value": {
                              "type": "Point",
                              "coordinates": [13.3903, 52.5075]
                          }
                      },
                      "name": {
                          "type": "Text",
                          "value": "Checkpoint Markt"
                      }
                  }]
    store_entities = []
    for store in store_dict:
        store_entities.append(orion.Entity(store))

    return store_entities



def create_shelf_entities():

     Shelf_dicts =[{
         "id":"urn:ngsi-ld:Shelf:unit001", "type":"Shelf",
         "location":{
             "type":"geo:json",
             "value":
                 { "type":"Point","coordinates":[13.3986112, 52.554699]}},
         "name":{
             "type":"Text",
             "value":"Corner Unit"},
         "maxCapacity":{
             "type":"Integer", "value":50 }},
         { "id":"urn:ngsi-ld:Shelf:unit002", "type":"Shelf",
           "location":{
               "type":"geo:json",
               "value":{"type":"Point","coordinates":[13.3987221, 52.5546640]}},
           "name": {"type":"Text", "value":"Wall Unit 1"},
           "maxCapacity":{"type":"Integer", "value":100}},
         {"id":"urn:ngsi-ld:Shelf:unit003", "type":"Shelf",
          "location":{
              "type":"geo:json", "value":{"type":"Point","coordinates":[13.3987221, 52.5546640]}},
          "name":{
              "type":"Text", "value":"Wall Unit 2"},
          "maxCapacity":{
              "type":"Integer", "value":100}},
         {"id":"urn:ngsi-ld:Shelf:unit004", "type":"Shelf",
          "location":
              {"type":"geo:json", "value":
                  {"type":"Point","coordinates":[13.390311, 52.507522]}},
          "name":{
              "type":"Text", "value":"Corner Unit"},
          "maxCapacity":{
              "type":"Integer", "value":50}},
         {"id":"urn:ngsi-ld:Shelf:unit005", "type":"Shelf",
          "location":{
              "type":"geo:json","value":
                  {"type":"Point","coordinates":[13.390309, 52.50751]}},
          "name":{
              "type":"Text", "value":"Long Wall Unit"},
          "maxCapacity":{
              "type":"Integer", "value":200
          }}]
     shelf_entities = []
     for entity in Shelf_dicts:
         shelf_entities.append(orion.Entity(entity))

     return shelf_entities


def create_product_entities():
    product_dict = [{"id":"urn:ngsi-ld:Product:001", "type":"Product",
                     "name":{"type":"Text", "value":"Beer"},
                     "size":{"type":"Text", "value": "S"},
                     "price":{"type":"Integer", "value": 99}},
                    {"id":"urn:ngsi-ld:Product:002", "type":"Product",
                     "name":{
                         "type":"Text", "value":"Red Wine"},
                     "size":{"type":"Text", "value": "M"},
                     "price":{"type":"Integer", "value": 1099}},
                    {"id":"urn:ngsi-ld:Product:003", "type":"Product",
                     "name":{
                         "type":"Text", "value":"White Wine"},
                     "size":{"type":"Text", "value": "M"},
                     "price":{"type":"Integer", "value": 1499}},
                    {"id":"urn:ngsi-ld:Product:004", "type":"Product",
                     "name":{"type":"Text", "value":"Vodka"},
                     "size":{"type":"Text", "value": "XL"},
                     "price":{ "type":"Integer", "value": 5000}
                     }
                    ]

    product_entities = []
    for product in product_dict:
        product_entities.append(orion.Entity(product))

    return product_entities





if __name__=="__main__":

    # setup logging
    # before the first initalization the log_config.yaml.example file needs to be modified

    config.setup_logging()


    CONFIG = config.Config('config.json')
    ORION_CB = orion.Orion(CONFIG)
    ORION_CB.sanity_check()

    store_entities = create_store_entities()
    for store in store_entities:
        ORION_CB.post_json(store.get_json())

    shelf_entities = create_shelf_entities()
    for shelf in shelf_entities:
        ORION_CB.post_json(shelf.get_json())


    product_entities = create_product_entities()
    for product in product_entities:
        ORION_CB.post_json(product.get_json())


    # get infos for shelves
    for shelf in shelf_entities:
        print(ORION_CB.get_entity_attribute_list(entity_name=shelf.id, attr_name_list=shelf.get_attributes()))

    # shelf 04 und 05 zu store 002
    list_ref_tuples = []
    for i in range(len(shelf_entities)):
        if (i == 3) or (i == 4):
            list_ref_tuples.append((store_entities[1], shelf_entities[i]))
        else:
            list_ref_tuples.append((store_entities[0], shelf_entities[i]))

    for tup in list_ref_tuples:
        rel = orion.Relationship(ref_object=tup[0], subject=tup[1])
        rel.add_ref()
        ORION_CB.post_relationship(json_data=rel.get_json())

    # get infos again to see the new refStore attribute
    for shelf in shelf_entities:
        print(f"These are the attributes of entity {shelf.id}:")
        print(ORION_CB.get_entity_attribute_list(entity_name=shelf.id, attr_name_list=shelf.get_attributes()))

    # reading from parent entity to child entity
    for store in store_entities:
        children = ORION_CB.get_subjects(object_entity_name=store.id, object_entity_type=store.type)
        print(f"These are the subjects / children of {store.id} : {children} ")
        #print(ORION_CB.get_subjects(object_entity_name=store.id, object_entity_type=store.type))


    # reading from child entity to parent entity
    for shelf in shelf_entities:
        parents = ORION_CB.get_objects(subject_entity_name=shelf.id, subject_entity_type=shelf.type, object_type="Store")
        print(f"These are the objects / parents of {shelf.id}: {parents} ")

    # get all associated attributes
    for shelf in shelf_entities:
        data = ORION_CB.get_associated(name=shelf.id, type=shelf.type)
        print(json.dumps(data, indent=4))

    for store in store_entities:
        data = ORION_CB.get_associated(name=store.id, type=store.type)
        print(json.dumps(data, indent=4))

    # After the end of the tutorial delete all entities
    ORION_CB.delete_all_entities()



