import copy
import io
import keyword
import os
from datetime import datetime
from string import ascii_letters, digits
from typing import List, Optional, Dict, Tuple, Set

import requests
import wget
from pydantic import BaseModel

from filip.semantics.ontology_parser.post_processer import \
    post_process_vocabulary, transfer_settings
from filip.semantics.ontology_parser.rdfparser import RdfParser
from filip.semantics.vocabulary import Vocabulary, Source, Entity, \
    RestrictionType, Class, ParsingError
from filip.semantics.vocabulary.data_property import DataFieldType
from filip.semantics.vocabulary.source import DependencyStatement
from filip.semantics.vocabulary.vocabulary import VocabularySettings

label_blacklist = list(keyword.kwlist)
label_blacklist.extend(["__references", "__device_settings"])
label_blacklist.extend(["references", "device_settings", "header",
                        "old_state", ""])
label_blacklist.extend(["id", "type", "class"])
label_blacklist.extend(["str", "int", "float", "complex", "list", "tuple",
                        "range","dict", "list", "set", "frozenset", "bool",
                        "bytes", "bytearray","memoryview"])

label_char_whitelist = ascii_letters + digits + "_"


class LabelSummary(BaseModel):
    class_label_duplicates: Dict[str, List[Entity]]
    field_label_duplicates: Dict[str, List[Entity]]
    datatype_label_duplicates: Dict[str, List[Entity]]

    blacklisted_labels: List[Tuple[str, Entity]]
    labels_with_illegal_chars: List[Tuple[str, Entity]]

    def is_valid(self) -> bool:
        return len(self.class_label_duplicates) == 0 and \
               len(self.field_label_duplicates) == 0 and \
               len(self.datatype_label_duplicates) == 0 and \
               len(self.blacklisted_labels) == 0 and \
               len(self.labels_with_illegal_chars) == 0

    def __str__(self):
        res = ""

        def print_collection(collection):
            sub_res = ""
            for key, values in collection.items():
                sub_res += f"\t{key}: "
                for v in values:
                    sub_res += f" \n\t\t{v.iri}"
                sub_res += "\n"

            if len(collection) == 0:
                sub_res +="\t/\n"
            return sub_res

        def print_list(collection):
            sub_res = ""
            for key, value in collection:
                sub_res += f"\t{key}: \t {value.iri}"
                sub_res += "\n"
            if len(collection) == 0:
                sub_res += "\t/\n"
            return sub_res

        res += "class_label_duplicates:\n"
        res += print_collection(self.class_label_duplicates)
        res += "field_label_duplicates:\n"
        res += print_collection(self.field_label_duplicates)
        res += "datatype_label_duplicates:\n"
        res += print_collection(self.datatype_label_duplicates)
        res += "blacklisted_labels:\n"
        res += print_list(self.blacklisted_labels)
        res += "labels_with_illegal_chars:\n"
        res += print_list(self.labels_with_illegal_chars)
        return res


