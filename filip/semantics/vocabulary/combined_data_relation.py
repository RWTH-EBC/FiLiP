from enum import Enum
from typing import List, TYPE_CHECKING

from . import CombinedRelation

if TYPE_CHECKING:
    from . import Vocabulary


class CDRType(Enum):
    """Type of this CombinedDataRelations, it is either:
           -   UserSetData (Default): The user defines values (ex: RoomNumber)
           -   DeviceData (Device Only): The field hods values that are read
                    from the device (ex: TemperaturMeasrument)
           -   Command (Device Only): The field holds the name of the command
                    that needs to be send to the device

    """
    DeviceData = "DeviceData"
    UserSetData = "UserSetData"
    Command = "Command"


class CombinedDataRelation(CombinedRelation):
    """
    Combines all data relations of a class that share the same DataProperty
    Represents one Data Field of a class
    """

    type: CDRType = CDRType.UserSetData
    """Type of this CDR, it is either:
        -   UserSetData (Default): The user defines values (ex: RoomNumber)
        -   DeviceData (Device Only): The field hods values that are read from 
                the device (ex: TemperaturMeasrument)
        -   Command (Device Only): The field holds the name of the command 
                that needs to be send to the device
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
