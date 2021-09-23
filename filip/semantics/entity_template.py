from typing import List, Union

from pydantic import Field

from filip.models.ngsi_v2.context import ContextEntity

from filip.semantics.semantic_context_entity import SemanticContextEntity


class AC_DC(SemanticContextEntity):
    """
    CLASS.comment
    """

    temperature: Union[List[str], int] \
                = Field(
                    type=Union[List[str], int],
                    default=[],
                    minItems=2,
                    description="CR.comment")


ac = AC_DC(temperature = 2)
