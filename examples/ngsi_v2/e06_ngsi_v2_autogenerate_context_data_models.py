"""
# This example shows how you can automatically build useful data model
# classes from context entity data or json-schema files.
# Afterwards, the generated models can be used for validation purposes.
#
# E.g. the Smart Data Models provide their models in such format.
# https://www.fiware.org/developers/smart-data-models/

# **Note**: Although the generator function in principle works quite well.
# It usage might be limited to uncommon definitions in the provided files or
# rather definitions that the used third-party library is currently not able to
# handle. Unfortunately, is especially happens a lot with the smart data model
# definitions

 """

# ## Import packages
import os
from pathlib import Path

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute
from filip.utils.model_generation import (
    create_data_model_file,
    create_context_entity_model,
)

# ## Parameters
path = Path(os.getcwd()).joinpath("./data_models")


if __name__ == "__main__":
    # ## 1. Create a custom context entity model
    # # create an entity that looks like the one you want to creat a model for
    attr = NamedContextAttribute(name="someAttr", type="TEXT", value="something")
    entity = ContextEntity(id="myId", type="MyType")
    entity.add_attributes(attrs=[attr])

    # ### 1.1 create the model and write it to a json-schema file
    model = create_context_entity_model(
        name="MyModel", data=entity.model_dump(), path=path.joinpath("entity.json")
    )

    # ### 1.2 create the model and write it to a python file
    model = create_context_entity_model(
        name="MyModel", data=entity.model_dump(), path=path.joinpath("entity.py")
    )
    # ## 2. Parsing from external resources
    #
    create_data_model_file(
        path=path.joinpath("commons.py"),
        url="https://smart-data-models.github.io/data-models/" "common-schema.json",
    )

    # ## 3. Use generated data models
    from examples.ngsi_v2.data_models.commons import (
        OpeningHoursSpecificationItem,
        time,
        DayOfWeek,
        datetime,
    )

    opening_hours = OpeningHoursSpecificationItem(
        opens=time(hour=10),
        closes=time(hour=19),
        dayOfWeek=DayOfWeek.Saturday,
        validFrom=datetime(year=2022, month=1, day=1),
    )

    print(opening_hours.json(indent=2))
