from typing import List, Dict, Set

from filip.semantics.vocabulary import Source, IdType, Vocabulary, DatatypeType, Datatype, Class
from filip.semantics.vocabulary import Entity, CombinedDataRelation, CombinedObjectRelation, CombinedRelation


"""
The PostProcessing gets called after the vocabulary was parsed from sources

The postprocessing has the goal to add predefined values, 
compute combinedRelations, reload usersettings, and precompute 
information as: duplicate labels or sort relations
"""


def post_process_vocabulary(vocabulary: Vocabulary, project_id:str):
    """Main methode to be called for post processing

    Args:
        vocabulary (Vocabulary): Freshly parsed Vocabulary
        project_id (str): Id of the project

    Returns:

    """

    # all methods have to reset the state that they are editing first.
    # consecutive calls of post_process_vocabulary need to have the same result

    add_predefined_source(vocabulary)
    add_predefined_datatypes(vocabulary)
    add_owl_thing(vocabulary)

    log_and_clear_dependencies(vocabulary)
    compute_ancestor_classes(vocabulary)
    compute_child_classes(vocabulary)
    combine_relations(vocabulary)

    reload_user_settings(vocabulary, project_id=project_id)
    make_labels_fiware_safe(vocabulary)
    check_for_duplicate_labels(vocabulary)

    sort_relations(vocabulary)
    mirror_object_property_inverses(vocabulary)


def add_predefined_source(vocabulary: Vocabulary):
    """ Add a special source to the vocabulary: PREDEFINED

    Args:
        vocabulary (Vocabulary)

    Returns:
        None
    """
    if "PREDEFINED" not in vocabulary.sources:
        source = Source(was_link=False, source_path="/",
                        source_name="Predefined",
                        timestamp="", predefined=True)
        vocabulary.add_source(source, "PREDEFINED")


def log_and_clear_dependencies(vocabulary: Vocabulary):
    """remove all references to entities that are not in the vocabulary to
        prevent program errrors as we remove information we need to reparse the
        source each time a new source is added as than the dependency
        could be valid. Further log the found dependencies for the user to
        display

    Args:
        vocabulary (Vocabulary)

    Returns:
        None
    """
    for ontology in vocabulary.sources.values():
        ontology.treat_dependency_statements(vocabulary)


def add_predefined_datatypes(vocabulary: Vocabulary):
    """ Add predefinded datatypes to the PREDEFINED source; they are not
        included in an OWL file

    Args:
        vocabulary (Vocabulary)

    Returns:
        None
    """
    if 'http://www.w3.org/2002/07/owl#rational' in vocabulary.datatypes.keys():
        return

    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2002/07/owl#rational",
                 comment="All numbers allowed",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2002/07/owl#real",
                 comment="All whole numbers allowed",
                 type=DatatypeType.number,
                 number_decimal_allowed=False))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral",
                 comment="All strings allowed",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                 comment="XML Syntax required",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2000/01/rdf-schema#Literal",
                 comment="All strings allowed",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#anyURI",
                 comment="Needs to start with http://",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#base64Binary",
                 comment="Base64Binary",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#boolean",
                 comment="True or False",
                 type=DatatypeType.enum,
                 enum_values=["True", "False"]))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#byte",
                 comment="Byte Number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-128,
                 number_range_max=127))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#dateTime",
                 comment="Date with possible timezone",
                 type=DatatypeType.date))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#dateTimeStamp",
                 comment="Date",
                 type=DatatypeType.date))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#decimal",
                 comment="All decimal numbers",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#double",
                 comment="64 bit decimal",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#float",
                 comment="32 bit decimal",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#hexBinary",
                 comment="Hexadecimal",
                 type=DatatypeType.string,
                 allowed_chars=["0", "1", "2", "3", "4", "5", "6", "7", "8",
                                "9","a", "b", "c", "d", "e", "f"]))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#int",
                 comment="Signed 32 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-2147483648,
                 number_range_max=2147483647))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#integer",
                 comment="All whole numbers",
                 type=DatatypeType.number,
                 number_decimal_allowed=False))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#language",
                 comment="Language code, e.g: en, en-US, fr, or fr-FR",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#long",
                 comment="Signed 64 bit integer",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-9223372036854775808,
                 number_range_max=9223372036854775807,
                 number_decimal_allowed=False))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#Name",
                 comment="Name string (dont start with number)",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#NCName",
                 comment="Name string : forbidden",
                 type=DatatypeType.string,
                 forbidden_chars=[":"]))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#negativeInteger",
                 comment="All negative whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_max=-1
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#NMTOKEN",
                 comment="Token string",
                 type=DatatypeType.string))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
                 comment="All positive whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#nonPositiveInteger",
                 comment="All negative whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_max=-1
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#normalizedString",
                 comment="normalized String",
                 type=DatatypeType.string
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#positiveInteger",
                 comment="All positive whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#short",
                 comment="signed 16 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-32768,
                 number_range_max=32767
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#string",
                 comment="String",
                 type=DatatypeType.string
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#token",
                 comment="String",
                 type=DatatypeType.string
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedByte",
                 comment="unsigned 8 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=255
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedInt",
                 comment="unsigned 32 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=4294967295
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedLong",
                 comment="unsigned 64 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=18446744073709551615
                 ))
    vocabulary.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedShort",
                 comment="unsigned 16 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=65535
                 ))


