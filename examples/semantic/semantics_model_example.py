"""
Examples for modelling a real world state with a generated vocabulary model
The model will be imported, classes and devices created, given values,
and check if they are valid.
The whole modeling state is then saved at once to fiware.
Following the fiware state will be edited with automatic partial loading
"""



"""
To run this example you need a working Fiware v2 setup with a context-broker 
and an iota-broker. You can here set the addresses:
"""
cb_url = "http://localhost:1026"
iota_url = "http://localhost:4041"

if __name__ == '__main__':

    # 1. First we need to import the models that we have created in the
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

    # 2. The classes (with exception of semantic_manager) are either
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
    #               -   fiware_version: States if Fiware v2 or LD is used
    #               -   service: multi-tenancy space used in Fiware
    #               -   service-path: subpath in the multi-tenancy
    #
    # More details about the uniqueness later

    # 2.1 We can create an instance of a class by simply instantiating and
    # passing the id and header as parameters.
    from filip.semantics.semantic_models import InstanceHeader
    from filip.models.base import NgsiVersion

    header = InstanceHeader(cb_url=cb_url,
                            iota_url=iota_url,
                            fiware_version=NgsiVersion.v2,
                            service="example",
                            service_path="/")

    my_floor = Floor(id="my-first-floor", header=header)

    # If we work with the often with the same header we can also set a
    # default header in the semantic_manager. If a class without a header
    # parameter is created it gets automatically assigned this default header.

    semantic_manager.set_default_header(header)
    my_building = Building(id="building1")

    # 2.2 These defining information of an instance are immutable and can not
    # be changed after the creation.
    # They are further bundled into an identifier object that is used as an
    # identity by the system: The InstanceIdentifier

    # We can have a look at this identifier, and see that the header was
    # correctly set:
    print("\u0332".join("Instance Identifier of my_building:"))
    print(my_building.get_identifier())
    print("")

    # 2.3 Device-classes are a subtype of normal classes, they work as normal
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

    # 3. Our classes possess fields that we use to model the state. There are
    # multiple types of fields a normal-class or device-class can have.
    # Basically a field is a list to which values can be added, but that posses
    # additional functions and internal logic.

    # To view all fields a class possesses we can either:
    #   - try the autocompletion hint when typing building.
    #   - look inside the modules file
    #   - use the functions: .get
    print("\u0332".join("All fields of the Building class:"))
    print(my_building.get_all_field_names())
    print("")

    # To manipulate data inside a field all standard list interactions are
    # given:
    my_building.goal_temperature.append(23)
    my_building.goal_temperature[0] = 12
    del my_building.goal_temperature[0]

    # 3.1 RuleFields: Contains 1 or multiple rules that need to be fulfilled
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

    # 3.1.1 DataFields: Each ComplexDataProperty in our vocabulary with the
    # type "simple" was converted to this field type. (All for normal classes)
    # As values it takes basic types as string, int, bool,..

    my_building.goal_temperature.append(23)
    my_building.name.append("Main Building")

    # we can check again if all DataFields are now valid:
    print("\u0332".join("DataFields of my_building:"))
    for field in my_building.get_data_fields():
        print(f"Name: {field.name}, Rule: {field.rule}, Values: "
              f"{field.get_all_raw()}, Valid: {field.is_valid()}")
    print("")

    # Datafields can also specify rules with Datatype enums, in that case we
    # can either directly add the string, or use the enum of the model
    # In each case only the string value gets saved without enum information
    sensor = Sensor(id="sensor1")
    sensor.measures.append(MeasurementType.Air_Quality)
    sensor.measures.append("Air_Quality")
    print("\u0332".join("DataFields with enum values:"))
    print(f"Raw Values: {sensor.measures.get_all_raw()}")
    print(f"Values: {sensor.measures.get_all()}")
    print("")


    # 3.1.1 RelationFields: Each ComplexRelationProperty in our vocabulary was
    # converted to this field type.
    # As values it takes instances of classes

    my_building.has_floor.append(my_floor)
    my_building.has_floor.append(Floor(id="second_floor"))

    # we can check again if all RelationFields are now valid:
    print("\u0332".join("RelationFields of my_building:"))
    for field in my_building.get_relation_fields():
        print(f"Name: {field.name}, Rule: {field.rule}, Values: "
              f"{field.get_all_raw()}, Valid: {field.is_valid()}")
    print("")

    # As we can see the RelationField internally only saves the references to
    # the instances that he was given as values.
    # But we can access the instances comfortably:

    one_instance = my_building.has_floor[0]
    all_instances = my_building.has_floor.get_all()

    # we added my_floor as first value into has_floor, therefore one_instance
    # now points to exactly the same object as my_floor

    # as the value inside the has_floor field is dynamicaly set, we can not
    # use type hints when working with it. But if we assign a value and then
    # inspect my_floor we see that they are correctly linked.

    one_instance.has_room.append(Room(id="r1"))
    print("\u0332".join("Inspect my_floor.has_room:"))
    print(my_floor.has_room)
    print("")

    # A relation field can also take Individuals as values, or even require
    # them via rules. Instances are globally static, final  classes,
    # each instance of an Individual is equal

    my_floor.has_room.append(ExampleIndividual())

    # An individual is not saved as Identifier as it is not directly saved in
    # Fiware instead it is only saved as string, as a
    # kind of enum.

    print("\u0332".join("Individual internal saving:"))
    for field in my_building.get_relation_fields():
        print(my_floor.has_room.get_all_raw())
    print("")

    # 3.2 DeviceFields. Each ComplexDataProperty in our vocabulary with a
    # type other than "simple" was converted to this field type. Only device
    # classes posses fields of this type.

    # 3.2.1 DeviceAttributeField (type="device_attribute").
    # This field allows us to link directly to properties of the iot device
    # and read them in.

    # In a DeviceAttributeField can therefore multiple DeviceAttributes be
    # added.
    # A DeviceAttribute has two properties:
    # - name: The internal name that the specific device uses for this property
    # - attribute_type: if the value should be lazy or actively read by fiware

    # Our sensor has one measurement property that he names internally m
    # We add this attribute to our measurement_field.

    from filip.semantics.semantic_models import \
        DeviceAttribute, DeviceAttributeType
    my_sensor.measurement.append(
        DeviceAttribute(name="m", attribute_type=DeviceAttributeType.active))

    # To access the value of the attribute we could call:
    # my_sensor.measurement[0].get_value()
    # But only after we saved this state to Fiware, so that the attribute is
    # present. (More to this later)

    # 3.2.2 CommandField (type="command").
    # This field allows us to directly control the linked IoT device by
    # sending commands.

    # To do this we need to add Commands to the CommandField.
    # A command has 1 property:
    # - name: The internal name that the specific device uses for this purpose
    from filip.semantics.semantic_models import Command
    c1 = Command(name="open")
    my_outlet.control_command.append(c1)

    # After the current state was saved. We can interact with the command. It
    # offers three functions:
    # - c1.send(): Send the command to the device to execute it
    # - c1.get_info(): View the result of the executed command
    # - c1.get_status(): See the current status of the sent command

    # 4. We now have seen how the models can be instantiated, filled with
    # values and used to interact with iot-devices.
    # We will now see how the state is managed and how it can be saved and
    # loaded.

    # The library works in two state layers everything we create, load and
    # change is governed in the LocalState. Only if we save the state and the
    # state is valid all made changes will be transferred to the FiwareState.

    # 4.1 Creating/Loading
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
        entity_ids=[], # list of ids to load
        # or entity_types=[...],  # list of types to load
    )

    # 4.2 Saving the Local State

    # If we have finished editing in the local state we can publish our
    # changes to the Fiware State.
    # Before we can do that all instances in the local state need to be valid.

    # We can check this for each instance by calling:
    print("\u0332".join("Check instance validity:"))
    for instance in semantic_manager.get_all_local_instances():
        print(f'({instance.get_type()}, {instance.id}) is valid: '
              f'{instance.is_valid()}')
    print("")

    # if we want to save the LocalState to fiware with an invalid instance
    # an error will be raised.
    # But we maybe want to save the LocalState to continue working later.
    # Here we can save and load the LocalState as json:

    # Saving
    json_save = semantic_manager.save_local_state_as_json()
    # Loading
    # Be aware: If we load the local state, our current pointers will not be
    # correct anymore. Loading from json should only be done on a save place
    # where no active scopes are open.
    # semantic_manager.load_local_state_from_json(json_save)

    # We now model the state a bit so that it can be saved
    del my_floor.has_room[1]
    my_floor.name.append("Office 201")

    Sensor(id="sensor1").measures.append(MeasurementType.Air_Quality)

    from filip.semantics.semantic_models import RuleField
    inst = Sensor(id="sensor1")
    print("\u0332".join(f"Inspect field validity of instance {inst.id}:"))
    for field in inst.get_fields():
        print(f'{field.name}')
        print(f'\t Valid: {field.is_valid()}')
        if(isinstance(field, RuleField)):
             print(f'\t rule: {field.rule}')
        print(f'\t values:{field.get_all_raw()}')

    print("")

    # We can check this for each instance by calling:
    print("\u0332".join("Check instance validity:"))
    for instance in semantic_manager.get_all_local_instances():
        print(f'({instance.get_type()}, {instance.id}) is valid: '
              f'{instance.is_valid()}')

    print("")

    print(my_floor.is_valid())
