import datetime
from typing import List, Dict, Set, Optional

from filip.semantics.ontology_parser.vocabulary_builder import VocabularyBuilder
from filip.semantics.vocabulary import Source, IdType, Vocabulary, \
    DatatypeType, Datatype, Class
from filip.semantics.vocabulary import Entity, CombinedDataRelation, \
    CombinedObjectRelation, CombinedRelation


"""
The PostProcessing gets called after the vocabulary was parsed from sources

The postprocessing has the goal to add predefined values, 
compute combinedRelations, reload usersettings, and precompute 
information as: duplicate labels or sort relations
"""


def post_process_vocabulary(vocabulary: Vocabulary,
                            old_vocabulary: Optional[Vocabulary] = None):
    """Main methode to be called for post processing

    Args:
        vocabulary (Vocabulary): Freshly parsed Vocabulary
        old_vocabulary (Vocabulary): Existing Vocabulary of which the settings
            should be overtaken

    Returns:
        None
    """

    # all methods have to reset the state that they are editing first.
    # consecutive calls of post_process_vocabulary need to have the same result
    voc_builder = VocabularyBuilder(vocabulary=vocabulary)
    add_predefined_source(voc_builder)
    add_predefined_datatypes(voc_builder)
    add_owl_thing(voc_builder)
    remove_duplicate_parents(voc_builder)

    log_and_clear_dependencies(voc_builder)
    compute_ancestor_classes(voc_builder)
    compute_child_classes(voc_builder)
    combine_relations(voc_builder)

    if old_vocabulary is not None:
        transfer_settings(new_vocabulary=vocabulary,
                          old_vocabulary=old_vocabulary)
    make_labels_fiware_safe(voc_builder)

    sort_relations(voc_builder)
    mirror_object_property_inverses(voc_builder)


def add_predefined_source(voc_builder: VocabularyBuilder):
    """ Add a special source to the vocabulary: PREDEFINED

    Args:
        voc_builder: Builder object for Vocabulary

    Returns:
        None
    """
    if "PREDEFINED" not in voc_builder.vocabulary.sources:
        source = Source(was_link=False, source_path="/",
                        source_name="Predefined",
                        timestamp=datetime.datetime.now(), predefined=True)
        voc_builder.add_source(source, "PREDEFINED")


def log_and_clear_dependencies(voc_builder: VocabularyBuilder):
    """remove all references to entities that are not in the vocabulary to
        prevent program errrors as we remove information we need to reparse the
        source each time a new source is added as than the dependency
        could be valid. Further log the found dependencies for the user to
        display

    Args:
        voc_builder: Builder object for Vocabulary

    Returns:
        None
    """
    for ontology in voc_builder.vocabulary.sources.values():
        ontology.treat_dependency_statements(voc_builder.vocabulary)


