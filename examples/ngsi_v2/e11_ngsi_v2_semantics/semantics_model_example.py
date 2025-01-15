"""
# Examples for modelling a real world state with a generated vocabulary model
# The model will be imported, classes and devices created, given values,
# and check if they are valid.
# The whole modeling state is then saved at once to fiware.
# Following the fiware state will be edited with automatic partial loading
"""

"""
To run this example you need a working Fiware v2 setup with a context-broker 
and an iota-broker. You can here set the addresses:
"""
from filip.config import settings

cb_url = settings.CB_URL
iota_url = settings.IOTA_URL

if __name__ == "__main__":

    # # 0 Clean up Fiware state:
    #
    # For this example to work the fiware state needs to be clean:
    from filip.models.base import FiwareHeader
    from filip.utils.cleanup import clear_all

    fiware_header = FiwareHeader(service="example", service_path="/")
    clear_all(fiware_header=fiware_header, cb_url=cb_url, iota_url=iota_url)

    # # 1 Import Models
    #
    # First we need to import the models that we have created in the
    # "semantics_vocabulary_example" and exported into the file "models.py".
    # Each vocabulary class was converted to a python class and can now be
    # instantiated.
    # Additionally the class semantic_manager is created and will be used to
    # manage the local state as well as save it.
    # It is important that we only import one vocabulary model file,
    # if we want to use multiple models, we need to combine them in a
    # vocabulary and export them as one file.

    # We can import the classes selectively or all at once
    from models import semantic_manager
    from models import Floor, Building
    from models import *

    # # 2 Semantic Classes
    #
    # The classes (with exception of semantic_manager) are either
    # SemanticClasses that can be used to model or SemanticDeviceClasses
    # where each instance represents one iot-device.
    # Further SemanticClasses are referred to as normal-classes and
    # SemanticDeviceClasses as device-classes. The term class is used as a
    # grouping term for both.

    # Each instance of a class is uniquely defined by its
    # combination of:
    #   - id: A string given at creation by the user
    #   - type: Equals to the class name/label
    #   - header: Information where the information is stored in Fiware;
    #             contains:
    #               -   cb_url: Adresse of the used Fiware context-broker
    #               -   iota_url: Adresse of the used Fiware iota-broker
    #               -   ngsi_version: States if Fiware v2 or LD is used
    #               -   service: multi-tenancy space used in Fiware
    #               -   service-path: subpath in the multi-tenancy
    #
    # More details about the uniqueness later

    # ## 2.1 Instantiating a class
    #
    # We can create an instance of a class by simply instantiating and
    # passing the id and header as parameters.
    from filip.semantics.semantics_models import InstanceHeader
    from filip.models.base import NgsiVersion

    header = InstanceHeader(
        cb_url=cb_url,
        iota_url=iota_url,
        ngsi_version=NgsiVersion.v2,
        service="example",
        service_path="/",
    )

    my_floor = Floor(id="my-first-floor", header=header)

    # If we work with the often with the same header we can also set a
    # default header in the semantic_manager. If a class without a header
    # parameter is created it gets automatically assigned this default header.

    semantic_manager.set_default_header(header)
    my_building = Building(id="building1")

    # ## 2.2 Immutability
    #
    # These defining information of an instance are immutable and can not
    # be changed after the creation.
    # They are further bundled into an identifier object that is used as an
    # identity by the system: The InstanceIdentifier

    # We can have a look at this identifier, and see that the header was
    # correctly set:
    print("\u0332".join("Instance Identifier of my_building:"))
    print(my_building.get_identifier())
    print("")

    # ## 2.3 Device Classes
    #
    # Device-classes are a subtype of normal classes, they work as normal
    # classes, but posses additional field types and information about the
    # iot device that they are representing
    my_sensor = Sensor(id="sensor1")
    my_outlet = Outlet(id="o1")

    # All information about the device is gathered in the device settings
    # property of the instance
    # After initialisation all values are None:
    print("\u0332".join("Device settings:"))
    print(my_sensor.device_settings)
    print("")

    # Before the device instance can be saved the transport and endpoint
    # properties need to be set, all other properties are optional
    from filip.models.ngsi_v2.iot import TransportProtocol

    my_sensor.device_settings.endpoint = "http://localhost:1001"
    my_sensor.device_settings.transport = TransportProtocol.HTTP

    # # 2.4 Finding a fitting class
    #
    # If you are unsure which semantic class could be the right one to model
    # your current need, you can search for a fitting possibility:

    fitting_names = semantic_manager.find_fitting_model("SmokeSensor")

    print("\u0332".join("Found models for 'SmokeSensor':"))
    print(fitting_names)
    print("")

    # The search returns up to 5 model names as string. If a fitting name was
    # selected the corresponding class can be retrieved and instantiated:
    class_ = semantic_manager.get_class_by_name(fitting_names[0])
    sensor_instance = class_(id="temp_sensor")

    # # 3 Class Fields
    #
    # Our classes possess fields that we use to model the state. There are
    # multiple types of fields a normal-class or device-class can have.
    # Basically a field is a set to which values can be added, but that posses
    # additional functions and internal logic. Therefore values of a field
    # are without duplicates and without order
    # (These requirements are needed to manage the state merge of concurrent
    # changes)

    # To view all fields a class possesses we can either:
    #   - try the autocompletion hint when typing building.
    #   - look inside the modules file
    #   - use the functions: .get
    print("\u0332".join("All fields of the Building class:"))
    print(my_building.get_all_field_names())
    print("")

    # To manipulate data inside a field all standard set interactions are
    # given:
    my_building.goalTemperature.add(23)
    my_building.goalTemperature.update([12])
    my_building.goalTemperature.remove(23)
    my_building.goalTemperature.clear()

    # ## 3.1 RuleFields
    #
    # A RuleField contains 1 or multiple rules that need to be fulfilled
    # for the field to be valid. RuleFields are separated into Relation- and
    # DataFields. All fields of normal classes are RuleFields

    # To view the rule of a field we can simply inspect its rule property.
    # (This property is fixed by the model file and is immutable at runtime)

    print("\u0332".join("Field Rules:"))
    # As it is a normal class all fields are per definition rule_fields
    for field in my_building.get_fields():
        print(f"Name: {field.name}, Rule: {field.rule}")
    print("")

    # Possible rules are:
    # - min n
    # - max n
    # - exactly n
    # - some (equals min 1)
    # - all

    # A field can have multiple rules that all need to be fulfilled for the
    # field to be treated as valid. An instance is valid if all its fields
    # are valid

    print("\u0332".join("my_building is currently valid:"))
    print(my_building.are_rule_fields_valid())
    print("")

    # To make the instance valid we need to add values to our rule fields. We
    # look herefore at the subtypes of RuleFields.

    # ### 3.1.1 DataFields:
    #
    # Each ComplexDataProperty in our vocabulary with the
    # type "simple" was converted to this field type. (All for normal classes)
    # As values it takes basic types as string, int, bool,..

    my_building.goalTemperature.add(23)
    my_building.name.add("Main Building")

    # we can check again if all DataFields are now valid:
    print("\u0332".join("DataFields of my_building:"))
    for field in my_building.get_data_fields():
        print(
            f"Name: {field.name}, Rule: {field.rule}, Values: "
            f"{field.get_all_raw()}, Valid: {field.is_valid()}"
        )
    print("")

    # Datafields can also specify rules with Datatype enums, in that case we
    # can either directly add the string, or use the enum of the model
    # In each case only the string value gets saved without enum information
    # Each enum value has the prefix value_ to prevent name clashes
    sensor = Sensor(id="sensor1")
    sensor.measures.add(MeasurementType.value_Air_Quality)
    sensor.measures.add("Air_Quality")
    print("\u0332".join("DataFields with enum values:"))
    print(f"Raw Values: {sensor.measures.get_all_raw()}")
    print(f"Values: {sensor.measures.get_all()}")
    print("")

    # ### 3.1.1 RelationFields
    #
    # Each ComplexRelationProperty in our vocabulary
    # was converted to this field type.
    # As values it takes instances of classes

    my_building.hasFloor.add(my_floor)
    my_building.hasFloor.add(Floor(id="second_floor"))

    # we can check again if all RelationFields are now valid:
    print("\u0332".join("RelationFields of my_building:"))
    for field in my_building.get_relation_fields():
        print(
            f"Name: {field.name}, Rule: {field.rule}, Values: "
            f"{field.get_all_raw()}, Valid: {field.is_valid()}"
        )
    print("")

    # As we can see the RelationField internally only saves the references to
    # the instances that he was given as values.
    # But we can access the instances comfortably by calling get_all or even
    # iterating over the field:

    all_instances = my_building.hasFloor.get_all()

    for instance in my_building.hasFloor:
        instance.hasRoom.add(Room(id="r1"))

    # we added my_floor as first value into hasFloor, therefore one_instance
    # now points to exactly the same object as my_floor

    # as the value inside the hasFloor field is dynamically set, we can not
    # use type hints when working with it. But if we assign a value and then
    # inspect my_floor we see that they are correctly linked.

    print("\u0332".join("Inspect my_floor.hasRoom:"))
    print(my_floor.hasRoom)
    print("")

    # DO NOT CAST an instance to a type ex: Floor(instance) this will result
    # in an internally different state !

    # A relation field can also take Individuals as values, or even require
    # them via rules. Instances are globally static, final  classes,
    # each instance of an Individual is equal

    my_floor.hasRoom.add(ExampleIndividual())

    # An individual is not saved as Identifier as it is not directly saved in
    # Fiware instead it is only saved as string, as a
    # kind of enum.

    print("\u0332".join("Individual internal saving:"))
    for field in my_building.get_relation_fields():
        print(my_floor.hasRoom.get_all_raw())
    print("")

    # To each field each Instance or Individual can only be added once.
    # For example adding i1 twice to the field f of i1 will throw an ValueError

    # As we save the InstanceIdentifier as references, who holds all needed
    # lookup information we can reference instances in other services,
    # service-paths or even FiwareSetups

    # RelationFields can have a property inverse_of. (Linked to the
    # object_property property "inverse_of" of owl ontologies)
    # Example:
    # in_building is the inverse_of hasRoom and vis-versa
    # If the instance room1 adds the instance building1 as a value int the
    # RelationField in_building, room1 will be automatically added as value
    # in the field hasRoom of building1.
    # This mechanism is not executed if the inverse field does not exist in
    # the added instance.
    # The same logic is also applied to the deletion of value from a
    # RelationField
    # One field can have multiple inverse_ofs

    # ## 3.2 DeviceFields.
    #
    # Each ComplexDataProperty in our vocabulary with a
    # type other than "simple" was converted to this field type. Only device
    # classes posses fields of this type.

    # ### 3.2.1 DeviceAttributeField (type="device_attribute").
    #
    # This field allows us to link directly to properties of the iot device
    # and read them in.

    # In a DeviceAttributeField can therefore multiple DeviceAttributes be
    # added.
    # A DeviceAttribute has two properties:
    # - name: The internal name that the specific device uses for this property
    # - attribute_type: if the value should be lazy or actively read by fiware

    # Our sensor has one measurement property that he names internally m
    # We add this attribute to our measurement_field.

    from filip.semantics.semantics_models import DeviceAttribute, DeviceAttributeType

    my_sensor.measurement.add(
        DeviceAttribute(name="m", attribute_type=DeviceAttributeType.active)
    )

    # To access the value of the attribute we could call:
    # my_sensor.measurement[0].get_value()
    # But only after we saved this state to Fiware, so that the attribute is
    # present. (More to this later)

    # ### 3.2.2 CommandField (type="command").
    #
    # This field allows us to directly control the linked IoT device by
    # sending commands.

    # To do this we need to add Commands to the CommandField.
    # A command has 1 property:
    # - name: The internal name that the specific device uses for this purpose
    from filip.semantics.semantics_models import Command

    c1 = Command(name="open")
    my_outlet.controlCommand.add(c1)

    my_floor.hasRoom.add(my_building)
    print(my_building.build_context_entity().json(indent=2))

    # After the current state was saved. We can interact with the command. It
    # offers three functions:
    # - c1.send(): Send the command to the device to execute it
    # - c1.get_info(): View the result of the executed command
    # - c1.get_status(): See the current status of the sent command

    # ### 3.2.3 Uniqueness
    #
    # A property (Command, DeviceAttribute) can only be added to one instance
    # A property will add fields to the Fiware instance, as field names need
    # to be unique, a name check is made if a new property is added to an
    # instance field.
    # If a required field of the new property is already existing an error is
    # raised

    # ## 3.3 Metadata
    #
    # Each instance has the special attribute "metadata".
    # Here the user can save information that can help him identify the
    # instance. He can give the instance a name, and leave a comment

    my_floor.metadata.name = "First Basement"
    my_floor.metadata.comment = "The first basement is directly below the " "ground"

    # # 4 State Management
    #
    # We now have seen how the models can be instantiated, filled with
    # values and used to interact with iot-devices.
    # We will now see how the state is managed and how it can be saved and
    # loaded.

    # The library works in two state layers everything we create, load and
    # change is governed in the LocalState. Only if we save the state and the
    # state is valid all made changes will be transferred to the FiwareState.

    # ## 4.1 Creating/Loading
    #
    # As explained in (1) all instances are uniquely defined by their
    # InstanceIdentifier.
    # If a new instance is created: MyClass(id="x", header=..) with the
    # identifier IDEN the following logic is run:
    #  - Is IDEN registered in the LocalState:
    #       Yes -> return Object out of LocalState
    #  - Does the object exists at the given Fiware location:
    #       Yes -> Load Object into LocalState, return Object
    #  - Else:
    #       Create new Object, save Object in LocalState, return Object

    # This means that in the construction and initiating process of a new object
    # not always a new object is generated

    # If on two separate places in the same runtime an object with the same
    # Identifier is created, both pointers will point to the same object!

    # This logic is most beneficial for hot-loading from Fiware.
    # If we want to edit an existing state on Fiware we can directly access
    # the objects that we need by creating Objects of the corresponding
    # class, id and header. The object probably also has references to other
    # objects, which again reference objects and so on.
    # To prevent long unnecessary loading, a referenced object is only loaded
    # if it is directly accessed.
    # Example:
    #   In Fiware we have saved: Building b and Floor f, b references f in
    #   hasFloor index 1.
    #   If we load b, f is not loaded. f gets loaded the moment we access
    #   b.hasFloor[1] and is then present in the local state

    # If we want/need to batch load a set of entities in the local state,
    # we can use the corresponding functions in the semantic_manager:

    from filip.models.base import FiwareHeader

    semantic_manager.load_instances_from_fiware(
        fiware_version=NgsiVersion.v2,
        fiware_header=FiwareHeader(service="Example", service_path="/"),
        cb_url=cb_url,
        iota_url=iota_url,
        entity_ids=[],  # list of ids to load
        # or entity_types=[...],  # list of types to load
    )

    # ## 4.2 Saving the Local State
    #
    # If we have finished editing in the local state we can publish our
    # changes to the Fiware State.
    # Before we can do that all instances in the local state need to be valid.

    # We can check this for each instance by calling:
    print("\u0332".join("Check instance validity:"))
    for instance in semantic_manager.get_all_local_instances():
        print(
            f"({instance.get_type()}, {instance.id}) is valid: "
            f"{instance.is_valid()}"
        )
    print("")

    # if we want to save the LocalState to fiware with an invalid instance
    # an error will be raised.
    # But we maybe want to save the LocalState to continue working later.
    # Here we can save and load the LocalState as json:

    # Saving
    json_save = semantic_manager.save_local_state_as_json()
    # Loading
    # --> semantic_manager.load_local_state_from_json(json_save)
    # Be aware: If we load the local state, our current pointers will not be
    # correct anymore. Loading from json should only be done on a save place
    # where no active scopes are open.

    # We now model the state a bit so that it can be saved
    my_floor.hasRoom.clear()
    my_floor.name.add("Office 201")

    Sensor(id="sensor1").measures.set([MeasurementType.value_Air_Quality])
    Sensor(id="sensor1").unit.add(Unit.value_Relative_Humidity)

    my_outlet.connectedTo.set([Circuit(id="c1"), Room(id="r1")])
    my_outlet.device_settings.endpoint = "http://test.com"
    my_outlet.device_settings.transport = TransportProtocol.MQTT

    Floor(id="second_floor").name.add("Second Floor")

    r1 = Room(id="r1")
    r1.goalTemperature.set(["21"])
    r1.name.add("Room45")
    r1.volume.add(80)
    r1.hasOutlet.add(my_outlet)

    Circuit(id="c1").hasOutlet.add(my_outlet)
    Circuit(id="c1").name.set(["MainCircuit"])
    p1 = Producer(id="p1")
    Circuit(id="c1").hasProducer.add(p1)

    p1.name.add("CHU")
    p1.device_settings.endpoint = "http://test2.com"
    p1.device_settings.transport = TransportProtocol.MQTT

    sensor_instance.delete()

    # Now our state is completely valid and we can save:
    semantic_manager.save_state(assert_validity=True)
    # We could also force an invalid state to be saved, in that case the
    # fulfillment of RuleFields is not checked, but Devices still need an
    # endpoint and transport

    # If we save to Fiware it is tried to merge the changes made locally with
    # the current Fiware state. Each instance that gets loaded from fiware
    # holds it old_state internally on save_state() the old_state gets
    # compared to the current state of the instance and only the changes as
    # saved as small grained as possible

    # The state is merged locally before posting it on Fiware. After
    # .save_state() the values hold inside the local individuals can be
    # changed, as they now hold the same values as the live state on Fiware

    # ## 4.3 Deleting instances
    #
    # to delete an instance, we can simply call:
    my_sensor.delete(assert_no_references=False)

    # The parameter assert_no_references is optional; if true the instance is
    # only deleted if no other instance had a reference to it.
    # If we add an instance i1 into a RelationField f of an instance i2. i1
    # will hold the information that it is referenced in the field f of i2.
    # If we delete an instance, the instances is automatically removed from
    # all fields in other instances that it was referenced in.
    # If we delete i1, the value i1 will be removed from teh field f in i2.
    # If needed i2 is hot-loaded from Fiware
    #
    # The delete is as all other changes only a local change. It gets only
    # transferred to the Fiware state on the call: save_state()

    # # 5. Visualisation
    #
    # ## 5.1 Simple Debug Visualisation
    #
    # To have a fast look at your current local state when working with it,
    # you can call the following methode, and an image will be automatically
    # displayed in your OS default picture viewer.
    semantic_manager.visualize_local_state()
    #
    # ## 5.2 Cytoscape
    #
    # To have an interactive, visually appealing representation of your
    # semantic state, you can use the Library: CYTOSCAPE.
    # Filip can generate you the data needed for a cytoscape visualisation.
    # The visualisation tool itself is not included, but supported for
    # multiple platforms as Jupyter Notebooks or Plotly Dash.
    #
    # ### 5.2.1 Generate Data
    #
    # To generate a representation of the current local state simply call:
    [elements, stylesheet] = semantic_manager.generate_cytoscape_for_local_state(
        display_only_used_individuals=True
    )

    # As a result you receive a Tuple containing the graph elements (nodes,
    # edges) and a stylesheet. (For more details refer to the methode
    # descriptions)
    #
    # ### 5.2.2 Visualise in Jupyter
    #
    # Create the cytoscape graph widget
    """
        import ipycytoscape
        
        cyto = ipycytoscape.CytoscapeWidget()
        cyto.graph.add_graph_from_json(elements)
        cyto.set_style(stylesheet)   
    """
    #
    # Display the graph.
    """
        cyto
    """
    #
    # ### 5.2.3 Visualise in Plotly Dash
    #
    # #### 5.2.3.1 Layout
    """
        import dash_cytoscape as cyto
        ...
        cyto.Cytoscape(
            id='app-cytoscape',
            elements=[],
            layout={'name': 'cola',
                    'edgeLength': 150,
                    },
            style={'width': '100%', 'height': '700px'},
        )
        ...
    """
    # #### 5.2.3.2 Callbacks
    """
    @app.callback(
    Output('app-semantics-bigGraph-cytoscape', 'elements'),
    Output('app-semantics-bigGraph-cytoscape', 'stylesheet'),
    Input(...)
    State(...),
    )
    def my_callback_to_visualise_state(....):
        
        ...
        
        [element_dict, stylesheet] = 
            semantics_manager.generate_cytoscape_for_local_state()
    
        elements = element_dict['nodes'] + element_dict['edges']
    
        return elements, stylesheet
    """
