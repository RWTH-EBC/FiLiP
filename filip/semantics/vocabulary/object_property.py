from typing import List, Set, TYPE_CHECKING

from . import Entity

if TYPE_CHECKING:
    from . import Vocabulary


class ObjectProperty(Entity):
    """
    Representation of OWL:ObjectProperty
    """

    inverse_property_iris: Set[str] = set()
    """List of property iris that are inverse:Of; 
    If an instance i2 is added in an instance i1 for this property. 
    Then i1 is added to i2 under the inverseProperty 
    (if the class has that property)
    """

    def add_inverse_property_iri(self, iri: str):
        """Add an inverse property

        Args:
            iri (str): Iri of the inverse objectProperty

        Returns:
            None
        """
        self.inverse_property_iris.add(iri)

    def is_logically_equivalent_to(self, object_property: 'ObjectProperty',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:

        """Test if this Property in the new_vocabulary is logically equivalent
        to the object_property in the old_vocabulary

        Args:
            object_property (ObjectProperty): ObjectProperty to be tested
                against, from the old vocabulary
            vocabulary (Vocabulary): New project vocabulary, not used but
                needed to keep signature the same
            old_vocabulary (Vocabulary): Old project vocabulary, not used but
                needed to keep signature the same

        Returns:
            bool
        """
        if not self.inverse_property_iris == \
                object_property.inverse_property_iris:
            return False

        return True