def add_predefined_datatypes(voc_builder: VocabularyBuilder):
    """ Add predefinded datatypes to the PREDEFINED source; they are not
        included in an OWL file

    Args:
        voc_builder: Builder object for Vocabulary

    Returns:
        None
    """
    # Test if datatypes were already added, if yes skip
    if 'http://www.w3.org/2002/07/owl#rational' in \
            voc_builder.vocabulary.datatypes.keys():
        return

    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2002/07/owl#rational",
                 comment="All numbers allowed",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2002/07/owl#real",
                 comment="All whole numbers allowed",
                 type=DatatypeType.number,
                 number_decimal_allowed=False))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral",
                 comment="All strings allowed",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                 comment="XML Syntax required",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2000/01/rdf-schema#Literal",
                 comment="All strings allowed",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#anyURI",
                 comment="Needs to start with http://",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#base64Binary",
                 comment="Base64Binary",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#boolean",
                 comment="True or False",
                 type=DatatypeType.enum,
                 enum_values=["True", "False"]))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#byte",
                 comment="Byte Number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-128,
                 number_range_max=127))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#dateTime",
                 comment="Date with possible timezone",
                 type=DatatypeType.date))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#dateTimeStamp",
                 comment="Date",
                 type=DatatypeType.date))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#decimal",
                 comment="All decimal numbers",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#double",
                 comment="64 bit decimal",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#float",
                 comment="32 bit decimal",
                 type=DatatypeType.number,
                 number_decimal_allowed=True))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#hexBinary",
                 comment="Hexadecimal",
                 type=DatatypeType.string,
                 allowed_chars=["0", "1", "2", "3", "4", "5", "6", "7", "8",
                                "9","a", "b", "c", "d", "e", "f"]))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#int",
                 comment="Signed 32 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-2147483648,
                 number_range_max=2147483647))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#integer",
                 comment="All whole numbers",
                 type=DatatypeType.number,
                 number_decimal_allowed=False))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#language",
                 comment="Language code, e.g: en, en-US, fr, or fr-FR",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#long",
                 comment="Signed 64 bit integer",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-9223372036854775808,
                 number_range_max=9223372036854775807,
                 number_decimal_allowed=False))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#Name",
                 comment="Name string (dont start with number)",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#NCName",
                 comment="Name string : forbidden",
                 type=DatatypeType.string,
                 forbidden_chars=[":"]))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#negativeInteger",
                 comment="All negative whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_max=-1
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#NMTOKEN",
                 comment="Token string",
                 type=DatatypeType.string))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
                 comment="All positive whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#nonPositiveInteger",
                 comment="All negative whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_max=-1
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#normalizedString",
                 comment="normalized String",
                 type=DatatypeType.string
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#positiveInteger",
                 comment="All positive whole numbers",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#short",
                 comment="signed 16 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=-32768,
                 number_range_max=32767
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#string",
                 comment="String",
                 type=DatatypeType.string
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#token",
                 comment="String",
                 type=DatatypeType.string
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedByte",
                 comment="unsigned 8 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=255
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedInt",
                 comment="unsigned 32 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=4294967295
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedLong",
                 comment="unsigned 64 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=18446744073709551615
                 ))
    voc_builder.add_predefined_datatype(
        Datatype(iri="http://www.w3.org/2001/XMLSchema#unsignedShort",
                 comment="unsigned 16 bit number",
                 type=DatatypeType.number,
                 number_has_range=True,
                 number_range_min=0,
                 number_range_max=65535
                 ))


def add_owl_thing(voc_builder: VocabularyBuilder):
    """Add owl_thing class to the vocabulary in the predefined source

    By definition each class is a subclass of owl:thing and owl:thing can be a
    target of relation but owl thing is never mentioned explicitly in ontology
    files.

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    root_class = Class(iri="http://www.w3.org/2002/07/owl#Thing",
                       comment="Predefined root_class",
                       label="Thing",
                       predefined=True)

    # as it is the root object it is only a parent of classes which have no
    # parents yet
    for class_ in voc_builder.vocabulary.get_classes():
        if class_.parent_class_iris == []:
            class_.parent_class_iris.insert(0, root_class.iri)

    if root_class.iri not in voc_builder.vocabulary.classes:
        voc_builder.add_class(root_class)
        root_class.source_id = "PREDEFINED"


def remove_duplicate_parents(voc_builder: VocabularyBuilder):
    for class_ in voc_builder.vocabulary.classes.values():
        class_.parent_class_iris = list(dict.fromkeys(class_.parent_class_iris))


def make_labels_fiware_safe(voc_builder: VocabularyBuilder):
    """Make the labels of all entities FIWARE safe, so that they can be used as
     field keys

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    vocabulary = voc_builder.vocabulary
    for entity in vocabulary.get_all_entities():
        entity.label = entity.make_label_safe(entity.label)

        if entity.is_label_protected(entity.label):
            entity.label = "Unallowed_Label"

def compute_ancestor_classes(voc_builder: VocabularyBuilder):
    """Compute all ancestor classes of classes

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    vocabulary = voc_builder.vocabulary
    # clear state
    for class_ in vocabulary.get_classes():
        class_.ancestor_class_iris = []

    for class_ in vocabulary.get_classes():
        queue: List[str] = []
        queue.extend(class_.parent_class_iris)

        while len(queue) > 0:
            parent = queue.pop()

            if not voc_builder.entity_is_known(parent):
                # todo: parsing log
                continue

            class_.ancestor_class_iris.append(parent)
            grand_parents = \
                vocabulary.get_class_by_iri(parent).parent_class_iris

            for grand_parent in grand_parents:
                if grand_parent not in class_.ancestor_class_iris:
                    # prevent infinite loop if inheritence circle
                    queue.append(grand_parent)


def compute_child_classes(voc_builder: VocabularyBuilder):
    """Compute all child classes of classes

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    vocabulary = voc_builder.vocabulary
    # clear state
    for class_ in vocabulary.get_classes():
        class_.child_class_iris = []

    for class_ in vocabulary.get_classes():
        for parent in class_.ancestor_class_iris:

            if not voc_builder.entity_is_known(parent):
                # todo: parsing log
                continue

            parent_class = vocabulary.get_class_by_iri(parent)
            parent_class.child_class_iris.append(class_.iri)


