"""Vocabulary Models for CombinedRelations"""
from aenum import Enum

from filip.semantics.vocabulary import DataFieldType
from pydantic import BaseModel, Field
from typing import List, TYPE_CHECKING, Set
from . import Relation

if TYPE_CHECKING:
    from . import Vocabulary


class CombinedRelation(BaseModel):
    """
    Combines all relations of a class that share the same Property
    Represents one Field of a class. SHORT: CR

    It provides the common ground for the specialisations:
        CombinedObjectRelation, CombinedDataRelation
    """

    id: str = Field(description="Generated unique ID of the CR")
    relation_ids: List[str] = Field(
        default=[],
        description="List of all relations of the class that are "
                    "bundled; have the same property")
    property_iri: str = Field(description="IRI of the property, under which "
                                          "the relations are bundled")
    class_iri: str = Field(description="IRI of the class the relations and "
                                       "this CR belongs to")

    def get_relations(self, vocabulary: 'Vocabulary') -> List[Relation]:
        result = []
        for id in self.relation_ids:
            result.append(vocabulary.get_relation_by_id(id))

        return result

    def get_property_label(self, vocabulary: 'Vocabulary') -> str:
        """Get the label of the Property. Overwritten by children

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        return ""

    def get_all_targetstatements_as_string(self, vocabulary: 'Vocabulary') \
            -> str:
        """
        Get a string stating all conditions(target statement) that need to
        be fulfilled, so that this CR is fulfilled

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        res = ""
        for relation in self.get_relations(vocabulary=vocabulary):
            res = res + relation.to_string(vocabulary) + ", "

        return res[:-2]

    def get_all_target_iris(self, vocabulary: 'Vocabulary') -> Set[str]:
        """Get all iris of referenced targets

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            set(str)
        """
        iris = set()

        for relation_id in self.relation_ids:
            relation = vocabulary.get_relation_by_id(relation_id)
            iris.update(relation.get_all_target_iris())
        return iris

    def get_all_target_labels(self, vocabulary: 'Vocabulary') -> Set[str]:
        """ Get all labels of referenced targets

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            set(str)
        """
        return {vocabulary.get_label_for_entity_iri(iri)
                for iri in self.get_all_target_iris(vocabulary)}

    def export_rule(self, vocabulary: 'Vocabulary',
                    stringify_fields: bool) -> str:
        """Get the rule as string

        Args:
           vocabulary (Vocabulary): Vocabulary of the project
           stringify_fields (bool): If true, all string delimieters will be
                removed

        Returns:
           str
        """

        rules = [vocabulary.get_relation_by_id(id).export_rule(vocabulary)
                 for id in self.relation_ids]
        if stringify_fields:
            return str(rules).replace('"', "")
        else:
            return str(rules).replace("'","").replace('"', "'")


class CombinedDataRelation(CombinedRelation):
    """
    Combines all data relations of a class that share the same DataProperty
    Represents one Data Field of a class
    """

    def get_property_label(self, vocabulary: 'Vocabulary') -> str:
        """Get the label of the DataProperty

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        return vocabulary.get_data_property(self.property_iri).get_label()

    def get_possible_enum_target_values(self, vocabulary: 'Vocabulary') \
            -> List[str]:
        """Get all enum values that are allowed as values for this Data field

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[str]
        """

        enum_values = set()

        for relation in self.get_relations(vocabulary):
            for value in relation.get_possible_enum_target_values(vocabulary):
                enum_values.add(value)

        return sorted(list(enum_values))

    def get_field_type(self, vocabulary: 'Vocabulary') -> DataFieldType:
        """Get type of CDR (command, devicedata , simple)

         Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            DataFieldType
        """
        property = vocabulary.get_data_property(self.property_iri)
        return property.field_type

    def is_device_relation(self, vocabulary: 'Vocabulary') -> bool:
        """Test if the CDR is a device property(command, or readings)

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            bool
        """
        return not self.get_field_type(vocabulary) == DataFieldType.simple


class CombinedObjectRelation(CombinedRelation):
    """
    Combines all object relations of a class that share the same ObjectProperty
    Represents one Relation Field of a class
    """

    def get_all_possible_target_class_iris(self, vocabulary) -> List[str]:
        """Get all iris that are valid values for this cor

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[str]
        """
        from . import Vocabulary
        assert isinstance(vocabulary, Vocabulary)

        relations = self.get_relations(vocabulary)
        result_set = set()
        for relation in relations:
            result_set.update(relation.
                              get_all_possible_target_class_iris(vocabulary))

        return list(result_set)

    def get_property_label(self, vocabulary: 'Vocabulary') -> str:
        """Get the label of the ObjectProperty

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        return vocabulary.get_object_property(self.property_iri).get_label()

    def get_inverse_of_labels(self, vocabulary: 'Vocabulary') -> List[str]:
        """Get the labels of the inverse_of properties of this COR

         Args:
             vocabulary (Vocabulary): Vocabulary of the project

         Returns:
             List[str]
         """
        property = vocabulary.get_object_property(self.property_iri)
        return [vocabulary.get_entity_by_iri(iri).label
                for iri in property.inverse_property_iris]