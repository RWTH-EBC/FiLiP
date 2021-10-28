from enum import Enum
from typing import Dict, Union, List
from filip.semantics.semantic_models import \
	SemanticClass, SemanticIndividual, RelationField, DataField, SemanticDeviceClass, DeviceAttributeField,CommandField
from filip.semantics.semantic_manager import SemanticManager, InstanceRegistry


semantic_manager: SemanticManager = SemanticManager(
	instance_registry=InstanceRegistry(),
)

# ---------CLASSES--------- #


class Thing(SemanticClass):

	def __new__(cls, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class Building(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.goal_temperature._rules = [('exactly|1', [['integer']])]
			self.name._rules = [('exactly|1', [['string']])]

			self.has_floor._rules = [('min|1', [[Floor]])]

			self.has_floor._instance_identifier = self.get_identifier()
			self.goal_temperature._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()

			pass

	# Data fields
	goal_temperature: DataField = DataField(
		name='goal_temperature',
		rule='exactly 1 integer',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	has_floor: RelationField = RelationField(
		name='has_floor',
		rule='min 1 Floor',
		semantic_manager=semantic_manager)


class Circuit(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]

			self.has_outlet._rules = [('min|1', [[Outlet]])]
			self.has_producer._rules = [('min|1', [[Producer]])]

			self.has_outlet._instance_identifier = self.get_identifier()
			self.has_producer._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()

			pass

	# Data fields
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	has_outlet: RelationField = RelationField(
		name='has_outlet',
		rule='min 1 Outlet',
		semantic_manager=semantic_manager)
	has_producer: RelationField = RelationField(
		name='has_producer',
		rule='min 1 Producer',
		semantic_manager=semantic_manager)


class Floor(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]

			self.has_room._rules = [('only', [[Room]])]

			self.has_room._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()

			pass

	# Data fields
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	has_room: RelationField = RelationField(
		name='has_room',
		rule='only Room',
		semantic_manager=semantic_manager)


class Outlet(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.connected_to._rules = [('min|1', [[Circuit]]), ('exactly|1', [[Room]])]

			self.connected_to._instance_identifier = self.get_identifier()
			self.control_command._instance_identifier = self.get_identifier()
			self.state._instance_identifier = self.get_identifier()

			pass

	# Data fields
	control_command: CommandField = CommandField(
		name='control_command',
		semantic_manager=semantic_manager)
	state: DeviceAttributeField = DeviceAttributeField(
		name='state',
		semantic_manager=semantic_manager)

	# Relation fields
	connected_to: RelationField = RelationField(
		name='connected_to',
		rule='min 1 Circuit, exactly 1 Room',
		semantic_manager=semantic_manager)


class Producer(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]


			self.control_command._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()
			self.state._instance_identifier = self.get_identifier()

			pass

	# Data fields
	control_command: CommandField = CommandField(
		name='control_command',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)
	state: DeviceAttributeField = DeviceAttributeField(
		name='state',
		semantic_manager=semantic_manager)

	# Relation fields


class AirProducer(Producer):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]


			self.control_command._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()
			self.state._instance_identifier = self.get_identifier()

			pass

	# Data fields
	control_command: CommandField = CommandField(
		name='control_command',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)
	state: DeviceAttributeField = DeviceAttributeField(
		name='state',
		semantic_manager=semantic_manager)

	# Relation fields


class ColdProducer(Producer):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]


			self.control_command._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()
			self.state._instance_identifier = self.get_identifier()

			pass

	# Data fields
	control_command: CommandField = CommandField(
		name='control_command',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)
	state: DeviceAttributeField = DeviceAttributeField(
		name='state',
		semantic_manager=semantic_manager)

	# Relation fields


class HeatProducer(Producer):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.name._rules = [('exactly|1', [['string']])]


			self.control_command._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()
			self.state._instance_identifier = self.get_identifier()

			pass

	# Data fields
	control_command: CommandField = CommandField(
		name='control_command',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)
	state: DeviceAttributeField = DeviceAttributeField(
		name='state',
		semantic_manager=semantic_manager)

	# Relation fields


class Room(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.goal_temperature._rules = [('exactly|1', [['integer']])]
			self.name._rules = [('exactly|1', [['string']])]
			self.volume._rules = [('some', [['rational']])]

			self.has_outlet._rules = [('only', [[Outlet]])]
			self.has_sensor._rules = [('only', [[Sensor]])]
			self.has_tenant._rules = [('only', [[Tenant]])]

			self.has_outlet._instance_identifier = self.get_identifier()
			self.has_sensor._instance_identifier = self.get_identifier()
			self.has_tenant._instance_identifier = self.get_identifier()
			self.goal_temperature._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()
			self.volume._instance_identifier = self.get_identifier()

			pass

	# Data fields
	goal_temperature: DataField = DataField(
		name='goal_temperature',
		rule='exactly 1 integer',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)
	volume: DataField = DataField(
		name='volume',
		rule='some rational',
		semantic_manager=semantic_manager)

	# Relation fields
	has_outlet: RelationField = RelationField(
		name='has_outlet',
		rule='only Outlet',
		semantic_manager=semantic_manager)
	has_sensor: RelationField = RelationField(
		name='has_sensor',
		rule='only Sensor',
		semantic_manager=semantic_manager)
	has_tenant: RelationField = RelationField(
		name='has_tenant',
		rule='only Tenant',
		semantic_manager=semantic_manager)


class Sensor(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.measures._rules = [('exactly|1', [['MeasurementType']])]
			self.unit._rules = [('exactly|1', [['Unit']])]


			self.measurement._instance_identifier = self.get_identifier()
			self.measures._instance_identifier = self.get_identifier()
			self.unit._instance_identifier = self.get_identifier()

			pass

	# Data fields
	measurement: DeviceAttributeField = DeviceAttributeField(
		name='measurement',
		semantic_manager=semantic_manager)
	measures: DataField = DataField(
		name='measures',
		rule='exactly 1 MeasurementType',
		semantic_manager=semantic_manager)
	unit: DataField = DataField(
		name='unit',
		rule='exactly 1 Unit',
		semantic_manager=semantic_manager)

	# Relation fields


class Tenant(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.goal_temperature._rules = [('exactly|1', [['integer']])]
			self.name._rules = [('exactly|1', [['string']])]


			self.goal_temperature._instance_identifier = self.get_identifier()
			self.name._instance_identifier = self.get_identifier()

			pass

	# Data fields
	goal_temperature: DataField = DataField(
		name='goal_temperature',
		rule='exactly 1 integer',
		semantic_manager=semantic_manager)
	name: DataField = DataField(
		name='name',
		rule='exactly 1 string',
		semantic_manager=semantic_manager)

	# Relation fields


# ---------Individuals--------- #


class ExampleIndividual(SemanticIndividual):
	_parent_classes: List[type] = []





# ---------Datatypes--------- #
semantic_manager.datatype_catalogue = {
	'MeasurementType': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['Air_Quality', 'Temperature'], 'number_has_range': False},
	'Unit': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['Celsius', 'Kelvin', 'Relative_Humidity'], 'number_has_range': False},
	'rational': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'real': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'PlainLiteral': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'XMLLiteral': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'Literal': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'anyURI': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'base64Binary': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'boolean': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['True', 'False'], 'number_has_range': False},
	'byte': 	 {'type': 'number', 'number_range_min': -128, 'number_range_max': 127, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'dateTime': 	 {'type': 'date', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'dateTimeStamp': 	 {'type': 'date', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'decimal': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'double': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'float': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'hexBinary': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'], 'enum_values': [], 'number_has_range': False},
	'int': 	 {'type': 'number', 'number_range_min': -2147483648, 'number_range_max': 2147483647, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'integer': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'language': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'long': 	 {'type': 'number', 'number_range_min': -9223372036854775808, 'number_range_max': 9223372036854775807, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'Name': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'NCName': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [':'], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'negativeInteger': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': -1, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'NMTOKEN': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'nonNegativeInteger': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'nonPositiveInteger': 	 {'type': 'number', 'number_range_min': '/', 'number_range_max': -1, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'normalizedString': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'positiveInteger': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'short': 	 {'type': 'number', 'number_range_min': -32768, 'number_range_max': 32767, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'string': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'token': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'unsignedByte': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': 255, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'unsignedInt': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': 4294967295, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'unsignedLong': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': 18446744073709551615, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
	'unsignedShort': 	 {'type': 'number', 'number_range_min': 0, 'number_range_max': 65535, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True},
}


class MeasurementType(str, Enum):
	value_Air_Quality = 'Air_Quality'
	value_Temperature = 'Temperature'


class Unit(str, Enum):
	value_Celsius = 'Celsius'
	value_Kelvin = 'Kelvin'
	value_Relative_Humidity = 'Relative_Humidity'


# ---------Class Dict--------- #

semantic_manager.class_catalogue = {
	'AirProducer': AirProducer,
	'Building': Building,
	'Circuit': Circuit,
	'ColdProducer': ColdProducer,
	'Floor': Floor,
	'HeatProducer': HeatProducer,
	'Outlet': Outlet,
	'Producer': Producer,
	'Room': Room,
	'Sensor': Sensor,
	'Tenant': Tenant,
	'Thing': Thing,
	}


semantic_manager.individual_catalogue = {
	'ExampleIndividual': ExampleIndividual,
	}