def add_owl_thing(vocabulary: Vocabulary):
    """Add owl_thing class to the vocabulary in the predefined source

    By definition each class is a subclass of owl:thing and owl:thing can be a
    target of relation but owl thing is never mentioned explicitly in ontology
    files.

    Args:
        vocabulary (Vocabulary)
    Returns:
        None
    """
    root_class = Class(iri="http://www.w3.org/2002/07/owl#Thing",
                       comment="Predefined root_class",
                       label="Thing",
                       predefined=True)

    # as it is the root object it is only a parent of classes which have no
    # parents yet
    for class_ in vocabulary.get_classes():
        if class_.parent_class_iris == []:
            class_.parent_class_iris.insert(0, root_class.iri)

    if root_class.iri not in vocabulary.classes:
        vocabulary.add_class(root_class)
        root_class.source_id = "PREDEFINED"


def reload_user_settings(vocabulary: Vocabulary, project_id: str):
    """Transfer the user made settings from the old vocabulary to the new pared
        vocabulary

    Args:
        vocabulary (Vocabulary): Vocabulary of project
        project_id (str): Id of project
    Returns:
        None
    """
    old_vocabulary:Vocabulary = data_manager.access_object(project_id=project_id,
                                                           object_identifier=DataIdentifier.vocabulary)
    old_vocabulary.transfer_settings(vocabulary)


def make_labels_fiware_safe(vocabulary: Vocabulary):
    """Make the labels of all entities FIWARE safe, so that they can be used as
     field keys

    Args:
        vocabulary (Vocabulary)
    Returns:
        None
    """
    for entity in vocabulary.get_all_entities():
        entity.label = entity.make_label_safe(entity.label)

        if entity.is_label_protected(entity.label):
            entity.label = "Unallowed_Label"


def check_for_duplicate_labels(vocabulary: Vocabulary):
    """Check and log all entity labels that are not unique

    Args:
       vocabulary (Vocabulary)
    Returns:
        None
    """

    vocabulary.conflicting_label_entities = {}
    vocabulary.conflicting_original_labels.clear()

    # original label counter
    original_labels_first_encounter: Set[str] = set()

    # maps label to list of entities with that label
    used_labels: Dict[str, List[Entity]] = {}
    duplicate_labels = set()

    # process entities to find conflicts, ignore individuals and datatypes as
    # they are never used as Keys in FIWARE
    # Multiple individuals/datatypes can have the same label,
    # this is no issue for the system
    # it may disturb the user, but it is his own choice
    entities_to_check = [vocabulary.classes,
                         vocabulary.object_properties,
                         vocabulary.data_properties,
                         # vocabulary.datatypes,
                         # vocabulary.individuals
                         ]

    for entity_list in entities_to_check:
        for entity in entity_list.values():
            label = entity.get_label()
            if label in used_labels:
                duplicate_labels.add(label)
                used_labels[label].append(entity)
            else:
                used_labels[label] = [entity]

            if entity.get_original_label() in original_labels_first_encounter:
                vocabulary.conflicting_original_labels.add(
                    entity.get_original_label())
            else:
                original_labels_first_encounter.add(entity.get_original_label())

    # sort duplicate_labels to have alpahbatical order in list
    dup_list = list(duplicate_labels)
    dup_list = sorted(dup_list, key=str.casefold)

    # store and log findings
    for label in dup_list:
        vocabulary.conflicting_label_entities[label] = used_labels[label]


def compute_ancestor_classes(vocabulary: Vocabulary):
    """Compute all ancestor classes of classes

    Args:
       vocabulary (Vocabulary)
    Returns:
        None
    """

    # clear state
    for class_ in vocabulary.get_classes():
        class_.ancestor_class_iris = []

    for class_ in vocabulary.get_classes():
        queue: List[str] = []
        queue.extend(class_.parent_class_iris)

        while len(queue) > 0:
            parent = queue.pop()

            if not vocabulary.entity_is_known(parent):
                # todo: parsing log
                continue

            class_.ancestor_class_iris.append(parent)
            grand_parents = \
                vocabulary.get_class_by_iri(parent).parent_class_iris

            for grand_parent in grand_parents:
                if grand_parent not in class_.ancestor_class_iris:
                    # prevent infinite loop if inheritence circle
                    queue.append(grand_parent)


