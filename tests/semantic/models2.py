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


class Class1(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()
			self.dataProp2.add(2)

			self.objProp5.add(Individual1())

	# Data fields
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class1a(Class1):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class1aa(Class1a):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class1b(Class1):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('some', [[Class2]]), ('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some Class2, some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class2(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.oProp1._rules = [('min|1', [[Class1]])]
			self.objProp2._rules = [('only', [[Thing]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='min 1 Class1',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='only Thing',
		semantic_manager=semantic_manager)


class Class3(SemanticDeviceClass, Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp1._rules = [('only', [['customDataType4']])]

			self.oProp1._rules = [('value', [[Individual1]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()

			self.oProp1.add(Individual1())
			self.objProp2.add(Individual1())

	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	commandProp: CommandField = CommandField(
		name='commandProp',
		semantic_manager=semantic_manager)
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class123(Class1, Class2, Class3):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp1._rules = [('only', [['customDataType4']])]
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('value', [[Individual1]]), ('min|1', [[Class1]]), ('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]]), ('only', [[Thing]]), ('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	commandProp: CommandField = CommandField(
		name='commandProp',
		semantic_manager=semantic_manager)
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1, min 1 Class1, some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1, only Thing, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class13(Class1, Class3):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp1._rules = [('min|1', [['int']]), ('only', [['customDataType4']])]
			self.dataProp2._rules = [('exactly|1', [['boolean']]), ('value', [[]])]

			self.oProp1._rules = [('value', [[Individual1]]), ('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]]), ('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	commandProp: CommandField = CommandField(
		name='commandProp',
		semantic_manager=semantic_manager)
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='min 1 int, only customDataType4',
		semantic_manager=semantic_manager)
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='exactly 1 boolean, value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1, some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


class Class3a(Class3):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp1._rules = [('only', [['customDataType4']])]

			self.oProp1._rules = [('value', [[Individual1]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	commandProp: CommandField = CommandField(
		name='commandProp',
		semantic_manager=semantic_manager)
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class3aa(Class3a):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp1._rules = [('only', [['customDataType4']])]

			self.oProp1._rules = [('value', [[Individual1]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	commandProp: CommandField = CommandField(
		name='commandProp',
		semantic_manager=semantic_manager)
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class4(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.objProp4._rules = [('min|1', [[Class1]])]

			self.objProp4._instance_identifier = self.get_identifier()


	# Relation fields
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='min 1 Class1',
		semantic_manager=semantic_manager)


class Gertrude(Class1, Class2):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.dataProp2._rules = [('value', [[]])]

			self.oProp1._rules = [('min|1', [[Class1]]), ('some', [[Class2], [Class4]])]
			self.objProp2._rules = [('only', [[Thing]]), ('some', [[Class1, Class2]])]
			self.objProp3._rules = [('some', [[Class3]])]
			self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
			self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.objProp3._instance_identifier = self.get_identifier()
			self.objProp4._instance_identifier = self.get_identifier()
			self.objProp5._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.dataProp2._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DeviceAttributeField = DeviceAttributeField(
		name='attributeProp',
		semantic_manager=semantic_manager)
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='value 2',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='min 1 Class1, some (Class2 or Class4)',
		inverse_of=['objProp3'],
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='only Thing, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		inverse_of=['oProp1'],
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3)), value Individual1',
		semantic_manager=semantic_manager)


# ---------Individuals--------- #


class Individual1(SemanticIndividual):
	_parent_classes: List[type] = [Class2, Class1]


class Individual2(SemanticIndividual):
	_parent_classes: List[type] = [Class1]


class Individual3(SemanticIndividual):
	_parent_classes: List[type] = [Class2, Class1, Class3]


class Individual4(SemanticIndividual):
	_parent_classes: List[type] = [Class1, Class2]


# ---------Datatypes--------- #
semantic_manager.datatype_catalogue = {
	'customDataType1': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['0', '15', '30'], 'number_has_range': False},
	'customDataType2': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'customDataType3': 	 {'type': 'string', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False},
	'customDataType4': 	 {'type': 'enum', 'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['1', '2', '3', '4'], 'number_has_range': False},
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


class customDataType1(str, Enum):
	value_0 = '0'
	value_15 = '15'
	value_30 = '30'


class customDataType4(str, Enum):
	value_1 = '1'
	value_2 = '2'
	value_3 = '3'
	value_4 = '4'


# ---------Class Dict--------- #

semantic_manager.class_catalogue = {
	'Class1': Class1,
	'Class123': Class123,
	'Class13': Class13,
	'Class1a': Class1a,
	'Class1aa': Class1aa,
	'Class1b': Class1b,
	'Class2': Class2,
	'Class3': Class3,
	'Class3a': Class3a,
	'Class3aa': Class3aa,
	'Class4': Class4,
	'Gertrude': Gertrude,
	'Thing': Thing,
	}


semantic_manager.individual_catalogue = {
	'Individual1': Individual1,
	'Individual2': Individual2,
	'Individual3': Individual3,
	'Individual4': Individual4,
	}
