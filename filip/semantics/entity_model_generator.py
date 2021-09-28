import json
from typing import List

from filip.semantics.vocabulary import Vocabulary, Class
from filip.semantics.vocabulary.target_statment import StatementType
from filip.utils.datamodel_generator import create_datamodel


def generate_vocabulary_models(vocabulary: Vocabulary, path: str,
                               filename: str):

    content: str = ""

    # imports
    content += "import inspect, sys\n"
    content += "from pydantic import BaseModel, Field\n"
    content += "from typing import List, Union, Dict\n"
    content += "from filip.semantics.semantic_models import SemanticClass, " \
               "SemanticIndividual, Relationship\n"

    content += "\n"
    content += "##CLASSES##"

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

        content += "\n\n"
        # Parent Classes
        parent_classes = ""
        for parent in class_.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        parent_classes = parent_classes[2:]  # remove first comma and space
        if parent_classes == "":
            parent_classes = "SemanticClass"

        content += f"class {class_.get_label()}({parent_classes}):"

        content += "\n\n\t"
        content += "def __init__(self):"
        content += "\n\t\t"
        content += "super().__init__()"
        for cor in class_.get_combined_object_relations(vocabulary):
            content += "\n\t\t"
            content += f"self.{cor.get_property_label(vocabulary)}._models = " \
                       "models"

        if len(class_.get_combined_object_relations(vocabulary)) == 0:
            content += "\n\t\tpass"

        content += "\n\n\t"
        # Relation fields
        content += "#Relation fields"
        for cor in class_.get_combined_object_relations(vocabulary):
            content += "\n\n\t"

            # target_names = cor.get_all_target_labels(vocabulary)
            # if len(target_names)>1:
            #     types = f'Union{[n for n in target_names]}'.replace("'","")
            # else:
            #     types = target_names.pop()

            label = cor.get_property_label(vocabulary)
            # field
            content += f"{label}: Relationship = Relationship("
            content += "\n\t\t"
            content += f"rule='{cor.get_all_targetstatements_as_string(vocabulary)}',"
            content += "\n\t\t"
            content += f"_rules={cor.export_rule(vocabulary)},"
            content += "\n\t)"

        # if len(class_.get_combined_object_relations(vocabulary)) == 0:
        #     content += "\n\t pass"

    content += "\n\n\n"
    content += "##Individuals##"

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
    # update forware references
    # for class_ in vocabulary.get_classes_sorted_by_label():
    #     content += "\n"
    #     content += f"{class_.get_label()}.update_forward_refs()"
    #
    # for individual in vocabulary.individuals.values():
    #     content += "\n"
    #     content += f"{individual.get_label()}.update_forward_refs()"

    # build model dict
    content += "models: Dict[str, type] = {"
    for class_ in vocabulary.get_classes_sorted_by_label():
        content += "\n\t"
        content += f"'{class_.get_label()}': {class_.get_label()},"

    for individual in vocabulary.individuals.values():
        content += "\n\t"
        content += f"'{individual.get_label()}': {individual.get_label()},"
    content += "\n}"

    if not path[:-1] == "/":
        path += "/"
    with open(f"{path}{filename}.py", "w") as text_file:
        text_file.write(content)