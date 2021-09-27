import json
from typing import List

from filip.semantics.vocabulary import Vocabulary, Class
from filip.semantics.vocabulary.target_statment import StatementType
from filip.utils.datamodel_generator import create_datamodel


def generate_vocabulary_models(vocabulary: Vocabulary, path: str,
                               filename: str):

    content: str = ""

    # imports
    content += "from pydantic import BaseModel, Field\n"
    content += "from typing import List, Union\n"
    content += "from filip.semantics.semantic_models import SemanticClass, " \
               "SemanticIndividual, Relationship\n"

    content += "\n"
    content += "##CLASSES##"

    classes: List[Class] = vocabulary.get_classes_sorted_by_label()
    class_order:  List[Class] = []
    index: int = 0
    while len(classes) > 0:
        print([c.get_label() for c in class_order])
        print(index)
        print([c.get_label() for c in classes])
        for c in classes:
            for p in c.get_parent_classes(vocabulary):
                print(p.get_label())
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
        parent_classes = "SemanticClass"
        for parent in class_.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        content += f"class {class_.get_label()}({parent_classes}):"

        content += "\n\t"
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

        if len(class_.get_combined_object_relations(vocabulary)) == 0:
            content += "\n\t pass"

    content += "\n\n\n"
    content += "##Individuals##"

    for individual in vocabulary.individuals.values():
        content += "\n\n"
        parent_classes = "SemanticIndividual"

        for parent in individual.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        content += f"class {individual.get_label()}({parent_classes}):"

        # setter prevention
        treated_properties = set()
        for class_ in individual.get_parent_classes(vocabulary):
            for cor in class_.get_combined_object_relations(vocabulary):
                if cor.get_property_label(vocabulary) in treated_properties:
                    continue
                else:
                    treated_properties.add(cor.get_property_label(vocabulary))

                content += "\n\t"
                content += f"@{cor.get_property_label(vocabulary)}.setter"
                content += "\n\t"
                content += f"def {cor.get_property_label(vocabulary)}(self, " \
                           f"value):"
                content += "\n\t\t"
                content += "assert False, 'Individuals have no values'"

        if len(treated_properties) == 0:
            content += "\n\t pass"

    content += "\n\n\n"
    # update forware references
    # for class_ in vocabulary.get_classes_sorted_by_label():
    #     content += "\n"
    #     content += f"{class_.get_label()}.update_forward_refs()"
    #
    # for individual in vocabulary.individuals.values():
    #     content += "\n"
    #     content += f"{individual.get_label()}.update_forward_refs()"


    if not path[:-1] == "/":
        path += "/"
    with open(f"{path}{filename}.py", "w") as text_file:
        text_file.write(content)