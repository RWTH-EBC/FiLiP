
from . import Entity
from typing import List, TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from . import CombinedObjectRelation, CombinedDataRelation, \
        CombinedRelation, Relation, Vocabulary
    from .combined_data_relation import CombinedDataRelation


class Class(Entity):
    """
    Representation of OWL:CLASS

    A class has a set of relations that are combined into CombinedRelations

    Instances are instantiations of a class

    A class can represent Devices, Agents, None or both
    """

    # Note: Most methods need to be given the vocabulary of this project,
    # while it is slightly faster than the indirect
    #        loading this is mostly a legacy style.

    is_agent_class: bool = False
    """Stating that this class is an node_agent_class, each instance of this 
    class will be a node agent"""
    is_iot_class: bool = False
    """Stating that this class is an device_class, each instance of this 
    class will represent a physical IoT device"""

    # The objects whose ids/iris are listed here can be looked up in the
    # vocabulary of this class
    child_class_iris: List[str] = []
    """All class_iris of classes that inherit from this class"""
    ancestor_class_iris: List[str] = []
    """All class_iris of classes from which this class inherits"""
    parent_class_iris: List[str] = []
    """All class_iris of classes that are direct parents of this class"""

    relation_ids: List[str] = []
    """All ids of relations defined for this class"""

    combined_object_relation_ids: List[str] = []
    """All combined_object_relations ids defined for this class"""
    combined_data_relation_ids: List[str] = []
    """All combined_data_relations ids defined for this class"""

    def get_relation_ids(self) -> List[str]:
        """Get all ids of relations belonging to this class

        Returns:
            List[str]
        """
        return self.relation_ids

    def get_relations(self, vocabulary: 'Vocabulary') -> List['Relation']:
        """Get all relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Relation]
        """
        result = []
        for id in self.relation_ids:
            result.append(vocabulary.get_relation_by_id(id))

        return result

    def get_combined_object_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedObjectRelation']:
        """Get all combined object relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedObjectRelation]
        """

        result = []
        for id in self.combined_object_relation_ids:
            result.append(vocabulary.get_combined_object_relation_by_id(id))

        return result

    def get_combined_data_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedDataRelation']:
        """Get all combined data relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedDataRelation]
        """

        result = []
        for id in self.combined_data_relation_ids:
            result.append(vocabulary.get_combined_data_relation_by_id(id))

        return result

    def get_combined_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedRelation']:
        """Get all combined relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedRelation]
        """

        result = self.get_combined_object_relations(vocabulary)
        result.extend(self.get_combined_data_relations(vocabulary))
        return result

    def is_child_of_all_classes(self, target_list: List[str]) -> bool:
        """Tests if this class is a child class for each of the given classes

        Args:
            target_list (List[str]): List of ancestor class_iris

        Returns:
            bool
        """

        for target in target_list:
            if not target == self.iri:
                if target not in self.ancestor_class_iris:
                    return False
        return True

    def get_combined_object_relation_with_property_iri(
            self, obj_prop_iri: str, vocabulary: 'Vocabulary') \
            -> 'CombinedObjectRelation':
        """Get the CombinedObjectRelation of this class that combines the
        relations of the given ObjectProperty

        Args:
            obj_prop_iri (str): Iri of the ObjectProperty
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedObjectRelation
        """
        for cor in self.get_combined_object_relations(vocabulary):
            if cor.property_iri == obj_prop_iri:
                return cor
        return None

    def get_combined_data_relation_with_property_iri(self, property_iri,
                                                     vocabulary):
        """Get the CombinedDataRelation of this class that combines the
        relations of the given DataProperty

        Args:
            property_iri (str): Iri of the DataProperty
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedDataRelation
        """
        for cdr in self.get_combined_data_relations(vocabulary):
            if cdr.property_iri == property_iri:
                return cdr
        return None

    def get_combined_relation_with_property_iri(self, property_iri, vocabulary)\
            -> Union['CombinedRelation', None]:
        """Get the CombinedRelation of this class that combines the relations
        of the given Property

        If possible use the more specific access functions to save runtime.

        Args:
            property_iri (str): Iri of the Property
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedRelation, None if iri is unknown
       """
        for cdr in self.get_combined_data_relations(vocabulary):
            if cdr.property_iri == property_iri:
                return cdr
        for cor in self.get_combined_object_relations(vocabulary):
            if cor.property_iri == property_iri:
                return cor
        return None

    def get_ancestor_classes(self, vocabulary: 'Vocabulary') -> List['Class']:
        """Get all ancestor classes of this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Class]
        """
        ancestors = []
        for ancestor_iri in self.ancestor_class_iris:
            ancestors.append(vocabulary.get_class_by_iri(ancestor_iri))
        return ancestors

    def get_parent_classes(self, vocabulary: 'Vocabulary') -> List['Class']:
        """Get all parent classes of this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Class]
        """
        parents = []

        for parent_iri in self.parent_class_iris:
            parents.append(vocabulary.get_class_by_iri(parent_iri))

            if vocabulary.get_class_by_iri(parent_iri) is None:
                print("Parent in class {} with iri {} was none".format(
                    self.iri, parent_iri))

        return parents

    def treat_dependency_statements(self, vocabulary: 'Vocabulary') -> \
            List[Dict[str, str]]:
        """ Purge and _list all pointers/iris that are not contained in
        the vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
            Parent Class, class, dependency, fulfilled
        """

        statements = []
        # parent classes:
        parents_to_purge = []
        for parent_iri in self.parent_class_iris:
            found = parent_iri in vocabulary.classes
            statements.append({"type": "Parent Class", "class": self.iri,
                               "dependency": parent_iri, "fulfilled": found})
            if not found:
                parents_to_purge.append(parent_iri)
        for iri in parents_to_purge:
            self.parent_class_iris.remove(iri)

        # relations
        relation_ids_to_purge = []
        for relation in self.get_relations(vocabulary):

            relation_statements = relation.get_dependency_statements(
                vocabulary, self.get_ontology_iri(), self.iri)
            for statement in relation_statements:
                if statement['fulfilled'] == False:
                    relation_ids_to_purge.append(relation.id)
            statements.extend(relation_statements)

        for id in relation_ids_to_purge:
            self.relation_ids.remove(id)
            del vocabulary.relations[id]

        return statements

    def get_key_column_ids(self, vocabulary: 'Vocabulary') -> List[str]:
        """Get all CombinedRelation ids that should be listed in tables

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[str]: CombinedRelation ids
        """
        res = []
        for id in self.combined_data_relation_ids:
            if vocabulary.get_combined_relation_by_id(id).is_key_information:
                res.append(id)
        for id in self.combined_object_relation_ids:
            if vocabulary.get_combined_relation_by_id(id).is_key_information:
                res.append(id)
        return res

    def get_next_combined_relation_id(self, current_cr_id: str,
                                      object_relations: bool) -> str:
        """Get the alphabetically(Property label) next CombinedRelation.

        If no CR is after the given one, the first is returned

        Args:
            current_cr_id (str): ID of the CombinedRelation of which the next
            should be found object_relations (bool):
                True if Searching for  CombinedObjectRelations

        Returns:
            str: ID of next CR
        """
        list = self.combined_data_relation_ids
        if object_relations:
            list = self.combined_object_relation_ids

        current_index = list.index(current_cr_id)
        res_index = current_index+1
        if res_index >= len(list):
            res_index = 0
        return list[res_index]

    def get_previous_combined_relation_id(self, current_cr_id: str,
                                          object_relations: bool) -> str:
        """Get the alphabetically(Property label) previous CombinedRelation.

        If no CR is before the given one, the last is returned

        Args:
            current_cr_id (str): ID of the CombinedRelation of which the
                previous should be found
            object_relations (bool): True if Searching for
                CombinedObjectRelations

        Returns:
            str: ID of previous CR
        """

        list = self.combined_data_relation_ids
        if object_relations:
            list = self.combined_object_relation_ids

        current_index = list.index(current_cr_id)
        res_index = current_index - 1
        if res_index < 0:
            res_index = len(list)-1
        return list[res_index]

    def is_logically_equivalent_to(self, class_: 'Class',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if a class is logically equivalent in two vocabularies.

        Args:
            class_ (Class): Class to be tested against, from the old_vocabulary
            vocabulary (Vocabulary): New project vocabulary
            old_vocabulary (Vocabulary): Old project vocabulary

        Returns:
            bool
        """

        # test if parent classes are identical
        if not self._lists_are_identical(class_.parent_class_iris,
                                         self.parent_class_iris):
            return False

        # test if combined object relation ids are identical
        if not self._lists_are_identical(class_.combined_object_relation_ids,
                                         self.combined_object_relation_ids):
            return False

        # test if combined data  relation ids are identical
        if not self._lists_are_identical(class_.combined_data_relation_ids,
                                         self.combined_data_relation_ids):
            return False

        # test if combined relations are identical
        for cr in self.get_combined_relations(vocabulary):
            old_cr = old_vocabulary.get_combined_relation_by_id(cr.id)

            relation_strings = []
            for relation in cr.get_relations(vocabulary):
                relation_strings.append(relation.to_string(vocabulary))

            old_relation_strings = []
            for old_relation in old_cr.get_relations(old_vocabulary):
                old_relation_strings.append(old_relation.to_string(vocabulary))

            if not self._lists_are_identical(relation_strings,
                                             old_relation_strings):

                return False

        return True

    def get_all_commands_of_class(self, vocabulary: 'Vocabulary') -> \
            List['CombinedDataRelation']:
        """Get all CombinedDataRelations that are marked as CommandFields for
        this class

        Args:
            vocabulary (Vocabulary): project vocabulary

        Returns:
            List[CombinedDataRelation]
        """

        from .combined_data_relation import CDRType
        res = []
        for cdr_id in self.combined_data_relation_ids:
            if vocabulary.get_combined_data_relation_by_id(cdr_id).type == \
                    CDRType.Command:
                res.append(vocabulary.get_combined_data_relation_by_id(cdr_id))

        return res

    def get_all_device_data_of_class(self, vocabulary: 'Vocabulary') -> \
            List['CombinedDataRelation']:
        """Get all CombinedDataRelations that are marked as DeviceDataFields
        for this class

        Args:
            vocabulary (Vocabulary): project vocabulary

        Returns:
            List[CombinedDataRelation]
        """

        from .combined_data_relation import CDRType
        res = []
        for cdr_id in self.combined_data_relation_ids:
            if vocabulary.get_combined_data_relation_by_id(cdr_id).type == \
                    CDRType.DeviceData:
                res.append(vocabulary.get_combined_data_relation_by_id(cdr_id))

        return res
