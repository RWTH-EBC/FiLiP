from typing import Union, Optional
from pydantic import BaseModel, Field, ConfigDict


class GeoQuery(BaseModel):
    """
    GeoQuery used for Subscriptions, as described in NGSI-LD Spec section 5.2.13
    """
    geometry: str = Field(
        description="A valid GeoJSON [8] geometry, type excepting GeometryCollection"
    )
    coordinates: Union[list, str] = Field(
        description="A JSON Array coherent with the geometry type as per "
                    "IETF RFC 7946 [8]"
    )
    georel: str = Field(
        description="A valid geo-relationship as defined by clause 4.10 (near, "
                    "within, etc.)"
    )
    geoproperty: Optional[str] = Field(
        default=None,
        description="Attribute Name as a short-hand string"
    )
    model_config = ConfigDict(populate_by_name=True)


def validate_ngsi_ld_query(q: str) -> str:
    """
    Valid query string as described in NGSI-LD Spec section 5.2.12
    Args:
        q: query string
    Returns:

    """
    return q