def combine_relations(voc_builder: VocabularyBuilder):
    """Compute all CombinedRelations

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    vocabulary = voc_builder.vocabulary
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

            if not voc_builder.entity_is_known(ancestor_iri):
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
                voc_builder.add_combined_data_relation_for_class(
                    class_iri=class_.iri, cdata=combi)
            elif vocabulary.is_id_of_type(property_iri, IdType.object_property):
                id = "combined-object-relation|{}|{}".format(
                    class_.iri, property_iri)
                combi = CombinedObjectRelation(id=id,
                                               property_iri=property_iri,
                                               relation_ids=rel_list,
                                               class_iri=class_.iri)
                voc_builder.add_combined_object_relation_for_class(
                    class_iri=class_.iri, crel=combi)
            else:
                pass
                # todo?


def sort_relations(voc_builder: VocabularyBuilder):
    """sort relations alphabetically according to their labels

    Args:
        voc_builder: Builder object for Vocabulary
    Returns:
        None
    """
    vocabulary = voc_builder.vocabulary

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


def mirror_object_property_inverses(voc_builder: VocabularyBuilder):
    """inverses could only be given for 1 obj_prop of the pair and needs to be
    derived for the other also we could have the inverse inside an other import
    (there for done in postprocessing)

    Args:
        voc_builder: Builder object for Vocabulary

    Returns:
        Nonde
    """
    # the state is not cleared, instead add_inverse_property_iri() makes sure
    # that there will be no duplicates
    # as it is a set
    vocabulary = voc_builder.vocabulary

    for obj_prop_iri in vocabulary.object_properties:
        obj_prop = vocabulary.get_object_property(obj_prop_iri)

        for inverse_iri in obj_prop.inverse_property_iris:
            inverse_prop = vocabulary.get_object_property(inverse_iri)
            inverse_prop.add_inverse_property_iri(obj_prop_iri)
            
            
def transfer_settings(new_vocabulary: Vocabulary, old_vocabulary: Vocabulary):
    """
    Transfer all the user made settings (labels, key_colums, ia_agent,..)
    from an old vocabulary to a new vocabulary

    Args:
        new_vocabulary (Vocabulary): Vocabulary to which the settings should be
            transferred
        old_vocabulary (Vocabulary): Vocabulary of which the settings should be
            transferred

    Returns:
        None
    """

    # agent&device settings
    for class_ in old_vocabulary.get_classes():
        if class_.iri in new_vocabulary.classes:
            new_vocabulary.get_class_by_iri(class_.iri).is_agent_class = \
                class_.is_agent_class
            new_vocabulary.get_class_by_iri(class_.iri).is_iot_class = \
                class_.is_iot_class

    # label settings
    for entity in old_vocabulary.get_all_entities():
        new_entity = new_vocabulary.get_entity_by_iri(entity.iri)
        if new_entity is not None:
            new_entity.user_set_label = entity.user_set_label

    # combined relation settings
    combined_relation_pairs = [(old_vocabulary.combined_object_relations,
                                new_vocabulary.combined_object_relations),
                               (old_vocabulary.combined_data_relations,
                                new_vocabulary.combined_data_relations)]
    for (old_list, new_list) in combined_relation_pairs:
        for cr_id in old_list:
            if cr_id in new_list:

                old_cr = old_vocabulary.get_combined_relation_by_id(cr_id)
                new_cr = new_vocabulary.get_combined_relation_by_id(cr_id)
                new_cr.is_key_information = old_cr.is_key_information
                new_cr.inspect = old_cr.inspect

    # CombinedDataRelation additional Settings
    for cdr_id in old_vocabulary.combined_data_relations:
        if cdr_id in new_vocabulary.combined_data_relations:
            old_cdr = old_vocabulary.get_combined_data_relation_by_id(cdr_id)
            new_cdr = new_vocabulary.\
                get_combined_data_relation_by_id(cdr_id)
            new_cdr.type = old_cdr.type