def compute_child_classes(vocabulary: Vocabulary):
    """Compute all child classes of classes

    Args:
       vocabulary (Vocabulary)
    Returns:
        None
    """
    # clear state
    for class_ in vocabulary.get_classes():
        class_.child_class_iris = []

    for class_ in vocabulary.get_classes():
        for parent in class_.ancestor_class_iris:

            if not vocabulary.entity_is_known(parent):
                # todo: parsing log
                continue

            parent_class = vocabulary.get_class_by_iri(parent)
            parent_class.child_class_iris.append(class_.iri)


def combine_relations(vocabulary: Vocabulary):
    """Compute all CombinedRelations

    Args:
       vocabulary (Vocabulary)
    Returns:
        None
    """
    # clear state
    vocabulary.combined_object_relations.clear()
    vocabulary.combined_data_relations.clear()

    for class_ in vocabulary.get_classes():
        class_.combined_object_relation_ids = []
        class_.combined_data_relation_ids = []

    for class_ in vocabulary.get_classes():

        relations_with_property_iri = {}

        all_relation_ids = []
        all_relation_ids.extend(class_.get_relation_ids())
        for ancestor_iri in class_.ancestor_class_iris:

            if not vocabulary.entity_is_known(ancestor_iri):
                #todo: parsing log
                continue
            ancestor = vocabulary.get_class_by_iri(ancestor_iri)
            all_relation_ids.extend(ancestor.get_relation_ids())

        for relation_id in all_relation_ids:
            relation = vocabulary.get_relation_by_id(id=relation_id)
            property_iri = relation.property_iri

            if property_iri not in relations_with_property_iri:
                relations_with_property_iri[property_iri] = []

            relations_with_property_iri[property_iri].append(relation_id)

        for property_iri, rel_list in relations_with_property_iri.items():

            # These ids should be derived, so that the same combined relation
            # always ends up with the same id
            # as a class can only have 1 combined relation of a property these
            # ids are unique by keeping the ids always the same, we can store
            # informations more efficently in the database (settings)

            # if a property iri is not known while parsing an ontology
            # (depency not yet parsed) the relations with that
            # property are going to get ignored, maybe a not should be displayed
            if vocabulary.is_id_of_type(property_iri, IdType.data_property):
                id = "combined-data-relation|{}|{}".format(class_.iri,
                                                           property_iri)
                combi = CombinedDataRelation(id=id, property_iri=property_iri,
                                             relation_ids=rel_list,
                                             class_iri=class_.iri)
                vocabulary.add_combined_data_relation_for_class(
                    class_iri=class_.iri, cdata=combi)
            elif vocabulary.is_id_of_type(property_iri, IdType.object_property):
                id = "combined-object-relation|{}|{}".format(
                    class_.iri, property_iri)
                combi = CombinedObjectRelation(id=id,
                                               property_iri=property_iri,
                                               relation_ids=rel_list,
                                               class_iri=class_.iri)
                vocabulary.add_combined_object_relation_for_class(
                    class_iri=class_.iri, crel=combi)
            else:
                pass
                # todo?


def sort_relations(vocabulary: Vocabulary):
    """sort relations alphabetically according to their labels

    Args:
        vocabulary (Vocabulary)
    Returns:
        None
    """

    for class_ in vocabulary.get_classes():
        cors = class_.get_combined_object_relations(vocabulary)
        class_.combined_object_relation_ids = \
            sort_list_of_combined_relations(cors, vocabulary)

        cdrs = class_.get_combined_data_relations(vocabulary)
        class_.combined_data_relation_ids = \
            sort_list_of_combined_relations(cdrs, vocabulary)


def sort_list_of_combined_relations(combined_relations: List[CombinedRelation],
                                    vocabulary: Vocabulary) -> List[str]:
    """sort given CombinedRelations according to their labels

    Args:
        vocabulary (Vocabulary)
        combined_relations (List[CombinedRelation]): CRs to sort
    Returns:
        List[str], list of cr_id, sorted according to their label
    """

    property_dic = {}

    for cor in combined_relations:
        property_iri = cor.property_iri
        label = cor.get_property_label(vocabulary=vocabulary)
        property_dic[label + property_iri] = cor.id
        # combine label with iri to prevent an error due to two identical labels
    sorted_property_dic = sorted(property_dic.items())

    sorted_cor_ids = []
    for pair in sorted_property_dic:
        sorted_cor_ids.append(pair[1])
    return sorted_cor_ids


def mirror_object_property_inverses(vocabulary: Vocabulary):
    """inverses could only be given for 1 obj_prop of the pair and needs to be
    derived for the other also we could have the inverse inside an other import
    (there for done in postprocessing)

    Args:
        vocabulary (Vocabulary)

    Returns:
        Nonde
    """
    # the state is not cleared, instead add_inverse_property_iri() makes sure
    # that there will be no duplicates
    # as it is a set

    for obj_prop_iri in vocabulary.object_properties:
        obj_prop = vocabulary.get_object_property(obj_prop_iri)

        for inverse_iri in obj_prop.inverse_property_iris:
            inverse_prop = vocabulary.get_object_property(inverse_iri)
            inverse_prop.add_inverse_property_iri(obj_prop_iri)
