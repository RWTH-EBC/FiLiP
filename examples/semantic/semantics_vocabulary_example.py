"""
Examples for modelling a vocabulary with ontologies.
The ontologies will be added to a vocabulary,
the vocabulary configured
and exported as a python model file
"""
import logging
import requests
from filip.semantics.vocabulary_configurator import VocabularyConfigurator

from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient
from filip.models.base import FiwareHeader

if __name__ == '__main__':

    # 1. First we create a new blank vocabulary
    # A vocabulary consists out of a class hierarchy
    # Each classes posses a set of relations and inherits all relations of
    # its parents.
    # A relation consists out of a property (Relation- or DataProperty) and a
    # rule (ex: hasRoom some Room; temperature exactly 1 int)
    # A RelationProperty always refers to classes, a DataProperty to Data-types.
    #
    # In a class all relations of the same property are combined into a
    # CombinedRelation (CombinedObject- or CombinedDataRelation depending on
    # the property type)
    #
    #
    # A vocabulary can also contain Individuals. An individual is an
    # immutable instance of a class without values. It can be regarded as a
    # type of enum value.

    vocabulary = VocabularyConfigurator.create_vocabulary()

    # 2. We now add the wanted ontologies to our vocabulary.
    # The ontologies can be inserted via a file, a weblink or as content string.
    # The ontologies need to be Turtle encoded
    # We always get a new vocabulary object returned

    # as file
    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
            vocabulary=vocabulary,
            path_to_file='./ontology_files/RoomFloorOntology.ttl')

    # as string
    with open('./ontology_files/RoomFloor_Duplicate_Labels.ttl', 'r') as file:
        data = file.read()
    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_string(
            vocabulary=vocabulary,
            source_content=data,
            source_name="My Name"
        )

    # as link
    # if no source name is given, the name is extracted form the uri,
    # here: "saref.tll"
    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_link(
            vocabulary=vocabulary,
            link="https://ontology.tno.nl/saref.ttl"
        )

    # The ontologies are added to the vocabulary as sources we can check the
    # details of already contained sources by accessing the source list.
    # Here we print out the names and adding time of all contained sources:
    print("\u0332".join("Sources in vocabulary:"))
    for source in vocabulary.get_source_list():
        print(f'Name: {source.source_name}; Added: {source.timestamp}')
    print()

    # Each vocabulary always contains the source "Predefined". This source
    # contains all fundamental objects of an ontology, as owl:Thing and
    # predefined datatype.

    # todo: PARSING LOGS

    # 3. Each entity (class, property, datatype, individual) is uniquely
    # referenced by an IRI. An entity in a vocabulary file can reference
    # entities that are not present in the same file.
    # If an entity references an other entity that we have not added in the
    # vocabulary that reference gets automatically blended out.

    # We can check if entities are missing, and decide if we want to add
    # them:
    print("\u0332".join("List of missing dependencies with details:"))
    print(VocabularyConfigurator.get_missing_dependency_statements(vocabulary))
    print("")

    # To get only the missing iris we can also call:
    print("\u0332".join("List of missing dependency iris:"))
    print(VocabularyConfigurator.get_missing_dependencies(vocabulary))
    print("")

    # Here are two entities missing:
    # o 'http://www.w3.org/2006/time#TemporalEntity'
    #    This entity was globally imported into the ontology using an import
    #    statement
    # 'https://w3id.org/saref#UnitOfMeasure'
    #    This entity was locally imported into the ontology by using the
    #    rdfs_tag: isDefinedBy
    #
    # For both entities only the reference is imported, and the ontology file
    # does not contain all the needed information about these entities to
    # parse them into the vocabulary


    # 4. We can now configure the vocabulary
    # We can change the names of the the different entities in our vocabulary
    # by setting their label.
    # To get the used label of an entity always use .get_label()

    # todo

    # 5. Labels of entities need to unique as the represent a namespace
    # There are three seperated namespaces, in which the labels need to be
    # unique:
    #   - Classes and Individuals
    #   - DataProperties and RelationProperties
    #   - Datatypes (contains already a set of predefined types)
    # Further the labels are only allowed to have alphanumerical chars and _
    # And a set of labels is blacklisted as they are keyvalues of either
    # python, fiware or the model logic.
    #
    # A vocabulary needs to be free of label conflicts before it gets exported
    #
    # To check if our vocabulary has Label conflicts we can call:

    # todo

    # 6. Currently all our classes in the vocabulary are ContextEntities.
    # They can be used to model real world properties, but if we want to
    # interact with the world we need to configure some classes as device
    # classes. An instance of a device class represents 1 Iot-Device in the
    # real world, and can interact with it.
    #
    # An device class has two special subtypes of DataRelations:
    #   - The CommandRelations, contain a set of commands that can be send to
    #   device
    #   - The DeviceAttributeRelations, contain a set of DeviceAttributes. A
    #   DeviceAttribute models and reads out one measurment/datapoint of the
    #   device
    #
    # Which DataProperties are CommandProperties or DeviceAttributeProperties
    # is defined globally for the whole vocabulary.
    # Each class containing at least one such property is automatically
    # treated as device class
    #
    # To configure the devices of our vocabulary we change the field_type of
    # the DataProperties

    # todo
    vocabulary.get_data_property(
        "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
        "-ontology-25#commandProp").field_type = DataFieldType.command
    vocabulary.get_data_property(
        "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
        "-ontology-25#attributeProp").field_type = \
        DataFieldType.device_attribute

    VocabularyConfigurator.generate_vocabulary_models(
        vocabulary, "../", "models2")

    # 7. We export our configured dictionary as python models.
    # On export the each is converted to a SemanticClass Model and gets a
    # property field for each CombinedRelation it possess.
    # A CombinedObjectRelation gets converted to a RelationField that will
    # point to other instances of SemanticClass models.
    # On CombinedDataRelation gets converted to a :
    #  - DataField that will contain a list of basic values (string, int,..),
    #       if the dataproperty has the field_type: simple
    #  - CommandFiled that will contain a list of Command objects,
    #       if the dataproperty has the field_type: command
    #  - DeviceAttributeFiled that will contain a list of DeviceAttribute
    #    objects,
    #       if the dataproperty has the field_type: device_attribute
    #
    # for more details refer to the semantics_model_example
    #
    # The export function takes two arguments: path_to_file and file_name
    # it creates the file: path_to_file/file_name.py overridden any existing
    # file

    VocabularyConfigurator.generate_vocabulary_models(vocabulary, "../",
                                                      "models")

