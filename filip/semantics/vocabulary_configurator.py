"""Module providing an interface to manipulate the sources of a vocabulary,
and to ability to export it to models"""

import copy
import io
import keyword
import os
from datetime import datetime
from string import ascii_letters, digits
from typing import List, Optional, Dict, Tuple, Set

import pathlib
import requests
import wget

from filip.semantics.ontology_parser.post_processer import PostProcessor
from filip.semantics.ontology_parser.rdfparser import RdfParser
from filip.semantics.vocabulary import \
    LabelSummary, \
    Vocabulary, \
    Source, \
    Entity, \
    RestrictionType, \
    Class, \
    ParsingError, \
    CombinedRelation, \
    DataFieldType, \
    DependencyStatement, \
    VocabularySettings

# Blacklist containing all labels that are forbidden for entities to have
label_blacklist = list(keyword.kwlist)
label_blacklist.extend(["referencedBy", "deviceSettings"])
label_blacklist.extend(["references", "device_settings", "header",
                        "old_state", "", "semantic_manager", "delete",
                        "metadata"])
label_blacklist.extend(["id", "type", "class"])
label_blacklist.extend(["str", "int", "float", "complex", "list", "tuple",
                        "range", "dict", "list", "set", "frozenset", "bool",
                        "bytes", "bytearray", "memoryview"])

# Whitelist containing all chars that an entity label can consist of
label_char_whitelist = ascii_letters + digits + "_"


