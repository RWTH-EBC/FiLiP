from typing import List, TYPE_CHECKING, Dict

from . import Entity
from .source import DependencyStatement

if TYPE_CHECKING:
    from . import Vocabulary, Class


class Individual(Entity):
    """
    Represents OWL:Individual

    An individual is a predefined "instance" of a class
    But they are here only used as values for Relations

    They are not instances, no value can be assigned to them, they are no
    agents or devices
    """

    parent_class_iris: List[str] = []
    """List of all parent class iris, an individual can have multiple parents"""

    def to_string(self) -> str:
        """Get a string representation of the Individual

        Returns:
            str
        """
        return "(Individual)"+self.get_label()

    def get_ancestor_iris(self, vocabulary: 'Vocabulary') -> List[str]:
        """ Get all iris of ancestor classes

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[str]
        """
        ancestor_iris = set()
        for parent_iri in self.parent_class_iris:
            ancestor_iris.add(parent_iri)
            ancestor_iris.update(vocabulary.get_class_by_iri(parent_iri).
                                 ancestor_class_iris)

        return list(ancestor_iris)

    def get_parent_classes(self, vocabulary: 'Vocabulary') -> List['Class']:
        """ Get all parent class objects

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[Class]
        """
        parents = []
        for parent_iri in self.parent_class_iris:
            parents.append(vocabulary.get_class_by_iri(parent_iri))
        return parents

    def is_logically_equivalent_to(self, individual: 'Individual',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if this individal is logically equivalent in two vocabularies.

        Args:
            individual (Individual): Individual to be tested against, from the
                old vocabulary
            vocabulary (Vocabulary): New project vocabulary, not used but needed
                to keep signature the same
            old_vocabulary (Vocabulary): Old project vocabulary, not used but
                needed to keep signature the same

        Returns:
            bool
        """

        if not self._lists_are_identical(self.parent_class_iris,
                                         individual.parent_class_iris):
            return False
        return True

    def treat_dependency_statements(self, vocabulary: 'Vocabulary') -> \
            List[DependencyStatement]:
        """ Purge and list all pointers/iris that are not contained in the
        vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
            Parent Class, class, dependency, fulfilled
        """
        statements = []

        for parent_iri in self.parent_class_iris:
            found = parent_iri in vocabulary.classes
            statements.append(DependencyStatement(type="Parent Class",
                                                  class_iri=self.iri,
                                                  dependency_iri=parent_iri,
                                                  fulfilled=found
                                                  ))

            if not found:
                self.parent_class_iris.remove(parent_iri)

        return statements
