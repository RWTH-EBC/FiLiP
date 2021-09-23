import json

from filip.semantics.vocabulary import Vocabulary, Class
from filip.semantics.vocabulary.target_statment import StatementType
from filip.utils.datamodel_generator import  create_datamodel

# https://pydantic-docs.helpmanual.io/datamodel_code_generator/
# https://koxudaxi.github.io/datamodel-code-generator/

def generate_model_for_class(vocabulary: Vocabulary, class_: Class):

    # Build dictionary
    json_dic = {}

    json_dic['title'] = class_.get_label()
    json_dic['type'] = "object"

    properties_dic = {}
    json_dic['properties'] = properties_dic
    for cor in class_.get_combined_object_relations(vocabulary=vocabulary):
        cor_dict = {}

        # set the description equal to the target information string
        # ex: some Light, min 1 LED
        relations = cor.get_relations(vocabulary=vocabulary)
        cor_dict['description'] = \
            cor.get_all_targetstatements_as_string(vocabulary=vocabulary)

        # Fill in  allowed classes for field
        if len(relations) == 1:
            cor_dict['type'] ='string'
                # relations[0].get_all_possible_target_class_labels(vocabulary)[0]
        else:
            types = [r.get_all_possible_target_class_labels(vocabulary)
                     for r in relations]
            cor_dict['type'] = f"Union{types}"

        cor_dict['default'] = 'def'

        properties_dic[cor.get_property_label(vocabulary)] = cor_dict

    print(json.dumps(obj=json_dic, indent=2))
    create_datamodel(output_path="D:/",
                     filename=f"{class_.get_label()}.py",
                     schema=json.dumps(obj=json_dic, indent=2))

def generate_model(vocabulary: Vocabulary):

    # Build dictionary
    vocabulary_list = []

    for class_ in vocabulary.get_classes():
        class_dic = {}
        class_dic['title'] = class_.get_label()
        class_dic['type'] = "object"

        properties_dic = {}
        class_dic['properties'] = properties_dic
        for cor in class_.get_combined_object_relations(vocabulary=vocabulary):
            cor_dict = {}

            # set the description equal to the target information string
            # ex: some Light, min 1 LED
            relations = cor.get_relations(vocabulary=vocabulary)
            cor_dict['description'] = \
                cor.get_all_targetstatements_as_string(vocabulary=vocabulary)

            # Fill in  allowed classes for field
            if len(relations) == 1:
                cor_dict['type'] = \
                    relations[0].get_all_possible_target_class_labels(vocabulary)[0]
            else:
                types = [r.get_all_possible_target_class_labels(vocabulary)
                         for r in relations]
                cor_dict['type'] = f"Union{types}"

            properties_dic[cor.get_property_label(vocabulary)] = cor_dict


        vocabulary_list.append(class_dic)

    dic_obj = {}
    print(json.dumps(obj=vocabulary_list, indent=2))

    create_datamodel(output_path="D:/",
                     filename=f"test.py",
                     schema=json.dumps(obj=vocabulary_list, indent=2))


def generate_vocabulary_models(vocabulary: Vocabulary):

    content: str = ""

    # imports
    content += "from pydantic import BaseModel, Field"

    #classes
    for class_ in vocabulary.get_classes_sorted_by_label():
        content += "\n\n"
        # Parent Classes
        parent_classes = "BaseModel"
        for parent in class_.get_parent_classes(vocabulary):
            parent_classes += f", {parent.get_label()}"

        content += f"class {class_.get_label()}({parent_classes}):"

        content += "\n\t"
        # Relation fields
        content += "#Relation fields"
        for cor in class_.get_combined_object_relations(vocabulary):
            content += "\n\t"

            # target_names = cor.get_all_target_labels(vocabulary)
            # if len(target_names)>1:
            #     types = f'Union{[n for n in target_names]}'.replace("'","")
            # else:
            #     types = target_names.pop()




            content += f"{cor.get_property_label(vocabulary)}: List[{types}] = Field("
            content += "\n\t\t"
            content += f"description = '{cor.get_all_targetstatements_as_string(vocabulary)}',"
            content += "\n\t\t"
            content += f"default = []"
            content += "\n\t"
            content += ")"



        with open("D:/Output.py", "w") as text_file:
            text_file.write(content)


