from typing import Dict, Union, List
from filip.semantics.semantic_models import \
	SemanticClass, SemanticIndividual, RelationField, DataField, SemanticDeviceClass, DeviceAttributeField,CommandField
from filip.semantics.semantic_manager import SemanticManager, InstanceRegistry


semantic_manager: SemanticManager = SemanticManager(
	instance_registry=InstanceRegistry(),
)

# ---------CLASSES--------- #


class Currency(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class EnergyUnit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class IlluminanceUnit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class PowerUnit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class PressureUnit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class TemperatureUnit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


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

			self.has_floor._rules = [('only', [[Floor]])]

			self.has_floor._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_floor: RelationField = RelationField(
		name='has_floor',
		rule='only Floor',
		semantic_manager=semantic_manager)


class Command(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class CloseCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[OpenCloseState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only OpenCloseState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class Commodity(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class Coal(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class Device(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class BuildingRelated(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Electricity(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class EnergyRelated(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Floor(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_room._rules = [('only', [[Room]])]

			self.has_room._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_room: RelationField = RelationField(
		name='has_room',
		rule='only Room',
		semantic_manager=semantic_manager)


class Function(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='min 1 Command',
		semantic_manager=semantic_manager)


class ActuatingFunction(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='min 1 Command',
		semantic_manager=semantic_manager)


class EventFunction(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[NotifyCommand]]), ('min|1', [[Command]])]
			self.has_threshold_measurement._rules = [('min|1', [[Measurement]])]

			self.has_command._instance_identifier = self.get_identifier()
			self.has_threshold_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only NotifyCommand, min 1 Command',
		semantic_manager=semantic_manager)
	has_threshold_measurement: RelationField = RelationField(
		name='has_threshold_measurement',
		rule='min 1 Measurement',
		semantic_manager=semantic_manager)


class FunctionRelated(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Actuator(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[ActuatingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some ActuatingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Appliance(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Gas(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class Generator(EnergyRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class GetCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class GetCurrentMeterValueCommand(GetCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class GetMeterDataCommand(GetCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class GetMeterHistoryCommand(GetCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class GetSensingDataCommand(GetCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class Hvac(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Comfort())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Comfort, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class LevelControlFunction(ActuatingFunction):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[SetAbsoluteLevelCommand], [SetRelativeLevelCommand], [StepDownCommand], [StepUpCommand]]), ('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only (SetAbsoluteLevelCommand or SetRelativeLevelCommand) or StepDownCommand) or StepUpCommand), min 1 Command',
		semantic_manager=semantic_manager)


class LightingDevice(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Comfort())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Comfort, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Load(EnergyRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Measurement(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_timestamp._rules = [('only', [['dateTime']])]

			self.relates_to_property._rules = [('only', [[Property]]), ('exactly|1', [[Property]])]

			self.relates_to_property._instance_identifier = self.get_identifier()
			self.has_timestamp._instance_identifier = self.get_identifier()
			self.has_values_saref._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_timestamp: DataField = DataField(
		name='has_timestamp',
		rule='only dateTime',
		semantic_manager=semantic_manager)
	has_values_saref: DeviceAttributeField = DeviceAttributeField(
		name='has_values_saref',
		semantic_manager=semantic_manager)

	# Relation fields
	relates_to_property: RelationField = RelationField(
		name='relates_to_property',
		rule='only Property, exactly 1 Property',
		semantic_manager=semantic_manager)


class Measurment(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_value._rules = [('exactly|1', [['integer']])]
			self.measures._rules = [('exactly|1', [['measurment_type']])]


			self.has_value._instance_identifier = self.get_identifier()
			self.measures._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_value: DataField = DataField(
		name='has_value',
		rule='exactly 1 integer',
		semantic_manager=semantic_manager)
	measures: DataField = DataField(
		name='measures',
		rule='exactly 1 measurment_type',
		semantic_manager=semantic_manager)

	# Relation fields


class Meter(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[MeteringFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some MeteringFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class EnergyMeter(Meter):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Energyefficiency]]), ('value', [[MeterReading]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('some', [[Meter]]), ('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[MeteringFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('some', [[Energy]]), ('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Energyefficiency())
			self.accomplishes.append(MeterReading())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Energyefficiency, value MeterReading, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='some Meter, only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some MeteringFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='some Energy, only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class MeteringFunction(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[GetCurrentMeterValueCommand], [GetMeterDataCommand], [GetMeterHistoryCommand]]), ('min|1', [[Command]])]
			self.has_meter_reading_type._rules = [('only', [[Commodity], [Property]])]
			self.has_meter_reading._rules = [('only', [[Measurement]])]

			self.has_command._instance_identifier = self.get_identifier()
			self.has_meter_reading_type._instance_identifier = self.get_identifier()
			self.has_meter_reading._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only (GetCurrentMeterValueCommand or GetMeterDataCommand) or GetMeterHistoryCommand), min 1 Command',
		semantic_manager=semantic_manager)
	has_meter_reading_type: RelationField = RelationField(
		name='has_meter_reading_type',
		rule='only (Commodity or Property)',
		semantic_manager=semantic_manager)
	has_meter_reading: RelationField = RelationField(
		name='has_meter_reading',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class MicroRenewable(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Energyefficiency]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Energyefficiency())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Energyefficiency, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Multimedia(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Entertainment]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Entertainment())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Entertainment, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Network(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class NotifyCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class OffCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[OnOffState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only OnOffState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class OnCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[OnOffState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only OnOffState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class OnOffFunction(ActuatingFunction):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[OffCommand], [OnCommand], [ToggleCommand]]), ('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only (OffCommand or OnCommand) or ToggleCommand), min 1 Command',
		semantic_manager=semantic_manager)


class OpenCloseFunction(ActuatingFunction):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[CloseCommand], [OpenCommand]]), ('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only (CloseCommand or OpenCommand), min 1 Command',
		semantic_manager=semantic_manager)


class OpenCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[OpenCloseState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only OpenCloseState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class PauseCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class Profile(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.consists_of._rules = [('only', [[Profile]])]
			self.has_price._rules = [('only', [[Price]])]
			self.has_time._rules = [('only', [[Time]])]
			self.isabout._rules = [('only', [[Commodity], [Property]])]

			self.consists_of._instance_identifier = self.get_identifier()
			self.has_price._instance_identifier = self.get_identifier()
			self.has_time._instance_identifier = self.get_identifier()
			self.isabout._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_price: RelationField = RelationField(
		name='has_price',
		rule='only Price',
		semantic_manager=semantic_manager)
	has_time: RelationField = RelationField(
		name='has_time',
		rule='only Time',
		semantic_manager=semantic_manager)
	isabout: RelationField = RelationField(
		name='isabout',
		rule='only (Commodity or Property)',
		semantic_manager=semantic_manager)


class Property(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Energy(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Humidity(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Light(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Motion(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Occupancy(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Power(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Pressure(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Price(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Room(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_sensor._rules = [('only', [[Sensor]])]
			self.is_on_floor._rules = [('some', [[Floor]])]

			self.has_sensor._instance_identifier = self.get_identifier()
			self.is_on_floor._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_sensor: RelationField = RelationField(
		name='has_sensor',
		rule='only Sensor',
		semantic_manager=semantic_manager)
	is_on_floor: RelationField = RelationField(
		name='is_on_floor',
		rule='some Floor',
		semantic_manager=semantic_manager)


class SarefSensor(FunctionRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[SensingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some SensingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class SensingFunction(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[GetSensingDataCommand]]), ('min|1', [[Command]])]
			self.has_sensing_range._rules = [('some', [[Measurement]])]
			self.has_sensor_type._rules = [('only', [[Property]])]

			self.has_command._instance_identifier = self.get_identifier()
			self.has_sensing_range._instance_identifier = self.get_identifier()
			self.has_sensor_type._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only GetSensingDataCommand, min 1 Command',
		semantic_manager=semantic_manager)
	has_sensing_range: RelationField = RelationField(
		name='has_sensing_range',
		rule='some Measurement',
		semantic_manager=semantic_manager)
	has_sensor_type: RelationField = RelationField(
		name='has_sensor_type',
		rule='only Property',
		semantic_manager=semantic_manager)


class Sensor(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.makes_measurment._rules = [('some', [[Measurment]])]

			self.makes_measurment._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	makes_measurment: RelationField = RelationField(
		name='makes_measurment',
		rule='some Measurment',
		semantic_manager=semantic_manager)


class Service(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_offered_by._rules = [('min|1', [[Device]])]
			self.represents._rules = [('min|1', [[Function]])]

			self.is_offered_by._instance_identifier = self.get_identifier()
			self.represents._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_offered_by: RelationField = RelationField(
		name='is_offered_by',
		rule='min 1 Device',
		semantic_manager=semantic_manager)
	represents: RelationField = RelationField(
		name='represents',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class SetLevelCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[MultiLevelState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only MultiLevelState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class SetAbsoluteLevelCommand(SetLevelCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[MultiLevelState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only MultiLevelState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class SetRelativeLevelCommand(SetLevelCommand):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[MultiLevelState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only MultiLevelState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class Smoke(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class SmokeSensor(SarefSensor):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Safety]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('some', [[SarefSensor]]), ('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[EventFunction]]), ('some', [[SensingFunction]]), ('some', [[SensingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('some', [[Smoke]]), ('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Safety())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Safety, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='some SarefSensor, only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some EventFunction, some SensingFunction, some SensingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='some Smoke, only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class StartCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[StartStopState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only StartStopState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class StartStopFunction(ActuatingFunction):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.has_command._rules = [('only', [[StartCommand], [StopCommand]]), ('min|1', [[Command]])]

			self.has_command._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	has_command: RelationField = RelationField(
		name='has_command',
		rule='only (StartCommand or StopCommand), min 1 Command',
		semantic_manager=semantic_manager)


class State(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class MultiLevelState(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class OnOffState(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class OffState(OnOffState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class OnState(OnOffState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class OpenCloseState(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class CloseState(OpenCloseState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class OpenState(OpenCloseState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class StartStopState(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class StartState(StartStopState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class StepDownCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[MultiLevelState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only MultiLevelState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class StepUpCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[MultiLevelState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only MultiLevelState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class StopCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[StartStopState]]), ('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only StartStopState, only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class StopState(StartStopState):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


class Storage(EnergyRelated):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Switch(Actuator):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[ActuatingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some ActuatingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class DoorSwitch(Switch):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Safety]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('some', [[Switch]]), ('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[OpenCloseFunction]]), ('some', [[ActuatingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('some', [[OpenCloseState]]), ('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Safety())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Safety, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='some Switch, only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some OpenCloseFunction, some ActuatingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='some OpenCloseState, only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class LightSwitch(Switch):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Lighting]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('some', [[Switch]]), ('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[OnOffFunction]]), ('some', [[ActuatingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('some', [[OnOffState]]), ('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('some', [[Light]]), ('only', [[Property]])]
			self.offers._rules = [('some', [[SwitchOnService]]), ('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Lighting())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Lighting, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='some Switch, only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some OnOffFunction, some ActuatingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='some OnOffState, only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='some Light, only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='some SwitchOnService, only Service',
		semantic_manager=semantic_manager)


class SwitchOnService(Service):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_offered_by._rules = [('some', [[LightSwitch]]), ('min|1', [[Device]])]
			self.represents._rules = [('some', [[OnOffFunction]]), ('min|1', [[Function]])]

			self.is_offered_by._instance_identifier = self.get_identifier()
			self.represents._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_offered_by: RelationField = RelationField(
		name='is_offered_by',
		rule='some LightSwitch, min 1 Device',
		semantic_manager=semantic_manager)
	represents: RelationField = RelationField(
		name='represents',
		rule='some OnOffFunction, min 1 Function',
		semantic_manager=semantic_manager)


class Task(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_accomplished_by._rules = [('min|1', [[Device]])]

			self.is_accomplished_by._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_accomplished_by: RelationField = RelationField(
		name='is_accomplished_by',
		rule='min 1 Device',
		semantic_manager=semantic_manager)


class Temperature(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class TemperatureSensor(SarefSensor):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('some', [[SarefSensor]]), ('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[SensingFunction]]), ('some', [[SensingFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('only', [[Profile]])]
			self.has_state._rules = [('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('some', [[Temperature]]), ('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Comfort())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Comfort, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='some SarefSensor, only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some SensingFunction, some SensingFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='some Temperature, only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Time(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.is_controlled_by_device._rules = [('only', [[Device]])]
			self.is_measured_by_device._rules = [('only', [[Device]])]
			self.relates_to_measurement._rules = [('only', [[Measurement]])]

			self.is_controlled_by_device._instance_identifier = self.get_identifier()
			self.is_measured_by_device._instance_identifier = self.get_identifier()
			self.relates_to_measurement._instance_identifier = self.get_identifier()

			pass

	# Data fields

	# Relation fields
	is_controlled_by_device: RelationField = RelationField(
		name='is_controlled_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	is_measured_by_device: RelationField = RelationField(
		name='is_measured_by_device',
		rule='only Device',
		semantic_manager=semantic_manager)
	relates_to_measurement: RelationField = RelationField(
		name='relates_to_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class ToggleCommand(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]

			self.acts_upon._rules = [('only', [[State]])]
			self.is_command_of._rules = [('min|1', [[Function]])]

			self.acts_upon._instance_identifier = self.get_identifier()
			self.is_command_of._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()

			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	acts_upon: RelationField = RelationField(
		name='acts_upon',
		rule='only State',
		semantic_manager=semantic_manager)
	is_command_of: RelationField = RelationField(
		name='is_command_of',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class WashingMachine(Appliance, Load):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.has_description._rules = [('max|1', [['string']])]
			self.has_manufacturer._rules = [('max|1', [['string']])]

			self.accomplishes._rules = [('value', [[Washing]]), ('min|1', [[Task]])]
			self.consists_of._rules = [('only', [[Device]])]
			self.controls_property._rules = [('only', [[Property]])]
			self.has_function._rules = [('some', [[StartStopFunction]]), ('min|1', [[Function]])]
			self.has_profile._rules = [('some', [[Profile]]), ('only', [[Profile]])]
			self.has_state._rules = [('some', [[StartStopState]]), ('only', [[State]])]
			self.has_typical_consumption._rules = [('only', [[Energy], [Power]])]
			self.is_used_for._rules = [('only', [[Commodity]])]
			self.makes_measurement._rules = [('only', [[Measurement]])]
			self.measures_property._rules = [('only', [[Property]])]
			self.offers._rules = [('only', [[Service]])]

			self.accomplishes._instance_identifier = self.get_identifier()
			self.consists_of._instance_identifier = self.get_identifier()
			self.controls_property._instance_identifier = self.get_identifier()
			self.has_function._instance_identifier = self.get_identifier()
			self.has_profile._instance_identifier = self.get_identifier()
			self.has_state._instance_identifier = self.get_identifier()
			self.has_typical_consumption._instance_identifier = self.get_identifier()
			self.is_used_for._instance_identifier = self.get_identifier()
			self.makes_measurement._instance_identifier = self.get_identifier()
			self.measures_property._instance_identifier = self.get_identifier()
			self.offers._instance_identifier = self.get_identifier()
			self.has_description._instance_identifier = self.get_identifier()
			self.has_manufacturer._instance_identifier = self.get_identifier()
			self.has_model._instance_identifier = self.get_identifier()

			self.accomplishes.append(Washing())
			pass

	# Data fields
	has_description: DataField = DataField(
		name='has_description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_manufacturer: DataField = DataField(
		name='has_manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	has_model: CommandField = CommandField(
		name='has_model',
		semantic_manager=semantic_manager)

	# Relation fields
	accomplishes: RelationField = RelationField(
		name='accomplishes',
		rule='value Washing, min 1 Task',
		semantic_manager=semantic_manager)
	consists_of: RelationField = RelationField(
		name='consists_of',
		rule='only Device',
		semantic_manager=semantic_manager)
	controls_property: RelationField = RelationField(
		name='controls_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	has_function: RelationField = RelationField(
		name='has_function',
		rule='some StartStopFunction, min 1 Function',
		semantic_manager=semantic_manager)
	has_profile: RelationField = RelationField(
		name='has_profile',
		rule='some Profile, only Profile',
		semantic_manager=semantic_manager)
	has_state: RelationField = RelationField(
		name='has_state',
		rule='some StartStopState, only State',
		semantic_manager=semantic_manager)
	has_typical_consumption: RelationField = RelationField(
		name='has_typical_consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	is_used_for: RelationField = RelationField(
		name='is_used_for',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	makes_measurement: RelationField = RelationField(
		name='makes_measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	measures_property: RelationField = RelationField(
		name='measures_property',
		rule='only Property',
		semantic_manager=semantic_manager)
	offers: RelationField = RelationField(
		name='offers',
		rule='only Service',
		semantic_manager=semantic_manager)


class Water(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:



			pass

	# Data fields

	# Relation fields


# ---------Individuals--------- #


class UnitedStatesDollar(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Bar(SemanticIndividual):
	_parent_classes: List[type] = [PressureUnit]


class DegreeCelsius(SemanticIndividual):
	_parent_classes: List[type] = [TemperatureUnit]


class DegreeFahrenheit(SemanticIndividual):
	_parent_classes: List[type] = [TemperatureUnit]


class Euro(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Kelvin(SemanticIndividual):
	_parent_classes: List[type] = [TemperatureUnit]


class Kilowatt(SemanticIndividual):
	_parent_classes: List[type] = [PowerUnit]


class KilowattHour(SemanticIndividual):
	_parent_classes: List[type] = [EnergyUnit]


class Lux(SemanticIndividual):
	_parent_classes: List[type] = [IlluminanceUnit]


class Pascal(SemanticIndividual):
	_parent_classes: List[type] = [PressureUnit]


class GreatBritainPoundSterling(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Watt(SemanticIndividual):
	_parent_classes: List[type] = [PowerUnit]


class Cleaning(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Close(SemanticIndividual):
	_parent_classes: List[type] = [CloseCommand, CloseState]


class Comfort(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Drying(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Energyefficiency(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Entertainment(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class GetCurrentMeterValue(SemanticIndividual):
	_parent_classes: List[type] = [GetCurrentMeterValueCommand]


class GetMeterData(SemanticIndividual):
	_parent_classes: List[type] = [GetMeterDataCommand]


class GetMeterHistory(SemanticIndividual):
	_parent_classes: List[type] = [GetMeterHistoryCommand]


class GetSensingData(SemanticIndividual):
	_parent_classes: List[type] = [GetSensingDataCommand]


class Lighting(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class MeterReading(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Notify(SemanticIndividual):
	_parent_classes: List[type] = [NotifyCommand]


class Off(SemanticIndividual):
	_parent_classes: List[type] = [OffCommand, OffState]


class On(SemanticIndividual):
	_parent_classes: List[type] = [OnCommand, OnState]


class Open(SemanticIndividual):
	_parent_classes: List[type] = [OpenCommand, OpenState]


class Pause(SemanticIndividual):
	_parent_classes: List[type] = [PauseCommand]


class Safety(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class SetAbsoluteLevel(SemanticIndividual):
	_parent_classes: List[type] = [SetAbsoluteLevelCommand]


class SetRelativeLevel(SemanticIndividual):
	_parent_classes: List[type] = [SetRelativeLevelCommand]


class Start(SemanticIndividual):
	_parent_classes: List[type] = [StartCommand, StartState]


class StepDown(SemanticIndividual):
	_parent_classes: List[type] = [StepDownCommand]


class StepUp(SemanticIndividual):
	_parent_classes: List[type] = [StepUpCommand]


class Stop(SemanticIndividual):
	_parent_classes: List[type] = [StopCommand, StopState]


class Toggle(SemanticIndividual):
	_parent_classes: List[type] = [ToggleCommand]


class Washing(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Wellbeing(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class WattHour(SemanticIndividual):
	_parent_classes: List[type] = [EnergyUnit]





# ---------Datatypes--------- #
semantic_manager.datatype_catalogue = {
	'measurment_type': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['Humidity', 'Temp'], 'number_has_range': False},
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

semantic_manager.class_catalogue = {
	'ActuatingFunction': ActuatingFunction,
	'Actuator': Actuator,
	'Appliance': Appliance,
	'Building': Building,
	'BuildingRelated': BuildingRelated,
	'CloseCommand': CloseCommand,
	'CloseState': CloseState,
	'Coal': Coal,
	'Command': Command,
	'Commodity': Commodity,
	'Currency': Currency,
	'Device': Device,
	'DoorSwitch': DoorSwitch,
	'Electricity': Electricity,
	'Energy': Energy,
	'EnergyMeter': EnergyMeter,
	'EnergyRelated': EnergyRelated,
	'EnergyUnit': EnergyUnit,
	'EventFunction': EventFunction,
	'Floor': Floor,
	'Function': Function,
	'FunctionRelated': FunctionRelated,
	'Gas': Gas,
	'Generator': Generator,
	'GetCommand': GetCommand,
	'GetCurrentMeterValueCommand': GetCurrentMeterValueCommand,
	'GetMeterDataCommand': GetMeterDataCommand,
	'GetMeterHistoryCommand': GetMeterHistoryCommand,
	'GetSensingDataCommand': GetSensingDataCommand,
	'Humidity': Humidity,
	'Hvac': Hvac,
	'IlluminanceUnit': IlluminanceUnit,
	'LevelControlFunction': LevelControlFunction,
	'Light': Light,
	'LightSwitch': LightSwitch,
	'LightingDevice': LightingDevice,
	'Load': Load,
	'Measurement': Measurement,
	'Measurment': Measurment,
	'Meter': Meter,
	'MeteringFunction': MeteringFunction,
	'MicroRenewable': MicroRenewable,
	'Motion': Motion,
	'MultiLevelState': MultiLevelState,
	'Multimedia': Multimedia,
	'Network': Network,
	'NotifyCommand': NotifyCommand,
	'Occupancy': Occupancy,
	'OffCommand': OffCommand,
	'OffState': OffState,
	'OnCommand': OnCommand,
	'OnOffFunction': OnOffFunction,
	'OnOffState': OnOffState,
	'OnState': OnState,
	'OpenCloseFunction': OpenCloseFunction,
	'OpenCloseState': OpenCloseState,
	'OpenCommand': OpenCommand,
	'OpenState': OpenState,
	'PauseCommand': PauseCommand,
	'Power': Power,
	'PowerUnit': PowerUnit,
	'Pressure': Pressure,
	'PressureUnit': PressureUnit,
	'Price': Price,
	'Profile': Profile,
	'Property': Property,
	'Room': Room,
	'SarefSensor': SarefSensor,
	'SensingFunction': SensingFunction,
	'Sensor': Sensor,
	'Service': Service,
	'SetAbsoluteLevelCommand': SetAbsoluteLevelCommand,
	'SetLevelCommand': SetLevelCommand,
	'SetRelativeLevelCommand': SetRelativeLevelCommand,
	'Smoke': Smoke,
	'SmokeSensor': SmokeSensor,
	'StartCommand': StartCommand,
	'StartState': StartState,
	'StartStopFunction': StartStopFunction,
	'StartStopState': StartStopState,
	'State': State,
	'StepDownCommand': StepDownCommand,
	'StepUpCommand': StepUpCommand,
	'StopCommand': StopCommand,
	'StopState': StopState,
	'Storage': Storage,
	'Switch': Switch,
	'SwitchOnService': SwitchOnService,
	'Task': Task,
	'Temperature': Temperature,
	'TemperatureSensor': TemperatureSensor,
	'TemperatureUnit': TemperatureUnit,
	'Thing': Thing,
	'Time': Time,
	'ToggleCommand': ToggleCommand,
	'WashingMachine': WashingMachine,
	'Water': Water,
	}


semantic_manager.individual_catalogue = {
	'UnitedStatesDollar': UnitedStatesDollar,
	'Bar': Bar,
	'DegreeCelsius': DegreeCelsius,
	'DegreeFahrenheit': DegreeFahrenheit,
	'Euro': Euro,
	'Kelvin': Kelvin,
	'Kilowatt': Kilowatt,
	'KilowattHour': KilowattHour,
	'Lux': Lux,
	'Pascal': Pascal,
	'GreatBritainPoundSterling': GreatBritainPoundSterling,
	'Watt': Watt,
	'Cleaning': Cleaning,
	'Close': Close,
	'Comfort': Comfort,
	'Drying': Drying,
	'Energyefficiency': Energyefficiency,
	'Entertainment': Entertainment,
	'GetCurrentMeterValue': GetCurrentMeterValue,
	'GetMeterData': GetMeterData,
	'GetMeterHistory': GetMeterHistory,
	'GetSensingData': GetSensingData,
	'Lighting': Lighting,
	'MeterReading': MeterReading,
	'Notify': Notify,
	'Off': Off,
	'On': On,
	'Open': Open,
	'Pause': Pause,
	'Safety': Safety,
	'SetAbsoluteLevel': SetAbsoluteLevel,
	'SetRelativeLevel': SetRelativeLevel,
	'Start': Start,
	'StepDown': StepDown,
	'StepUp': StepUp,
	'Stop': Stop,
	'Toggle': Toggle,
	'Washing': Washing,
	'Wellbeing': Wellbeing,
	'WattHour': WattHour,
	}
