# Exercise 3: Context Entities and Relationships

Create building context entity of type 'Building' according to FIWARE's
SmartData Models with the properties: `id`, `type`, `address`, `category`,
https://github.com/smart-data-models/dataModel.Building/blob/master/Building/doc/spec.md

<p align="center">
  <img src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/139-Add-images-to-tutorials/tutorials/ngsi_v2/e3_context_entities/tutorials_ngsi_v2-Exercise3.drawio.png" alt="Context 
entities"/>
</p>


For the single properties check on the "Data Model description of
properties" section. The input sections are marked with 'ToDo'

#### Steps to complete:
1. Set up the missing parameters in the parameter section
2. Find the Building data model online:
   https://github.com/smart-data-models/dataModel.Building/blob/master/Building/doc/spec.md
3. Create a `ContextEntity` object for your building
4. Create the required `ContextAttributes` and add them to your building model
5. Create a `ContextBrokerClient` and add post your building to the
   ContextBroker. Afterwards, check if the Context Broker returns the
   correct information about your building
6. Create an `opening hours` attribute add them to the server
7. Retrieve the `opening hours` manipulate them and update the model at the
   server
8. Repeat the procedure with a thermal zone. Currently, the smart data
   models hold no definition of a thermal zone. Therefore, we first only add a
   description attribute.
9. Add a `Relationship` attribute to your thermal zone with name
   `refBuilding` and type `Relationship` pointing to your building and post
   the model to the context broker
10. Add a `Relationship` attribute to your building with name
   `hasZone` and type `Relationship` pointing to your thermal zone and
   update the model in the context broker.
11. Update the thermal zone and the building in the context broker
12. Retrieve the data by using query statements for their relationships.