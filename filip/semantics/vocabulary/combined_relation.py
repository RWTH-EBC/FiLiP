
from pydantic import BaseModel
from typing import List, TYPE_CHECKING, Set
import uuid
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

    id: str
    """Generated unique ID of the CR"""
    relation_ids: List[str]
    """List of all relations of the class that are bundled; 
    have the same property"""
    property_iri: str
    """IRI of the property, under which the relations are bundled"""
    class_iri: str
    """IRI of the class the relations and this CR belongs to"""

    is_key_information: bool = False
    """user settings for field: Should this CR be displayed as column in a 
    table. Default: FALSE """
    inspect: bool = True
    """user settings for field: Does this field needs to fulfiled to deem the 
    instance fulfilled. Default: TRUE """

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
        """Get a string stating all conditions(target statement) that need to
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
        iris = set()

        for relation_id in self.relation_ids:
            relation = vocabulary.get_relation_by_id(relation_id)
            iris.update(relation.get_all_target_iris())
        return iris

    def get_all_target_labels(self, vocabulary: 'Vocabulary') -> Set[str]:
        return {vocabulary.get_label_for_entity_iri(iri)
                for iri in self.get_all_target_iris(vocabulary)}

    def export_rule(self, vocabulary: 'Vocabulary') -> str:

        rules= [vocabulary.get_relation_by_id(id).export_rule(vocabulary)
                for id in self.relation_ids]
        # return str(rules).replace('"', "")
        return str(rules).replace("'","").replace('"', "'")
