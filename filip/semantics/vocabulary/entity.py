from typing import TYPE_CHECKING, List

from pydantic import BaseModel


if TYPE_CHECKING:
    from . import Vocabulary


unallowed_labels = ["id","type","geo:property", "metadata"]
"""Labels that are not allowed, as the would lead to errors in FIWARE"""
allowed_label_symbols = ["-", "_"]
"""Whitelisted special symbols that can be used in labels"""


class Entity(BaseModel):
    """
    Representing an OWL Entity (Class, Datatype, DataProperty, ObjectProperty,
                                Individual)

    An Entity is characterised by a unique IRI and originates from a source

    An Entity needs a unique Label (displayname) as it is used in FIWARE as
    field key. The user can overwrite the given
    label
    """
    iri: str
    """Unique Internationalized Resource Identifier """
    label: str = ""
    """Label (displayname) extracted from source file 
            (multiple Entities could have the same label)"""
    user_set_label = ""
    """Given by user and overwrites 'label'. Needed to make labels unique """
    comment: str = ""
    """Comment extracted from the ontology/source"""
    source_id: str = ""
    """ID of the source"""
    predefined: bool = False
    """Stats if the entity is not extracted from a source, but predefined 
    in the program (Standard Datatypes)"""

    # if no specific label was given, extract the name out of the iri
    def get_label(self) -> str:
        """ Get the label for the entity.
        If the user has set a label it is returned, else the label extracted
        from the source

        Returns:
             str
        """
        if not self.user_set_label == "":
            return self.user_set_label

        return self.get_original_label()

    def get_ontology_iri(self) -> str:
        """ Get the IRI of the ontology that this entity belongs to
        (extracted from IRI)

        Returns:
            str
        """
        index = self.iri.find("#")
        return self.iri[:index]

    def get_source_id(self) -> str:
        """ Get ID of the source

        Returns:
            str
        """
        return self.source_id

    def get_source_name(self, vocabulary: 'Vocabulary') -> str:
        """ Get name of the source

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        return vocabulary.get_source(self.source_id).get_name()

    def _lists_are_identical(self, a: List, b: List) -> bool:
        """ Methode to test if to lists contain the same entries

        Args:
            a (List): first list
            b (List): second list
        Returns:
            bool
        """
        return len(set(a).intersection(b)) == len(set(a)) and len(a) == len(b)

    def is_renamed(self) -> bool:
        """ Check if the entity was renamed by the user

        Returns:
            bool
        """
        return not self.user_set_label == ""

    def get_original_label(self) -> str:
        """ Get label as defined in the source
        It can be that the label is empty, then extract the label from the iri

        Returns:
            str
        """
        if not self.label == "":
            return self.label

        index = self.iri.find("#") + 1
        return self.make_label_safe(self.iri[index:])

    def make_label_safe(self, label: str) -> str:
        """ make the given label FIWARE safe

        Args:
            label (str): LAble to make Fiware safe

        Returns:
            str
        """
        label = label.replace(" ", "_")
        label = label + "*"

        for char in label:
            if not char.isalnum():
                if char not in allowed_label_symbols:
                    label = label.replace(char, "")

        return label

    @staticmethod
    def is_label_protected(label: str) -> bool:
        """ Test if the given label is protected, and is therefore invalid

        Args:
            label (str): label to test

        Returns:
            bool
        """

        if label in unallowed_labels:
            return True

        # Fiware automatically created entity fields with these endings for
        # device commands
        if len(label) >= 5 and label[-5:] == "_info":
            return True
        if len(label) >= 7 and label[-7:] == "_status":
            return True

        return False

    @staticmethod
    def are_chars_in_label_allowed(label: str) -> bool:
        """ Test if the given label contains no blacklisted chars

        Args:
            label (str): label to test

        Returns:
           bool
        """
        for char in label:
            if not char.isalnum():
                if char not in allowed_label_symbols:
                    return False
            if char == " ":
                return False
        return True
