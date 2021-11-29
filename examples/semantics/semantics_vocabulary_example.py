"""
# Examples for modelling a vocabulary with ontologies.
# The ontologies will be added to a vocabulary,
# the vocabulary configured
# and exported as a python model file
"""
from filip.semantics.vocabulary import DataFieldType
from filip.semantics.vocabulary.vocabulary import VocabularySettings
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


if __name__ == '__main__':

    # # 1. Creating a new vocabulary
    #
    # First we create a new blank vocabulary
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
    # A vocabulary can also contain Individuals. An individual is an
    # immutable instance of a class without values. It can be regarded as a
    # type of enum value.

    # ## 1.1 To automatically adapt the label of the entities in the ontology we
    # can pass some settings to our vocabulary:
    settings = VocabularySettings(
        pascal_case_class_labels=True,
        pascal_case_individual_labels=True,
        camel_case_property_labels=True,
        camel_case_datatype_labels=True,
        pascal_case_datatype_enum_labels=True
    )
    # We create our new blank vocabulary:
    vocabulary = VocabularyConfigurator.create_vocabulary(settings=settings)

    # # 2. Adding ontologies
    #
    # We now add the wanted ontologies to our vocabulary.
    # The ontologies can be inserted via a file, a weblink or as content string.
    # The ontologies need to be Turtle encoded
    # We always get a new vocabulary object returned

    # ### 2.0.1 as file
    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
            vocabulary=vocabulary,
            path_to_file='./ontology_files/building circuits.owl')

    # ### 2.0.2 as string
    with open('./ontology_files/ParsingTesterOntology.ttl', 'r') as file:
        data = file.read()
    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_string(
            vocabulary=vocabulary,
            source_content=data,
            source_name="ParsingExample"
        )

    # ### 2.0.3 as link
    #
    # if no source name is given, the name is extracted form the uri,
    # here: "saref.tll". Only for demonstration of the function, we do not need
    # saref in our example vocabulary

    vocabulary = \
        VocabularyConfigurator.add_ontology_to_vocabulary_as_link(
            vocabulary=vocabulary,
            link="https://ontology.tno.nl/saref.ttl"
        )

    # ## 2.1 Inspect added sources
    #
    # The ontologies are added to the vocabulary as sources.
    # We can check the details of already contained sources by accessing the
    # source list.
    # Here we print out the names and adding time of all contained sources:
    print("\u0332".join("Sources in vocabulary:"))
    for source in vocabulary.get_source_list():
        print(f'Name: {source.source_name}; Added: {source.timestamp}; '
              f'Id: {source.id}')
    print("")

    # ## 2.2 Predefined source
    #
    # Each vocabulary always contains the source "Predefined". This
    # source
    # contains all fundamental objects of an ontology, as owl:Thing and
    # predefined datatype.

    # ## 2.3 Parsing Logs
    #
    # To see if an ontology could be parsed completely we have to look at
    # the parsing logs:
    print("\u0332".join("Parsing Logs of vocabulary:"))
    print(f'{VocabularyConfigurator.get_parsing_logs(vocabulary)}\n')
    # Here we see that a statement in the ParsingTesterOntology was dropped
    # as it was in a non supported OR format. The semantic logic is not
    # compatible with the OR combination of two relations.

    # ## 2.4 Removing an added source
    #
    # We could still use the rest of the ParsingTesterOntology, as only
    # the problematic statement was dropped or we remove it again from our
    # vocabulary. Here we need the source id, which was given to us in
    # the parsing logs. We could also look it up in the vocabulary as shown
    # above

    source_id = [source.id for source in vocabulary.get_source_list() if
                 source.source_name == "ParsingExample"][0]

    vocabulary = VocabularyConfigurator.delete_source_from_vocabulary(
                    vocabulary=vocabulary,
                    source_id=source_id)

    # # 3 Completeness
    #
    # Each entity (class, property, datatype, individual) is uniquely
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
    # o 'https://w3id.org/saref#UnitOfMeasure'
    #    This entity was locally imported into the ontology by using the
    #    rdfs_tag: isDefinedBy
    #
    # For both entities only the reference is imported, and the ontology file
    # does not contain all the needed information about these entities to
    # parse them into the vocabulary. We here decide to not include these
    # sources

    # # 4 Uniqueness of labels
    #
    # Labels of entities need to unique as they represent a namespace
    # There are three separated namespaces, in which the labels need to be
    # unique:
    #   - Classes and Individuals
    #   - DataProperties and RelationProperties
    #   - Datatypes (contains already a set of predefined types)
    # Further the labels are only allowed to have alphanumerical chars and _
    # And a set of labels is blacklisted as they are keyvalues of either
    # python, fiware or the model logic.
    #
    # A vocabulary needs to be free of label conflicts before it gets exported

    # ## 4.1 Vocabulary is valid
    #
    # To check if our vocabulary is valid  we can call:
    print("\u0332".join("Vocabulary is valid:"))
    print(VocabularyConfigurator.is_vocabulary_valid(vocabulary))
    print("")

    # ## 4.2 Label Conflicts
    #
    # To check which label conflicts our vocabulary posses we can call:
    print("\u0332".join("Label Conflicts:"))
    print(VocabularyConfigurator.get_label_conflicts_in_vocabulary(vocabulary))
    print("")

    # # 5 Resolving Label Conflicts
    #
    # We can rename entities by setting their label to resolve conflicts
    # or to better adapt the ontology to our liking.
    # To get the used label of an entity always use .get_label()

    # The easiest way to access an entity is the get_entity_by_iri function
    entity = vocabulary.get_entity_by_iri('https://w3id.org/saref#Sensor')
    entity.set_label("SarefSensor")


    # # 6 IoT Devices
    #
    # Currently all our classes in the vocabulary are ContextEntities.
    # They can be used to model real world properties, but if we want to
    # interact with the world we need to configure some classes as device
    # classes. An instance of a device class represents 1 Iot-Device in the
    # real world, and can interact with it.
    #
    # An device class has two special subtypes of DataRelations:
    #   - The CommandRelations, contain a set of commands that can be send to
    #   device
    #   - The DeviceAttributeRelations, contain a set of DeviceAttributes. A
    #   DeviceAttribute models and reads out one measurement/datapoint of the
    #   device
    #
    # Which DataProperties are CommandProperties or DeviceAttributeProperties
    # is defined globally for the whole vocabulary.
    # Each class containing at least one such property is automatically
    # treated as device class
    #
    # To configure the devices of our vocabulary we change the field_type of
    # the DataProperties

    # # 6.1 Available DataProperties
    #
    # To see a list of all our available data-properties we can use:
    print("\u0332".join("Available Data-properties:"))
    for prop_iri, prop in vocabulary.data_properties.items():
        print(f'Label: {prop.get_label()}, Iri: {prop.iri}')
    print("")
    # This logic is the same if we want to look into classes,
    # object-properties, datatypes or individuals of our vocabulary.

    # # 6.2 Accessing properties
    #
    # We access the wanted properties over the specialised getter,
    # the general getter, or directly
    vocabulary.get_data_property(
        "http://www.semanticweb.org/building#controlCommand").field_type = \
        DataFieldType.command
    vocabulary.get_entity_by_iri(
        "http://www.semanticweb.org/building#measurement").field_type = \
        DataFieldType.device_attribute
    vocabulary.get_entity_by_iri(
        "http://www.semanticweb.org/building#state").field_type = \
        DataFieldType.device_attribute

    # To see which classes are now device classes we can use:
    print("\u0332".join("Device Classes:"))
    for class_ in vocabulary.get_classes():
        if class_.is_iot_class(vocabulary=vocabulary):
            print(f'Label: {class_.get_label()}, Iri: {class_.iri}')
    print("")

    # # 7 Exporting Vocabulary to models
    #
    # We export our configured dictionary as python models.
    # On the export each class is converted to a SemanticClass Model and gets a
    # property field for each CombinedRelation it possess.
    # A CombinedObjectRelation gets converted to a RelationField that will
    # point to other instances of SemanticClass models.
    # A CombinedDataRelation gets converted to a :
    #  - DataField that will contain a list of basic values (string, int,..),
    #       if the dataproperty has the field_type: simple
    #  - CommandFiled that will contain a list of Command objects,
    #       if the dataproperty has the field_type: command
    #  - DeviceAttributeFiled that will contain a list of DeviceAttribute
    #    objects, if the dataproperty has the field_type: device_attribute
    #
    # for more details refer to the semantics_model_example

    # The saref ontology was good to display some functions of the vocabulary
    # configurator, but to simplify the next example we remove it here
    source_id = [source.id for source in vocabulary.get_source_list() if
                 source.source_name == "saref.ttl"][0]
    vocabulary = VocabularyConfigurator.delete_source_from_vocabulary(
        vocabulary=vocabulary,
        source_id=source_id)

    # The export function takes two arguments: path_to_file and file_name
    # it creates the file: path_to_file/file_name.py overriding any existing
    # file
    VocabularyConfigurator.generate_vocabulary_models(vocabulary, ".",
                                                      "models")

