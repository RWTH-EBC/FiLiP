from filip.models.ngsi_v2.context import ContextEntity
from pydantic import BaseModel


class SemanticContextEntity(BaseModel):



    def get_class(self):
        pass

    def is_fulfilled(self):
        pass

    def is_agent(self):
        pass

    def is_device(self):
        pass