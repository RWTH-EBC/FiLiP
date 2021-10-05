import json
from typing import List

from filip.semantics.vocabulary import Vocabulary, Class
from filip.semantics.vocabulary.target_statment import StatementType
from filip.utils.datamodel_generator import create_datamodel


def generate_vocabulary_models(vocabulary: Vocabulary, path: str,
                               filename: str):

    content: str = ""

    # imports
    content += "from typing import Dict, Union\n"
    content += "from filip.semantics.semantic_models import \\"\
               "\n\tSemanticClass, SemanticIndividual, RelationField, " \
               "DataField, InstanceRegistry"
    content += "\n"
    content += "from filip.semantics.semantic_manager import SemanticManager"

    content += "\n\n\n"
    content += "semantic_manager: SemanticManager = SemanticManager("
    content += "\n\t"
    content += "instance_registry=InstanceRegistry()"
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
        parent_classes = ""
        for parent in class_.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        parent_classes = parent_classes[2:]  # remove first comma and space
        if parent_classes == "":
            parent_classes = "SemanticClass"

        content += f"class {class_.get_label()}({parent_classes}):"

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
            content += "super().__init__(*args, **kwargs)"

        else:
            content += "\n\n\t"
            content += "def __init__(self, *args, **kwargs):"
            content += "\n\t\t"
            content += "super().__init__(*args, **kwargs)"

        content += "\n"
        for cdr in class_.get_combined_data_relations(vocabulary):
            content += "\n\t\t"
            content += f"self." \
                       f"" \
                       f"{cdr.get_property_label(vocabulary)}._rules = " \
                       f"{cdr.export_rule(vocabulary)}"
        content += "\n"
        for cor in class_.get_combined_object_relations(vocabulary):
            content += "\n\t\t"
            content += f"self.{cor.get_property_label(vocabulary)}" \
                       f"._class_identifier = " \
                       f"self.get_identifier()"

        # if len(class_.get_combined_object_relations(vocabulary)) == 0:
        #     content += "\n\t\tpass"

        content += "\n\n\t"

        # Data fields
        content += "# Data fields"
        for cdr in class_.get_combined_data_relations(vocabulary):
            content += "\n\t"
            label = cdr.get_property_label(vocabulary)
            content += f"{label}: DataField = DataField("
            content += "\n\t\t"
            content += f"name='{label}',"
            content += "\n\t\t"
            content += f"rule='" \
                       f"{cdr.get_all_targetstatements_as_string(vocabulary)}')"

        content += "\n\n\t"

        # Relation fields
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

    content += "\n\n\n"
    content += "# ---------Individuals--------- #"

    for individual in vocabulary.individuals.values():
        content += "\n\n"
        parent_classes = "SemanticIndividual"

        for parent in individual.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        content += f"class {individual.get_label()}({parent_classes}):"

        # setter prevention
        properties = []
        for class_ in individual.get_parent_classes(vocabulary):
            for cor in class_.get_combined_object_relations(vocabulary):
                if cor.get_property_label(vocabulary) in properties:
                    continue
                else:
                    properties.append(cor.get_property_label(vocabulary))

        content += "\n\tpass"
        # if len(properties) == 0:
        #     content += "\n\t pass"
        # else:
        #     content += "\n\t"
        #     content += "def __init__(self):"
        #     content += "\n\t\t"
        #     content += "super().__init__()"
        #     for label in properties:
        #         content += "\n\t\t"
        #         content += f"self.{label} = None"

            # content += "\n"
            # for label in properties:
            #     content += "\n\t"
            #     content += f"@{label}.setter"
            #     content += "\n\t"
            #     content += f"def {label}(self, " \
            #                f"value):"
            #     content += "\n\t\t"
            #     content += "assert False, 'Individuals have no values'"

    content += "\n\n\n"

    content += "\n\n\n"
    content += "# ---------Datatypes--------- #"
    content += "\n"

    content += "datatypes = {"

    for name, datatype in vocabulary.datatypes.items():
        definition = datatype.export()

        content += "\n\t"
        content += f"'{datatype.get_label()}': \t {definition},"
    content += "\n"
    content += "}"

    # build model dict
    content += "\n\n"
    content += "semantic_manager.model_catalogue = {"
    for class_ in vocabulary.get_classes_sorted_by_label():
        content += "\n\t"
        content += f"'{class_.get_label()}': {class_.get_label()},"

    for individual in vocabulary.individuals.values():
        content += "\n\t"
        content += f"'{individual.get_label()}': {individual.get_label()},"
    content += "\n\t}"
    content += "\n"



    if not path[:-1] == "/":
        path += "/"
    with open(f"{path}{filename}.py", "w") as text_file:
        text_file.write(content)