"""
The PostProcessing gets called after the vocabulary was parsed from sources

The postprocessing has the goal to add predefined values,
compute combinedRelations, reload user settings, and precompute
information as: duplicate labels or sort relations
"""

import datetime
import re
from typing import List, Optional

import stringcase

from filip.semantics.ontology_parser.vocabulary_builder import VocabularyBuilder
from filip.semantics.vocabulary import Source, IdType, Vocabulary, \
    DatatypeType, Datatype, Class
from filip.semantics.vocabulary import CombinedDataRelation, \
    CombinedObjectRelation, CombinedRelation


class PostProcessor:
    """Class offering postprocessing as cls-methods for a vocabulary"""

    @classmethod
    def post_process_vocabulary(cls, vocabulary: Vocabulary,
                                old_vocabulary: Optional[Vocabulary] = None):
        """Main methode to be called for post processing

        Args:
            vocabulary (Vocabulary): Freshly parsed Vocabulary
            old_vocabulary (Vocabulary): Existing Vocabulary of which the
                settings should be overtaken

        Returns:
            None
        """

        # all methods have to reset the state that they are editing first.
        # consecutive calls of post_process_vocabulary need to have the same
        # result
        voc_builder = VocabularyBuilder(vocabulary=vocabulary)
        cls._set_labels(voc_builder)
        cls._add_predefined_source(voc_builder)
        cls._add_predefined_datatypes(voc_builder)
        cls._add_owl_thing(voc_builder)
        cls._remove_duplicate_parents(voc_builder)

        cls._log_and_clear_dependencies(voc_builder)
        cls._compute_ancestor_classes(voc_builder)
        cls._compute_child_classes(voc_builder)
        cls._combine_relations(voc_builder)

        if old_vocabulary is not None:
            cls.transfer_settings(new_vocabulary=vocabulary,
                                  old_vocabulary=old_vocabulary)
        cls._apply_vocabulary_settings(voc_builder)

        cls._ensure_parent_class(voc_builder)

        cls._sort_relations(voc_builder)
        cls._mirror_object_property_inverses(voc_builder)

        cls._save_initial_label_summary(vocabulary)

    @classmethod
    def _set_labels(cls, voc_builder: VocabularyBuilder):
        """ If entities have no label, extract their label from the iri

        Args:
            voc_builder: Builder object for Vocabulary

        Returns:
            None
        """
        for entity in voc_builder.vocabulary.get_all_entities():
            entity.label = entity.get_original_label()

    @classmethod
    def _add_predefined_source(cls, voc_builder: VocabularyBuilder):
        """ Add a special source to the vocabulary: PREDEFINED

        Args:
            voc_builder: Builder object for Vocabulary

        Returns:
            None
        """
        if "PREDEFINED" not in voc_builder.vocabulary.sources:
            source = Source(source_name="Predefined",
                            timestamp=datetime.datetime.now(), predefined=True)
            voc_builder.add_source(source, "PREDEFINED")

    @classmethod
    def _log_and_clear_dependencies(cls, voc_builder: VocabularyBuilder):
        """
        remove all references to entities that are not in the vocabulary to
        prevent program errrors as we remove information we need to reparse
        the source each time a new source is added as than the dependency
        could be valid. Further log the found dependencies for the user to
        display

        Args:
            voc_builder: Builder object for Vocabulary

        Returns:
            None
        """
        for ontology in voc_builder.vocabulary.sources.values():
            ontology.treat_dependency_statements(voc_builder.vocabulary)

    @classmethod
    def _add_predefined_datatypes(cls, voc_builder: VocabularyBuilder):
        """
        Add predefinded datatype_catalogue to the PREDEFINED source; they
        are not included in an OWL file

        Args:
            voc_builder: Builder object for Vocabulary

        Returns:
            None
        """
        # Test if datatype_catalogue were already added, if yes skip
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
            Datatype(
                iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral",
                comment="All strings allowed",
                type=DatatypeType.string))
        voc_builder.add_predefined_datatype(
            Datatype(
                iri="http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
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
                                    "9", "A", "B", "C", "D", "E", "F"]))
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

    @classmethod
    def _add_owl_thing(cls, voc_builder: VocabularyBuilder):
        """Add owl_thing class to the vocabulary in the predefined source

        By definition each class is a subclass of owl:thing and owl:thing can be
        a target of relation but owl thing is never mentioned explicitly in
        ontology files.

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
            root_class.source_ids.add("PREDEFINED")

    @classmethod
    def _remove_duplicate_parents(cls, voc_builder: VocabularyBuilder):
        """Prevent that a class_ has the same parent iri multiple times

        Args:
            voc_builder: Builder object for Vocabulary
        Returns:
            None
        """
        for class_ in voc_builder.vocabulary.classes.values():
            class_.parent_class_iris = list(dict.fromkeys(class_.parent_class_iris))

    @classmethod
    def _ensure_parent_class(cls, voc_builder: VocabularyBuilder):
        """If a class has a parent class, which was provided by an other
        ontology. And that ontology is not given, it will have no parents.
        In that case give him Thing as direct parent

        Args:
            voc_builder: Builder object for Vocabulary
        Returns:
            None
        """
        for class_ in voc_builder.vocabulary.classes.values():
            # Thing is the root of all
            if not class_.iri == "http://www.w3.org/2002/07/owl#Thing":
                if len(class_.parent_class_iris) == 0:
                    class_.parent_class_iris.append(
                        "http://www.w3.org/2002/07/owl#Thing")

    @classmethod
    def _apply_vocabulary_settings(cls, voc_builder: VocabularyBuilder):
        """
        Make the labels of all entities FIWARE safe, so that they can be used
        as field keys

        Args:
            voc_builder: Builder object for Vocabulary
        Returns:
            None
        """
        vocabulary = voc_builder.vocabulary
        settings = vocabulary.settings

        def to_pascal_case(string: str) -> str:
            return stringcase.pascalcase(string).replace("_", "").\
                replace(" ", "").replace("-", "")

        def to_camel_case(string: str) -> str:
            camel_string = stringcase.camelcase(string)
            return camel_string

        def to_snake_case(string: str) -> str:
            camel_string = to_pascal_case(string)
            return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_string).lower()

        # replace all whitespaces
        for entity in vocabulary.get_all_entities():
            entity.label = entity.label.replace(" ", "_")

        # replace al whitespaces in enum_values
        for datatype in vocabulary.datatypes.values():
            new_enums = []
            for enum in datatype.enum_values:
                new_enums.append(enum.replace(" ", "_"))
            datatype.enum_values = new_enums

        if settings.pascal_case_class_labels:
            for class_ in vocabulary.get_classes():
                class_.label = to_pascal_case(class_.label)

        if settings.pascal_case_individual_labels:
            for individual in vocabulary.individuals.values():
                individual.label = to_pascal_case(individual.label)

        if settings.camel_case_property_labels:
            props = list(vocabulary.data_properties.values())
            props.extend(vocabulary.object_properties.values())
            for prop in props:
                prop.label = to_camel_case(prop.label)

        if settings.camel_case_datatype_labels:
            for datatype in vocabulary.datatypes.values():
                datatype.label = to_camel_case(datatype.label)

        if settings.pascal_case_datatype_enum_labels:
            for datatype in vocabulary.get_enum_dataytypes().values():
                datatype.label = to_pascal_case(datatype.label)

    @classmethod
    def _save_initial_label_summary(cls, vocabulary: Vocabulary):
        """
        Save the label_summary existing after parsing, before the user
        changed labels

        Args:
            vocabulary: vocabulary of which the label summary should be saved

        Returns:
            None
        """
        from filip.semantics.vocabulary_configurator import \
            VocabularyConfigurator
        vocabulary.original_label_summary = \
            VocabularyConfigurator.get_label_conflicts_in_vocabulary(
                vocabulary=vocabulary)

    @classmethod
    def _compute_ancestor_classes(cls, voc_builder: VocabularyBuilder):
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
                    continue

                class_.ancestor_class_iris.append(parent)
                grand_parents = \
                    vocabulary.get_class_by_iri(parent).parent_class_iris

                for grand_parent in grand_parents:
                    if grand_parent not in class_.ancestor_class_iris:
                        # prevent infinite loop if inheritance circle
                        queue.append(grand_parent)

    @classmethod
    def _compute_child_classes(cls, voc_builder: VocabularyBuilder):
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
                    continue

                parent_class = vocabulary.get_class_by_iri(parent)
                parent_class.child_class_iris.append(class_.iri)

    @classmethod
    def _combine_relations(cls, voc_builder: VocabularyBuilder):
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

                # These ids should be derived, so that the same combined
                # relation always ends up with the same id as a class can
                # only have 1 combined relation of a property these ids are
                # unique by keeping the ids always the same, we can store
                # information more efficiently in the database (settings)

                # if a property iri is not known while parsing an ontology
                # (dependency not yet parsed) the relations with that
                # property are going to get ignored, maybe a not should be
                # displayed
                if vocabulary.is_id_of_type(property_iri, IdType.data_property):
                    id = "combined-data-relation|{}|{}".format(class_.iri,
                                                               property_iri)
                    combi = CombinedDataRelation(id=id,
                                                 property_iri=property_iri,
                                                 relation_ids=rel_list,
                                                 class_iri=class_.iri)
                    voc_builder.add_combined_data_relation_for_class(
                        class_iri=class_.iri, cdata=combi)
                elif vocabulary.is_id_of_type(property_iri,
                                              IdType.object_property):
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

    @classmethod
    def _sort_relations(cls, voc_builder: VocabularyBuilder):
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
                cls._sort_list_of_combined_relations(cors, vocabulary)

            cdrs = class_.get_combined_data_relations(vocabulary)
            class_.combined_data_relation_ids = \
                cls._sort_list_of_combined_relations(cdrs, vocabulary)

    @classmethod
    def _sort_list_of_combined_relations(
            cls,
            combined_relations: List[CombinedRelation],
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
            # combine label with iri to prevent an error due to two identical
            # labels
        sorted_property_dic = sorted(property_dic.items())

        sorted_cor_ids = []
        for pair in sorted_property_dic:
            sorted_cor_ids.append(pair[1])
        return sorted_cor_ids

    @classmethod
    def _mirror_object_property_inverses(cls, voc_builder: VocabularyBuilder):
        """
        inverses could only be given for 1 obj_prop of the pair and needs to
        be derived for the other also we could have the inverse inside an other
        import (there for done in postprocessing)

        Args:
            voc_builder: Builder object for Vocabulary

        Returns:
            None
        """
        # the state is not cleared, instead add_inverse_property_iri() makes
        # sure that there will be no duplicates as it is a set
        vocabulary = voc_builder.vocabulary

        for obj_prop_iri in vocabulary.object_properties:
            obj_prop = vocabulary.get_object_property(obj_prop_iri)

            for inverse_iri in obj_prop.inverse_property_iris:
                inverse_prop = vocabulary.get_object_property(inverse_iri)
                inverse_prop.add_inverse_property_iri(obj_prop_iri)

    @classmethod
    def transfer_settings(cls, new_vocabulary: Vocabulary,
                          old_vocabulary: Vocabulary):
        """
        Transfer all the user made settings (labels, ..)
        from an old vocabulary to a new vocabulary

        Args:
            new_vocabulary (Vocabulary): Vocabulary to which the settings should
                be transferred
            old_vocabulary (Vocabulary): Vocabulary of which the settings should
                be transferred

        Returns:
            None
        """

        # label settings
        for entity in old_vocabulary.get_all_entities():
            new_entity = new_vocabulary.get_entity_by_iri(entity.iri)
            if new_entity is not None:
                new_entity.user_set_label = entity.user_set_label

        # device settings
        for iri, data_property in old_vocabulary.data_properties.items():
            if iri in new_vocabulary.data_properties:
                new_data_property = new_vocabulary.data_properties[iri]
                new_data_property.field_type = data_property.field_type