class VocabularyConfigurator:

    @classmethod
    def create_vocabulary(cls,
                          settings: VocabularySettings = VocabularySettings()) \
            -> Vocabulary:

        return Vocabulary(settings=settings)

    @classmethod
    def delete_source_from_vocabulary(cls, vocabulary: Vocabulary,
                                      source_id: str) -> Vocabulary:
        new_vocabulary = Vocabulary(settings=copy.copy(vocabulary.settings))
        parser = RdfParser()
        found = False
        for source in vocabulary.sources.values():
            if not source_id == source.id:
                parser.parse_source_into_vocabulary(
                    source=copy.deepcopy(source), vocabulary=new_vocabulary)
            else:
                found = True

        post_process_vocabulary(vocabulary=new_vocabulary,
                                old_vocabulary=vocabulary)

        if not found:
            raise ValueError(
                f"Source with source_id {source_id} not in vocabulary")

        transfer_settings(new_vocabulary=new_vocabulary,
                          old_vocabulary=vocabulary)

        return new_vocabulary

    @classmethod
    def add_ontology_to_vocabulary_as_link(
            cls,
            vocabulary: Vocabulary,
            link: str,
            source_name: Optional[str] = None) -> Vocabulary:

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
        source = Source(source_name=source_name,
                        content=source_content,
                        timestamp=datetime.now())

        return VocabularyConfigurator._parse_sources_into_vocabulary(
            vocabulary=vocabulary, sources=[source])

    @classmethod
    def _parse_sources_into_vocabulary(cls, vocabulary: Vocabulary,
                                       sources: List[Source]) -> Vocabulary:

        # create a new vocabulary by reparsing the existing sources
        new_vocabulary = Vocabulary(settings=copy.copy(vocabulary.settings))
        parser = RdfParser()
        for source in vocabulary.sources.values():
            source.clear()
            parser.parse_source_into_vocabulary(source=copy.deepcopy(source),
                                                vocabulary=new_vocabulary)

        # try to parse in the new sources and post_process
        try:
            for source in sources:
                parser.parse_source_into_vocabulary(source=source,
                                                    vocabulary=new_vocabulary)
            post_process_vocabulary(vocabulary=new_vocabulary,
                                    old_vocabulary=vocabulary)
        except Exception as e:
            raise ParsingException(e.args)

        return new_vocabulary

    @classmethod
    def get_label_conflicts_in_vocabulary(cls, vocabulary: Vocabulary) -> \
            LabelSummary:

        def get_conflicts_in_group(entities_to_check: List[Dict]):
            # maps label to _list of entities with that label
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

            # sort duplicate_labels to have alphabetical order in _list
            dup_list = list(duplicate_labels)
            dup_list = sorted(dup_list, key=str.casefold)

            result: Dict[str, List[Entity]] = {}
            # store and log findings
            for label in dup_list:
                result[label] = used_labels[label]

            return result

        def get_blacklisted_labels(entities_to_check: List[Dict]):

            blacklist = label_blacklist

            result: List[Tuple[str, Entity]] = []
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if label in blacklist:
                        result.append((label, entity))

            return result

        def get_illegal_labels(entities_to_check: List[Dict]):

            whitelist = label_char_whitelist

            result: List[Tuple[str, Entity]] = []
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    for c in label:
                        if c not in whitelist:
                            result.append((label, entity))

            return result

        summary = LabelSummary(
            class_label_duplicates=get_conflicts_in_group(
                [vocabulary.classes, vocabulary.individuals]),
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
    def is_vocabulary_valid(cls, vocabulary: Vocabulary):
        return VocabularyConfigurator.get_label_conflicts_in_vocabulary(
            vocabulary).is_valid()

    @classmethod
    def build_class_models(cls, vocabulary: Vocabulary):

        if not VocabularyConfigurator.is_vocabulary_valid(vocabulary):
            raise Exception

        for class_ in vocabulary.classes.values():
            print()
            print(class_.dict())

    @classmethod
    def get_missing_dependency_statements(cls, vocabulary: Vocabulary) -> \
            List[DependencyStatement]:
        missing_dependencies: List[DependencyStatement] = []
        for source in vocabulary.get_source_list():
            for statement in source.dependency_statements:
                if not statement.fulfilled:
                    missing_dependencies.append(statement)
        return missing_dependencies

    @classmethod
    def get_missing_dependencies(cls, vocabulary: Vocabulary) -> List[str]:
        missing_dependencies: Set[str] = set()
        for source in vocabulary.get_source_list():
            for statement in source.dependency_statements:
                if not statement.fulfilled:
                    missing_dependencies.add(statement.dependency_iri)
        return list(missing_dependencies)

    @classmethod
    def get_parsing_logs(cls, vocabulary: Vocabulary) -> List[ParsingError]:
        res = []
        for source in vocabulary.sources.values():
            res.extend(source.get_parsing_log(vocabulary))
        return res

    @classmethod
    def generate_vocabulary_models(cls, vocabulary: Vocabulary, path: str,
                                   filename: str):

        content: str = ""

        # imports
        content += "from typing import Dict, Union, List\n"
        content += "from filip.semantics.semantic_models import \\" \
                   "\n\tSemanticClass, SemanticIndividual, RelationField, " \
                   "DataField, SemanticDeviceClass, DeviceAttributeField," \
                   "CommandField"
        content += "\n"
        content += "from filip.semantics.semantic_manager import " \
                   "SemanticManager, InstanceRegistry"

        content += "\n\n\n"
        content += "semantic_manager: SemanticManager = SemanticManager("
        content += "\n\t"
        content += "instance_registry=InstanceRegistry(),"
        # content += "\n\t"
        # content += "default_header= InstanceHeader(),"
        content += "\n"
        content += ")"

        content += "\n\n"
        content += "# ---------CLASSES--------- #"

        classes: List[Class] = vocabulary.get_classes_sorted_by_label()
        class_order: List[Class] = []
        index: int = 0
        while len(classes) > 0:
            class_ = classes[index]
            parents = class_.get_parent_classes(vocabulary)
            if len([p for p in parents if p in class_order]) == len(
                    parents):
                class_order.append(class_)
                del classes[index]
                index = 0

            else:
                index += 1

        for class_ in class_order:
            relationship_validators_content = ""

            content += "\n\n\n"
            # Parent Classes
            parent_class_string = ""
            parents = class_.get_parent_classes(vocabulary)

            # Device Class, only add if this is a device class and it was not added
            # for a parent
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

            # ------Constructors------
            if class_.get_label() == "Thing":
                content += "\n\n\t"
                content += "def __new__(cls, *args, **kwargs):"
                content += "\n\t\t"
                content += "kwargs['semantic_manager'] = semantic_manager"
                content += "\n\t\t"
                content += "return super().__new__(cls, *args, **kwargs)"

                content += "\n\n\t"
                content += "def __init__(self, *args, **kwargs):"
                content += "\n\t\t"
                content += "kwargs['semantic_manager'] = semantic_manager"
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

            content += "\n"
            for cor in class_.get_combined_object_relations(vocabulary):
                content += "\n\t\t\t"
                content += f"self." \
                           f"{cor.get_property_label(vocabulary)}._rules = " \
                           f"{cor.export_rule(vocabulary, stringify_fields=False)}"

            content += "\n"
            for cr in class_.get_combined_relations(vocabulary):
                content += "\n\t\t\t"
                content += f"self.{cr.get_property_label(vocabulary)}" \
                           f"._instance_identifier = " \
                           f"self.get_identifier()"

            # ------Add preset Values------
            for cdr in class_.get_combined_data_relations(vocabulary):
                # Add fixed values to fields, for CDRs these values need to be
                # strings. Only add the statement on the uppermost occurring class
                if not cdr.is_device_relation(vocabulary):
                    for rel in cdr.get_relations(vocabulary):
                        if rel.id in class_.relation_ids:
                            # only reinitialise the fields if this child class
                            # changed them
                            if rel.restriction_type == RestrictionType.value:
                                content += "\n\t\t\t"
                                content += \
                                    f"self.{cdr.get_property_label(vocabulary)}" \
                                    f".append(" \
                                    f"{rel.target_statement.target_data_value})"

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
                                       f".append({i}())"

            content += "\n\t\t\tpass"

            # if len(class_.get_combined_object_relations(vocabulary)) == 0:
            #     content += "\n\t\tpass"

            content += "\n\n\t"

            # ------Add Data Fields------
            content += "# Data fields"
            for cdr in class_.get_combined_data_relations(vocabulary):
                cdr_type = cdr.get_field_type(vocabulary)
                if cdr_type == DataFieldType.simple:
                    content += "\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: DataField = DataField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += \
                        f"rule='" \
                        f"{cdr.get_all_targetstatements_as_string(vocabulary)}',"
                    content += "\n\t\t"
                    content += "semantic_manager=semantic_manager)"
                elif cdr_type == DataFieldType.command:
                    content += "\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: CommandField = CommandField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += "semantic_manager=semantic_manager)"

                elif cdr_type == DataFieldType.device_attribute:
                    content += "\n\t"
                    label = cdr.get_property_label(vocabulary)
                    content += f"{label}: DeviceAttributeField " \
                               f"= DeviceAttributeField("
                    content += "\n\t\t"
                    content += f"name='{label}',"
                    content += "\n\t\t"
                    content += "semantic_manager=semantic_manager)"

            content += "\n\n\t"

            # ------Add Relation Fields------
            content += "# Relation fields"
            for cor in class_.get_combined_object_relations(vocabulary):
                content += "\n\t"
                label = cor.get_property_label(vocabulary)
                content += f"{label}: RelationField = RelationField("
                content += "\n\t\t"
                content += f"name='{label}',"
                content += "\n\t\t"
                content += f"rule='" \
                           f"{cor.get_all_targetstatements_as_string(vocabulary)}',"
                content += "\n\t\t"
                content += "semantic_manager=semantic_manager)"

            # # ------Add Settings Fields------
            # if class_.is_iot_class(vocabulary):
            #     if True not in [p.is_iot_class(vocabulary) for p in parents]:
            #         content += "\n\n\t"
            #         content += "# Setting fields"
            #
            #
            #         # device transport field
            #         content += "\n\t"
            #         content += "SETTING_transport: SettingsField = SettingsField("
            #         content += "\n\t\t"
            #         content += "name='transport',"
            #         content += "\n\t\t"
            #         content += "type=str,"
            #         content += "\n\t\t"
            #         content += "semantic_manager=semantic_manager)"
            #
            #         # device endpoint field
            #         content += "\n\t"
            #         content += "SETTING_endpoint: SettingsField = SettingsField("
            #         content += "\n\t\t"
            #         content += "name='endpoint',"
            #         content += "\n\t\t"
            #         content += "type=str,"
            #         content += "\n\t\t"
            #         content += "semantic_manager=semantic_manager)"

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

            # content += "\n"
            # variable_name = re.sub(r'(?<!^)(?=[A-Z])', '_', label).lower()
            # content += f"{variable_name} = {label}(id='individual')"

        content += "\n\n\n"

        content += "\n\n\n"
        content += "# ---------Datatypes--------- #"
        content += "\n"

        # Datatypes dict

        # datatype_dict = {}
        # for name, datatype in vocabulary.datatype_catalogue.items():
        #     definition = datatype.export()
        #     datatype_dict[datatype.get_label()] = definition
        #
        # content += json.dumps(datatype_dict, indent=4)
        # content += "\n"

        # Datatypes inline
        content += "semantic_manager.datatype_catalogue = {"
        for name, datatype in vocabulary.datatypes.items():
            definition = datatype.export()
            content += "\n\t"
            content += f"'{datatype.get_label()}': \t {definition},"
        content += "\n"
        content += "}"

        # build class dict
        content += "\n\n"
        content += "semantic_manager.class_catalogue = {"
        for class_ in vocabulary.get_classes_sorted_by_label():
            content += "\n\t"
            content += f"'{class_.get_label()}': {class_.get_label()},"
        content += "\n\t}"
        content += "\n"

        # build individual dict
        content += "\n\n"
        content += "semantic_manager.individual_catalogue = {"
        for individual in vocabulary.individuals.values():
            content += "\n\t"
            content += f"'{individual.get_label()}': {individual.get_label()},"
        content += "\n\t}"
        content += "\n"

        if not path[:-1] == "/":
            path += "/"
        with open(f"{path}{filename}.py", "w") as text_file:
            text_file.write(content)


class ParsingException(Exception):

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.value)