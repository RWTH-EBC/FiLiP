import json
import re
from typing import List

from filip.semantics.vocabulary import Vocabulary, Class, RestrictionType
from filip.semantics.vocabulary.data_property import DataFieldType
from filip.semantics.vocabulary.target_statment import StatementType
from filip.utils.datamodel_generator import create_datamodel


def generate_vocabulary_models(vocabulary: Vocabulary, path: str,
                               filename: str):

    content: str = ""

    # imports
    content += "from typing import Dict, Union, List\n"
    content += "from filip.semantics.semantic_models import \\"\
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
    class_order:  List[Class] = []
    index: int = 0
    while len(classes) > 0:
        class_ = classes[index]
        parents = class_.get_parent_classes(vocabulary)
        if len([p for p in parents if p in class_order]) == len(parents):
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
            if True not in [p.is_iot_class(vocabulary) for p in parents] :
                parent_class_string = " ,SemanticDeviceClass"

        for parent in parents:
            parent_class_string += f", {parent.get_label()}"

        parent_class_string = parent_class_string[2:]  # remove first comma and space
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
                    i = vocabulary.\
                        get_label_for_entity_iri(rel.get_targets()[0][0])
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
            elif cdr_type  == DataFieldType.command:
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