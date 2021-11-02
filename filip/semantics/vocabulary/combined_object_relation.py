

from . import CombinedRelation
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Vocabulary


class CombinedObjectRelation(CombinedRelation):
    """
    Combines all object relations of a class that share the same ObjectProperty
    Represents one Relation Field of a class
    """

    def get_all_possible_target_class_iris(self, vocabulary) -> List[str]:
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