class VocabularyConfigurator:
    """
    Class that provides static interfaces to manipulate the sources of a
    vocabulary, validate and save it.
    """

    @classmethod
    def create_vocabulary(cls,
                          settings: VocabularySettings = VocabularySettings()) \
            -> Vocabulary:
        """
        Create a new blank vocabulary with given settings

        Args:
            settings: VocabularySettings

        Returns:
            Vocabulary
        """

        return Vocabulary(settings=settings)

    @classmethod
    def delete_source_from_vocabulary(cls, vocabulary: Vocabulary,
                                      source_id: str) -> Vocabulary:
        """
        Delete a source from the vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary from which the source should
            be removed
            source_id (str): Id of source to remove

        Raises:
            ValueError:  If no source with given Id exists in Vocabulary

        Returns:
            New Vocabulary without the given source
        """
        new_vocabulary = Vocabulary(settings=copy.copy(vocabulary.settings))
        parser = RdfParser()
        found = False
        for source in vocabulary.sources.values():
            if not source_id == source.id:
                parser.parse_source_into_vocabulary(
                    source=copy.deepcopy(source), vocabulary=new_vocabulary)
            else:
                found = True

        PostProcessor.post_process_vocabulary(
            vocabulary=new_vocabulary, old_vocabulary=vocabulary)

        if not found:
            raise ValueError(
                f"Source with source_id {source_id} not in vocabulary")

        PostProcessor.transfer_settings(
            new_vocabulary=new_vocabulary, old_vocabulary=vocabulary)

        return new_vocabulary

    @classmethod
    def add_ontology_to_vocabulary_as_link(
            cls,
            vocabulary: Vocabulary,
            link: str,
            source_name: Optional[str] = None) -> Vocabulary:
        """
        Add a source to the vocabulary with via a weblink. Source name will
        be extracted from link, if no name is given

        Args:
            vocabulary (Vocabulary): Vocabulary to which the source should
            be added
            link (str): Weblink to the source
            source_name (Optional[str]): Name for the source

        Raises:
            ParsingException:  If the given source was not valid and could not
            be parsed

        Returns:
            New Vocabulary with the given source added to it
        """

        downloaded_obj = requests.get(link)
        file_bytes = io.BytesIO(downloaded_obj.content)
        if source_name is None:
            source_name = wget.filename_from_url(link)

        file_str = io.TextIOWrapper(file_bytes, encoding='utf-8').read()

        return cls.add_ontology_to_vocabulary_as_string(vocabulary=vocabulary,
                                                        source_name=source_name,
                                                        source_content=file_str)

    @classmethod
    def add_ontology_to_vocabulary_as_file(
            cls,
            vocabulary: Vocabulary,
            path_to_file: str,
            source_name: Optional[str] = None) -> Vocabulary:
        """
        Add a source to the vocabulary with via a file path. Source name will
        be extracted from path, if no name is given

        Args:
            vocabulary (Vocabulary): Vocabulary to which the source should
            be added
            path_to_file (str): Path to the source file
            source_name (Optional[str]): Name for the source

        Raises:
            ParsingException:  If the given source was not valid and could not
            be parsed

        Returns:
            New Vocabulary with the given source added to it
        """

        with open(path_to_file, 'r') as file:
            data = file.read()

        if source_name is None:
            source_name = os.path.basename(path_to_file).split(".")[0]

        source = Source(source_name=source_name,
                        content=data,
                        timestamp=datetime.now())

        return VocabularyConfigurator._parse_sources_into_vocabulary(
            vocabulary=vocabulary, sources=[source])

    @classmethod
    def add_ontology_to_vocabulary_as_string(cls, vocabulary: Vocabulary,
                                             source_name: str,
                                             source_content: str) -> Vocabulary:
        """
        Add a source to the vocabulary by giving the source content as string.
        Source name needs to be given

        Args:
            vocabulary (Vocabulary): Vocabulary to which the source should
            be added
            source_content (str): Content of source
            source_name (str): Name for the source

        Raises:
            ParsingException:  If the given source was not valid and could not
            be parsed

        Returns:
            New Vocabulary with the given source added to it
        """
        source = Source(source_name=source_name,
                        content=source_content,
                        timestamp=datetime.now())

        return VocabularyConfigurator._parse_sources_into_vocabulary(
            vocabulary=vocabulary, sources=[source])

    @classmethod
    def _parse_sources_into_vocabulary(cls, vocabulary: Vocabulary,
                                       sources: List[Source]) -> Vocabulary:
        """
        Parse the given source objects into the vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary to which the source should
            be added
            sources (List[Source]): Source objects to be added

        Raises:
            ParsingException:  If the given source was not valid and could not
            be parsed

        Returns:
            New Vocabulary with the given sources added to it
        """

        # create a new vocabulary by reparsing the existing sources
        new_vocabulary = Vocabulary(settings=copy.copy(vocabulary.settings))
        parser = RdfParser()
        for source in vocabulary.sources.values():
            source_copy = copy.deepcopy(source)
            source_copy.clear()
            parser.parse_source_into_vocabulary(source=source_copy,
                                                vocabulary=new_vocabulary)

        # try to parse in the new sources and post_process
        try:
            for source in sources:
                parser.parse_source_into_vocabulary(source=source,
                                                    vocabulary=new_vocabulary)
            PostProcessor.post_process_vocabulary(
                vocabulary=new_vocabulary, old_vocabulary=vocabulary)
        except Exception as e:
            raise ParsingException(e.args)

        return new_vocabulary

    @classmethod
    def is_label_blacklisted(cls, label: str) -> bool:
        """Checks if the given label is forbidden for an entity to possess

        Args:
            label (str): label to check

        Returns:
            bool
        """
        return label in label_blacklist

    @classmethod
    def is_label_illegal(cls, label: str) -> bool:
        """Checks if the given label contains a forbidden char

        Args:
            label (str): label to check

        Returns:
            bool, True if label forbidden
        """
        for c in label:
            if c not in label_char_whitelist:
                return True
        return False

    @classmethod
    def get_label_conflicts_in_vocabulary(cls, vocabulary: Vocabulary) -> \
            LabelSummary:
        """
        Compute a summary for all labels present in the vocabulary.
        The summary contains all naming clashes and illegal labels.

        Args:
            vocabulary (Vocabulary): Vocabulary to analyse

        Returns:
            LabelSummary
        """

        def get_conflicts_in_group(entities_to_check: List[Dict]):
            # maps label to list of entities with that label
            used_labels: Dict[str, List[Entity]] = {}
            duplicate_labels = set()

            # process entities to find conflicts
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if label in used_labels:
                        duplicate_labels.add(label)
                        used_labels[label].append(entity)
                    else:
                        used_labels[label] = [entity]

            # sort duplicate_labels to have alphabetical order in list
            dup_list = list(duplicate_labels)
            dup_list = sorted(dup_list, key=str.casefold)

            result: Dict[str, List[Entity]] = {}
            # store and log findings
            for label in dup_list:
                result[label] = used_labels[label]

            return result

        def get_blacklisted_labels(entities_to_check: List[Dict]):
            result: List[Tuple[str, Entity]] = []
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if cls.is_label_blacklisted(label):
                        result.append((label, entity))

            return result

        def get_illegal_labels(entities_to_check: List[Dict]):
            result: List[Tuple[str, Entity]] = []
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if cls.is_label_illegal(label):
                        result.append((label, entity))

            return result

        summary = LabelSummary(
            class_label_duplicates=get_conflicts_in_group(
                [vocabulary.classes, vocabulary.individuals,
                 vocabulary.get_enum_dataytypes()]),
            field_label_duplicates=get_conflicts_in_group(
                [vocabulary.data_properties, vocabulary.object_properties]),
            datatype_label_duplicates=get_conflicts_in_group(
                [vocabulary.datatypes]),
            blacklisted_labels=get_blacklisted_labels([
                vocabulary.classes, vocabulary.individuals,
                vocabulary.data_properties, vocabulary.object_properties
            ]),
            labels_with_illegal_chars=get_illegal_labels([
                vocabulary.classes, vocabulary.individuals,
                vocabulary.data_properties, vocabulary.object_properties,
                vocabulary.datatypes
            ]),
        )

        return summary

    @classmethod
    def is_vocabulary_valid(cls, vocabulary: Vocabulary) -> bool:
        """
        Test if the given vocabulary is valid -> all labels are unique and
        correct

        Args:
            vocabulary (Vocabulary): Vocabulary to analyse

        Returns:
            bool
        """
        return VocabularyConfigurator.get_label_conflicts_in_vocabulary(
            vocabulary).is_valid()

    @classmethod
    def get_missing_dependency_statements(cls, vocabulary: Vocabulary) -> \
            List[DependencyStatement]:
        """
        Get a list of all Dependencies that are currently missing in the
        vocabulary in form of DependencyStatements

        Args:
            vocabulary (Vocabulary): Vocabulary to analyse

        Returns:
            List[DependencyStatement]
        """
        missing_dependencies: List[DependencyStatement] = []
        for source in vocabulary.get_source_list():
            for statement in source.dependency_statements:
                if not statement.fulfilled:
                    missing_dependencies.append(statement)
        return missing_dependencies

    @classmethod
    def get_missing_dependencies(cls, vocabulary: Vocabulary) -> List[str]:
        """
        Get a list of all Dependencies that are currently missing in the
        vocabulary in form of iris

        Args:
            vocabulary (Vocabulary): Vocabulary to analyse

        Returns:
            List[str]: List of missing iris
        """

        missing_dependencies: Set[str] = set()
        for source in vocabulary.get_source_list():
            for statement in source.dependency_statements:
                if not statement.fulfilled:
                    missing_dependencies.add(statement.dependency_iri)
        return list(missing_dependencies)

    @classmethod
    def get_parsing_logs(cls, vocabulary: Vocabulary) -> List[ParsingError]:
        """
        Get the parsing logs of a vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary to analyse

        Returns:
            List[ParsingError]
        """
        res = []
        for source in vocabulary.sources.values():
            res.extend(source.get_parsing_log(vocabulary))
        return res

    @classmethod
    def generate_vocabulary_models(
            cls,
            vocabulary: Vocabulary,
            path: Optional[str] = None,
            filename: Optional[str] = None,
            alternative_manager_name: Optional[str] = None) ->  \
            Optional[str]:
        """
        Export the given vocabulary as python model file.
        All vocabulary classes will be converted to python classes,
        with their CRs as property fields.
        If path and filename are given, the generated file will be saved,
        else the file content is returned as string.

        Args:
            vocabulary (Vocabulary): Vocabulary to export
            path (Optional[str]): Path where the file should be saved
            filename (Optional[str]): Name of the file
            alternative_manager_name (Optional[str]): alternative name for
                the semantic_manager. The manager of the model can than also
                be referenced over the object with this name

        Raises:
            Exception: if file can not be saved as specified with path and
                       filename
            Exception: if vocabulary has label conflicts and is thus not valid

        Returns:
            Optional[str], generated content if path or filename not given
        """

        if not cls.is_vocabulary_valid(vocabulary):
            raise Exception(
                "Vocabulary was not valid. Label conflicts "
                "prevented the generation of models. Check for conflicts with: "
                "VocabularyConfigurator."
                "get_label_conflicts_in_vocabulary(vocabulary)"
                )

        def split_string_into_lines(string: str, limit: int) -> [str]:
            """Helper methode, takes a long string and splits it into
            multiple parts that each represent one line

            Args:
                string: value to split
                limit: line limit
            Returns:
                [str], string separated into lines
            """
            last_space_index = 0
            last_split_index = 0
            current_index = 0
            result = []

            for char in string:
                if char == " ":
                    last_space_index = current_index
                if current_index-last_split_index > limit:
                    result.append(string[last_split_index: last_space_index])
                    last_split_index = last_space_index+1
                current_index += 1

            # add the remaining part, if the last character of the string was
            # not a space at the perfect position
            if not last_split_index == len(string):
                result.append(string[last_split_index:current_index])
            return result

        content: str = '"""\nAutogenerated Models for the vocabulary ' \
                       'described ' \
                       'by the ontologies:\n'
        for source in vocabulary.sources.values():
            if not source.predefined:
                content += f'\t{source.ontology_iri} ({source.source_name})\n'
        content += '"""\n\n'

        # imports
        content += "from enum import Enum\n"
        content += "from typing import Dict, Union, List\n"
        content += "from filip.semantics.semantics_models import\\" \
                   "\n\tSemanticClass,\\" \
                   "\n\tSemanticIndividual,\\" \
                   "\n\tRelationField,\\" \
                   "\n\tDataField,\\" \
                   "\n\tSemanticDeviceClass,\\" \
                   "\n\tDeviceAttributeField,\\" \
                   "\n\tCommandField"
        content += "\n"
        content += "from filip.semantics.semantics_manager import\\" \
                   "\n\tSemanticsManager,\\" \
                   "\n\tInstanceRegistry"

        content += "\n\n\n"
        content += f"semantic_manager: SemanticsManager = SemanticsManager("
        content += "\n\t"
        content += "instance_registry=InstanceRegistry(),"
        content += "\n"
        content += ")"
        content += "\n\n"
        if alternative_manager_name is not None:
            content += f"{alternative_manager_name}: SemanticsManager"
            content += f"= semantic_manager"
            content += "\n\n"
        content += "# ---------CLASSES--------- #"

        # the classes need to be added in order, so that the parents are
        # defined, the moment the children are added
        classes: List[Class] = vocabulary.get_classes_sorted_by_label()
        class_order: List[Class] = []
        children: Dict[str, Set] = {}
        added_class_iris = set()

        # set up data for computation of order
        iri_queue = ["http://www.w3.org/2002/07/owl#Thing"]
        for class_ in classes:
            if class_.iri not in children:
                children[class_.iri] = set()

                if class_.label == "Currency":
                    print(class_.get_parent_classes(vocabulary))

            for parent in class_.get_parent_classes(vocabulary):
                if parent.iri not in children:
                    children[parent.iri] = set()
                children[parent.iri].add(class_.iri)

        # compute class order, in the queue are always the classes, that have
        # all parents already defined (starting with Thing).
        # It is added from the queue and all children who are now fully
        # defined are added to the queue
        while len(iri_queue) > 0:
            # remove from queue
            parent_iri = iri_queue[0]
            del iri_queue[0]

            # add to class_order
            parent = vocabulary.classes[parent_iri]
            class_order.append(parent)
            added_class_iris.add(parent_iri)

            # check children
            child_iris = children[parent_iri]
            for child_iri in child_iris:
                child = vocabulary.classes[child_iri]

                # all parents added, add child to queue
                if len([p for p in child.parent_class_iris
                        if p in added_class_iris]) == len(
                        child.parent_class_iris):

                    if not child_iri in added_class_iris:
                        iri_queue.append(child_iri)

        for class_ in class_order:

            content += "\n\n\n"
            # Parent Classes
            parent_class_string = ""
            parents = class_.get_parent_classes(vocabulary,
                                                remove_redundancy=True)

            # Device Class, only add if this is a device class and it was not
            # added for a parent
            if class_.is_iot_class(vocabulary):
                if True not in [p.is_iot_class(vocabulary) for p in
                                parents]:
                    parent_class_string = " ,SemanticDeviceClass"

            for parent in parents:
                parent_class_string += f", {parent.get_label()}"

            parent_class_string = parent_class_string[
                                  2:]  # remove first comma and space
            if parent_class_string == "":
                parent_class_string = "SemanticClass"

            content += f"class {class_.get_label()}({parent_class_string}):"

            # add class docstring
            content += f'\n\t"""'
            for line in split_string_into_lines(class_.comment, 75):
                content += f"\n\t{line}"
            if class_.comment == "":
                content += "\n\tGenerated SemanticClass without description"
            content += f"\n\n\t"
            content += f"Source(s): \n\t\t"

            for source_id in class_.source_ids:
                content += f"{vocabulary.sources[source_id].ontology_iri} " \
                           f"({vocabulary.sources[source_id].source_name})"
            content += f'\n\t"""'

            # ------Constructors------
            if class_.get_label() == "Thing":
                content += "\n\n\t"
                content += "def __new__(cls, *args, **kwargs):"
                content += "\n\t\t"
                content += f"kwargs['semantic_manager'] = semantic_manager"
                content += "\n\t\t"
                content += "return super().__new__(cls, *args, **kwargs)"

                content += "\n\n\t"
                content += "def __init__(self, *args, **kwargs):"
                content += "\n\t\t"
                content += f"kwargs['semantic_manager'] = semantic_manager"
                content += "\n\t\t"
                content += "is_initialised = 'id' in self.__dict__"
                content += "\n\t\t"
                content += "super().__init__(*args, **kwargs)"

            else:
                content += "\n\n\t"
                content += "def __init__(self, *args, **kwargs):"
                content += "\n\t\t"
                content += "is_initialised = 'id' in self.__dict__"
                content += "\n\t\t"
                content += "super().__init__(*args, **kwargs)"

            # ------Init Fields------
            content += "\n\t\t"
            content += "if not is_initialised:"
            # Only initialise values once
            for cdr in class_.get_combined_data_relations(vocabulary):
                if not cdr.is_device_relation(vocabulary):
                    content += "\n\t\t\t"
                    content += \
                        f"self." \
                        f"{cdr.get_property_label(vocabulary)}._rules = " \
                        f"{cdr.export_rule(vocabulary, stringify_fields=True)}"

            if len(class_.get_combined_object_relations(vocabulary)) > 0:
                content += "\n"
            for cor in class_.get_combined_object_relations(vocabulary):
                content += "\n\t\t\t"
                content += f"self." \
                           f"{cor.get_property_label(vocabulary)}._rules = " \
                           f"{cor.export_rule(vocabulary, stringify_fields=False)}"

            if len(class_.get_combined_relations(vocabulary)) > 0:
                content += "\n"
            for cr in class_.get_combined_relations(vocabulary):
                content += "\n\t\t\t"
                content += f"self.{cr.get_property_label(vocabulary)}" \
                           f"._instance_identifier = " \
                           f"self.get_identifier()"

            # ------Add preset Values------
            for cdr in class_.get_combined_data_relations(vocabulary):
                # Add fixed values to fields, for CDRs these values need to be
                # strings. Only add the statement on the uppermost occurring
                # class
                if not cdr.is_device_relation(vocabulary):
                    for rel in cdr.get_relations(vocabulary):
                        if rel.id in class_.relation_ids:
                            # only reinitialise the fields if this child class
                            # changed them
                            if rel.restriction_type == RestrictionType.value:
                                content += "\n\t\t\t"
                                content += \
                                    f"self." \
                                    f"{cdr.get_property_label(vocabulary)}" \
                                    f".add(" \
                                    f"'{rel.target_statement.target_data_value}')"

            if len(class_.get_combined_object_relations(vocabulary)) > 0:
                content += "\n"
            for cor in class_.get_combined_object_relations(vocabulary):
                # Add fixed values to fields, for CORs these values need to be
                # Individuals.
                # Only add the statement on the uppermost occurring class
                for rel in cor.get_relations(vocabulary):
                    if rel.id in class_.relation_ids:
                        i = vocabulary. \
                            get_label_for_entity_iri(
                            rel.get_targets()[0][0])
                        if rel.restriction_type == RestrictionType.value:
                            content += "\n\t\t\t"
                            content += f"self." \
                                       f"{cor.get_property_label(vocabulary)}" \
                                       f".add({i}())"

            # if no content was added af the not initialised if, removed it
            # again, and its preceding \n
            if content[-22:] == "if not is_initialised:":
                content = content[:-25]

            # make space the same for each case above
            if "\n" in content[-2:]:
                content = content[:-1]

            def build_field_comment(cr: CombinedRelation) -> str:
                comment = vocabulary.get_entity_by_iri(cr.property_iri).comment
                res = ""
                if comment != "":
                    res += f'\n\t"""'
                    for line in split_string_into_lines(comment, 75):
                        res += f'\n\t{line}'
                    res += f'\n\t"""'
                return res

            # ------Add Data Fields------
            if len(class_.get_combined_data_relations(vocabulary)) > 0:
                content += "\n\n\t"
                content += "# Data fields"
            for cdr in class_.get_combined_data_relations(vocabulary):
                cdr_type = cdr.get_field_type(vocabulary)
                if cdr_type == DataFieldType.simple:
                    content += "\n\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: DataField = DataField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += \
                        f"rule='" \
                        f"{cdr.get_all_targetstatements_as_string(vocabulary)}',"
                    content += "\n\t\t"
                    content += f"semantic_manager=semantic_manager)"
                    content += build_field_comment(cdr)

                elif cdr_type == DataFieldType.command:
                    content += "\n\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: CommandField = CommandField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += f"semantic_manager=semantic_manager)"
                    content += build_field_comment(cdr)

                elif cdr_type == DataFieldType.device_attribute:
                    content += "\n\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: DeviceAttributeField " \
                               f"= DeviceAttributeField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += f"semantic_manager=semantic_manager)"
                    content += build_field_comment(cdr)

            # ------Add Relation Fields------
            if len(class_.get_combined_object_relations(vocabulary)) > 0:
                content += "\n\n\t"
                content += "# Relation fields"
            for cor in class_.get_combined_object_relations(vocabulary):
                content += "\n\n\t"
                label = cor.get_property_label(vocabulary)
                content += f"{label}: RelationField = RelationField("
                content += "\n\t\t"
                content += f"name='{label}',"
                content += "\n\t\t"
                content += f"rule='" \
                           f"{cor.get_all_targetstatements_as_string(vocabulary)}',"
                content += "\n\t\t"
                if not len(cor.get_inverse_of_labels(vocabulary)) == 0:
                    content += "inverse_of="
                    content += str(cor.get_inverse_of_labels(vocabulary))
                    content += ",\n\t\t"

                content += f"semantic_manager=semantic_manager)"
                content += build_field_comment(cor)

        content += "\n\n\n"
        content += "# ---------Individuals--------- #"

        for individual in vocabulary.individuals.values():
            content += "\n\n\n"

            parent_class_string = ""
            for parent in individual.get_parent_classes(vocabulary):
                parent_class_string += f", {parent.get_label()}"
            parent_class_string = parent_class_string[2:]

            content += f"class {individual.get_label()}(SemanticIndividual):"
            content += "\n\t"
            content += f"_parent_classes: List[type] = [{parent_class_string}]"

        content += "\n\n\n"

        content += "# ---------Datatypes--------- #"
        content += "\n"

        # Datatypes catalogue
        content += f"semantic_manager.datatype_catalogue = "
        content += "{"
        for name, datatype in vocabulary.datatypes.items():
            definition = datatype.export()
            content += "\n\t"
            # content += f"'{datatype.get_label()}': \t {definition},"
            content += f"'{datatype.get_label()}': "
            content += "{\n"
            for key, value in definition.items():
                string_value = f"'{value}'" if type(value) == str else value
                content += f"\t\t'{key}': {string_value},\n"
            content += "\t},"

        content += "\n"
        content += "}"

        # Build datatypes with enums as Enums
        content += "\n\n\n"
        for datatype in vocabulary.get_enum_dataytypes().values():
            content += f"class {datatype.get_label()}(str, Enum):"
            for value in datatype.enum_values:
                content += f"\n\tvalue_{value} = '{value}'"
            content += "\n\n\n"

        content += "# ---------Class Dict--------- #"

        # build class dict
        content += "\n\n"
        content += f"semantic_manager.class_catalogue = "
        content += "{"
        for class_ in vocabulary.get_classes_sorted_by_label():
            content += "\n\t"
            content += f"'{class_.get_label()}': {class_.get_label()},"
        content += "\n\t}"
        content += "\n"

        # build individual dict
        content += "\n\n"
        content += f"semantic_manager.individual_catalogue = "
        content += "{"
        for individual in vocabulary.individuals.values():
            content += "\n\t"
            content += f"'{individual.get_label()}': {individual.get_label()},"
        content += "\n\t}"
        content += "\n"

        if path is None or filename is None:
            return content
        else:
            path = pathlib.Path(path).joinpath(filename).with_suffix(".py")

            with open(path, "w", encoding ="utf-8") as text_file:
                text_file.write(content)


class ParsingException(Exception):
    """Error Class that is raised if parsing of an ontology was unsuccessful"""

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.value)
