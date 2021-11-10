from enum import Enum
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


class Energy_Unit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Illuminance_Unit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Power_Unit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Pressure_Unit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Temperature_Unit(SemanticClass):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


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


class Class2(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.attributeProp._rules = [('some', [['customDataType1']])]

			self.oProp1._rules = [('min|1', [[Class1]])]
			self.objProp2._rules = [('only', [[Thing]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some customDataType1',
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


class Class3(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.attributeProp._rules = [('some', [['string']])]
			self.commandProp._rules = [('some', [['string']])]
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
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some string',
		semantic_manager=semantic_manager)
	commandProp: DataField = DataField(
		name='commandProp',
		rule='some string',
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
			self.attributeProp._rules = [('some', [['string']]), ('some', [['customDataType1']])]
			self.commandProp._rules = [('some', [['string']])]
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
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some string, some customDataType1',
		semantic_manager=semantic_manager)
	commandProp: DataField = DataField(
		name='commandProp',
		rule='some string',
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
			self.attributeProp._rules = [('some', [['string']])]
			self.commandProp._rules = [('some', [['string']])]
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
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some string',
		semantic_manager=semantic_manager)
	commandProp: DataField = DataField(
		name='commandProp',
		rule='some string',
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
			self.attributeProp._rules = [('some', [['string']])]
			self.commandProp._rules = [('some', [['string']])]
			self.dataProp1._rules = [('only', [['customDataType4']])]

			self.oProp1._rules = [('value', [[Individual1]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some string',
		semantic_manager=semantic_manager)
	commandProp: DataField = DataField(
		name='commandProp',
		rule='some string',
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
			self.attributeProp._rules = [('some', [['string']])]
			self.commandProp._rules = [('some', [['string']])]
			self.dataProp1._rules = [('only', [['customDataType4']])]

			self.oProp1._rules = [('value', [[Individual1]])]
			self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

			self.oProp1._instance_identifier = self.get_identifier()
			self.objProp2._instance_identifier = self.get_identifier()
			self.attributeProp._instance_identifier = self.get_identifier()
			self.commandProp._instance_identifier = self.get_identifier()
			self.dataProp1._instance_identifier = self.get_identifier()


	# Data fields
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some string',
		semantic_manager=semantic_manager)
	commandProp: DataField = DataField(
		name='commandProp',
		rule='some string',
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


class Command(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Close_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Open_Close_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Open_Close_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Commodity(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Coal(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Device(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Building_Related(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Electricity(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Energy_Related(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Function(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class Actuating_Function(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class Event_Function(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Notify_Command]]), ('min|1', [[Command]])]
			self.Has_Threshold_Measurement._rules = [('min|1', [[Measurement]])]

			self.Has_Command._instance_identifier = self.get_identifier()
			self.Has_Threshold_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only Notify_Command, min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)
	Has_Threshold_Measurement: RelationField = RelationField(
		name='Has_Threshold_Measurement',
		rule='min 1 Measurement',
		semantic_manager=semantic_manager)


class Function_Related(Device):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Actuator(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Actuating_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Actuating_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Appliance(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Gas(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Generator(Energy_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Gertrude(Class1, Class2):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.attributeProp._rules = [('some', [['customDataType1']])]
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
	attributeProp: DataField = DataField(
		name='attributeProp',
		rule='some customDataType1',
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


class Get_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Get_Current_Meter_Value_Command(Get_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Get_Meter_Data_Command(Get_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Get_Meter_History_Command(Get_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Get_Sensing_Data_Command(Get_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Hvac(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Comfort())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Comfort, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Level_Control_Function(Actuating_Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Set_Absolute_Level_Command], [Set_Relative_Level_Command], [Step_Down_Command], [Step_Up_Command]]), ('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only (Set_Absolute_Level_Command or Set_Relative_Level_Command) or Step_Down_Command) or Step_Up_Command), min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class Lighting_Device(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Comfort())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Comfort, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Load(Energy_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Measurement(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Timestamp._rules = [('only', [['dateTime']])]
			self.Has_Value._rules = [('exactly|1', [['float']])]

			self.Relates_To_Property._rules = [('only', [[Property]]), ('exactly|1', [[Property]])]

			self.Relates_To_Property._instance_identifier = self.get_identifier()
			self.Has_Timestamp._instance_identifier = self.get_identifier()
			self.Has_Value._instance_identifier = self.get_identifier()


	# Data fields
	Has_Timestamp: DataField = DataField(
		name='Has_Timestamp',
		rule='only dateTime',
		semantic_manager=semantic_manager)
	Has_Value: DataField = DataField(
		name='Has_Value',
		rule='exactly 1 float',
		semantic_manager=semantic_manager)

	# Relation fields
	Relates_To_Property: RelationField = RelationField(
		name='Relates_To_Property',
		rule='only Property, exactly 1 Property',
		semantic_manager=semantic_manager)


class Meter(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Metering_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Metering_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Energy_Meter(Meter):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Energyefficiency]]), ('value', [[Meter_Reading]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('some', [[Meter]]), ('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Metering_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('some', [[Energy]]), ('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Energyefficiency())
			self.Accomplishes.add(Meter_Reading())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Energyefficiency, value Meter_Reading, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='some Meter, only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Metering_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='some Energy, only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Metering_Function(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Get_Current_Meter_Value_Command], [Get_Meter_Data_Command], [Get_Meter_History_Command]]), ('min|1', [[Command]])]
			self.Has_Meter_Reading_Type._rules = [('only', [[Commodity], [Property]])]
			self.Has_Meter_Reading._rules = [('only', [[Measurement]])]

			self.Has_Command._instance_identifier = self.get_identifier()
			self.Has_Meter_Reading_Type._instance_identifier = self.get_identifier()
			self.Has_Meter_Reading._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only (Get_Current_Meter_Value_Command or Get_Meter_Data_Command) or Get_Meter_History_Command), min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)
	Has_Meter_Reading_Type: RelationField = RelationField(
		name='Has_Meter_Reading_Type',
		rule='only (Commodity or Property)',
		semantic_manager=semantic_manager)
	Has_Meter_Reading: RelationField = RelationField(
		name='Has_Meter_Reading',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Micro_Renewable(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Energyefficiency]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Energyefficiency())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Energyefficiency, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Multimedia(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Entertainment]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Entertainment())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Entertainment, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Network(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Notify_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Off_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[On_Off_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only On_Off_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class On_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[On_Off_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only On_Off_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class On_Off_Function(Actuating_Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Off_Command], [On_Command], [Toggle_Command]]), ('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only (Off_Command or On_Command) or Toggle_Command), min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class Open_Close_Function(Actuating_Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Close_Command], [Open_Command]]), ('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only (Close_Command or Open_Command), min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class Open_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Open_Close_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Open_Close_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Pause_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Profile(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Consists_Of._rules = [('only', [[Profile]])]
			self.Has_Price._rules = [('only', [[Price]])]
			self.Has_Time._rules = [('only', [[Time]])]
			self.Isabout._rules = [('only', [[Commodity], [Property]])]

			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Has_Price._instance_identifier = self.get_identifier()
			self.Has_Time._instance_identifier = self.get_identifier()
			self.Isabout._instance_identifier = self.get_identifier()


	# Relation fields
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_Price: RelationField = RelationField(
		name='Has_Price',
		rule='only Price',
		semantic_manager=semantic_manager)
	Has_Time: RelationField = RelationField(
		name='Has_Time',
		rule='only Time',
		semantic_manager=semantic_manager)
	Isabout: RelationField = RelationField(
		name='Isabout',
		rule='only (Commodity or Property)',
		semantic_manager=semantic_manager)


class Property(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Energy(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Humidity(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Light(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Motion(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Occupancy(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Power(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Pressure(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Price(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Sensing_Function(Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Get_Sensing_Data_Command]]), ('min|1', [[Command]])]
			self.Has_Sensing_Range_._rules = [('some', [[Measurement]])]
			self.Has_Sensor_Type._rules = [('only', [[Property]])]

			self.Has_Command._instance_identifier = self.get_identifier()
			self.Has_Sensing_Range_._instance_identifier = self.get_identifier()
			self.Has_Sensor_Type._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only Get_Sensing_Data_Command, min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)
	Has_Sensing_Range_: RelationField = RelationField(
		name='Has_Sensing_Range_',
		rule='some Measurement',
		semantic_manager=semantic_manager)
	Has_Sensor_Type: RelationField = RelationField(
		name='Has_Sensor_Type',
		rule='only Property',
		semantic_manager=semantic_manager)


class Sensor(Function_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Sensing_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Sensing_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Service(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Offered_By._rules = [('min|1', [[Device]])]
			self.Represents._rules = [('min|1', [[Function]])]

			self.Is_Offered_By._instance_identifier = self.get_identifier()
			self.Represents._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Offered_By: RelationField = RelationField(
		name='Is_Offered_By',
		rule='min 1 Device',
		inverse_of=['Offers'],
		semantic_manager=semantic_manager)
	Represents: RelationField = RelationField(
		name='Represents',
		rule='min 1 Function',
		semantic_manager=semantic_manager)


class Set_Level_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Multi_Level_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Multi_Level_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Set_Absolute_Level_Command(Set_Level_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Multi_Level_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Multi_Level_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Set_Relative_Level_Command(Set_Level_Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Multi_Level_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Multi_Level_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Smoke(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Smoke_Sensor(Sensor):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Safety]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('some', [[Sensor]]), ('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Event_Function]]), ('some', [[Sensing_Function]]), ('some', [[Sensing_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('some', [[Smoke]]), ('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Safety())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Safety, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='some Sensor, only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Event_Function, some Sensing_Function, some Sensing_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='some Smoke, only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Start_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Start_Stop_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Start_Stop_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Start_Stop_Function(Actuating_Function):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Has_Command._rules = [('only', [[Start_Command], [Stop_Command]]), ('min|1', [[Command]])]

			self.Has_Command._instance_identifier = self.get_identifier()


	# Relation fields
	Has_Command: RelationField = RelationField(
		name='Has_Command',
		rule='only (Start_Command or Stop_Command), min 1 Command',
		inverse_of=['Is_Command_Of'],
		semantic_manager=semantic_manager)


class State(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Multi_Level_State(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class On_Off_State(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Off_State(On_Off_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class On_State(On_Off_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Open_Close_State(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Close_State(Open_Close_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Open_State(Open_Close_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Start_Stop_State(State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Start_State(Start_Stop_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Step_Down_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Multi_Level_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Multi_Level_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Step_Up_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Multi_Level_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Multi_Level_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Stop_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[Start_Stop_State]]), ('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only Start_Stop_State, only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Stop_State(Start_Stop_State):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


class Storage(Energy_Related):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Switch(Actuator):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Actuating_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Actuating_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Door_Switch(Switch):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Safety]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('some', [[Switch]]), ('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Open_Close_Function]]), ('some', [[Actuating_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('some', [[Open_Close_State]]), ('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Safety())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Safety, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='some Switch, only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Open_Close_Function, some Actuating_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='some Open_Close_State, only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Light_Switch(Switch):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Lighting]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('some', [[Switch]]), ('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[On_Off_Function]]), ('some', [[Actuating_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('some', [[On_Off_State]]), ('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('some', [[Light]]), ('only', [[Property]])]
			self.Offers._rules = [('some', [[Switch_On_Service]]), ('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Lighting())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Lighting, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='some Switch, only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some On_Off_Function, some Actuating_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='some On_Off_State, only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='some Light, only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='some Switch_On_Service, only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Switch_On_Service(Service):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Offered_By._rules = [('some', [[Light_Switch]]), ('min|1', [[Device]])]
			self.Represents._rules = [('some', [[On_Off_Function]]), ('min|1', [[Function]])]

			self.Is_Offered_By._instance_identifier = self.get_identifier()
			self.Represents._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Offered_By: RelationField = RelationField(
		name='Is_Offered_By',
		rule='some Light_Switch, min 1 Device',
		inverse_of=['Offers'],
		semantic_manager=semantic_manager)
	Represents: RelationField = RelationField(
		name='Represents',
		rule='some On_Off_Function, min 1 Function',
		semantic_manager=semantic_manager)


class Task(Thing):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Accomplished_By._rules = [('min|1', [[Device]])]

			self.Is_Accomplished_By._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Accomplished_By: RelationField = RelationField(
		name='Is_Accomplished_By',
		rule='min 1 Device',
		inverse_of=['Accomplishes'],
		semantic_manager=semantic_manager)


class Temperature(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Temperature_Sensor(Sensor):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Comfort]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('some', [[Sensor]]), ('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Sensing_Function]]), ('some', [[Sensing_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('only', [[Profile]])]
			self.Has_State._rules = [('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('some', [[Temperature]]), ('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Comfort())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Comfort, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='some Sensor, only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Sensing_Function, some Sensing_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='some Temperature, only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Time(Property):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:

			self.Is_Controlled_By_Device._rules = [('only', [[Device]])]
			self.Is_Measured_By_Device._rules = [('only', [[Device]])]
			self.Relates_To_Measurement._rules = [('only', [[Measurement]])]

			self.Is_Controlled_By_Device._instance_identifier = self.get_identifier()
			self.Is_Measured_By_Device._instance_identifier = self.get_identifier()
			self.Relates_To_Measurement._instance_identifier = self.get_identifier()


	# Relation fields
	Is_Controlled_By_Device: RelationField = RelationField(
		name='Is_Controlled_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Is_Measured_By_Device: RelationField = RelationField(
		name='Is_Measured_By_Device',
		rule='only Device',
		semantic_manager=semantic_manager)
	Relates_To_Measurement: RelationField = RelationField(
		name='Relates_To_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)


class Toggle_Command(Command):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]

			self.Acts_Upon._rules = [('only', [[State]])]
			self.Is_Command_Of._rules = [('min|1', [[Function]])]

			self.Acts_Upon._instance_identifier = self.get_identifier()
			self.Is_Command_Of._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()


	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Acts_Upon: RelationField = RelationField(
		name='Acts_Upon',
		rule='only State',
		semantic_manager=semantic_manager)
	Is_Command_Of: RelationField = RelationField(
		name='Is_Command_Of',
		rule='min 1 Function',
		inverse_of=['Has_Command'],
		semantic_manager=semantic_manager)


class Washing_Machine(Appliance, Load):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)
		if not is_initialised:
			self.Has_Description._rules = [('max|1', [['string']])]
			self.Has_Manufacturer._rules = [('max|1', [['string']])]
			self.Has_Model._rules = [('max|1', [['string']])]

			self.Accomplishes._rules = [('value', [[Washing]]), ('min|1', [[Task]])]
			self.Consists_Of._rules = [('only', [[Device]])]
			self.Controls_Property._rules = [('only', [[Property]])]
			self.Has_Function._rules = [('some', [[Start_Stop_Function]]), ('min|1', [[Function]])]
			self.Has_Profile._rules = [('some', [[Profile]]), ('only', [[Profile]])]
			self.Has_State._rules = [('some', [[Start_Stop_State]]), ('only', [[State]])]
			self.Has_Typical_Consumption._rules = [('only', [[Energy], [Power]])]
			self.Is_Used_For._rules = [('only', [[Commodity]])]
			self.Makes_Measurement._rules = [('only', [[Measurement]])]
			self.Measures_Property._rules = [('only', [[Property]])]
			self.Offers._rules = [('only', [[Service]])]

			self.Accomplishes._instance_identifier = self.get_identifier()
			self.Consists_Of._instance_identifier = self.get_identifier()
			self.Controls_Property._instance_identifier = self.get_identifier()
			self.Has_Function._instance_identifier = self.get_identifier()
			self.Has_Profile._instance_identifier = self.get_identifier()
			self.Has_State._instance_identifier = self.get_identifier()
			self.Has_Typical_Consumption._instance_identifier = self.get_identifier()
			self.Is_Used_For._instance_identifier = self.get_identifier()
			self.Makes_Measurement._instance_identifier = self.get_identifier()
			self.Measures_Property._instance_identifier = self.get_identifier()
			self.Offers._instance_identifier = self.get_identifier()
			self.Has_Description._instance_identifier = self.get_identifier()
			self.Has_Manufacturer._instance_identifier = self.get_identifier()
			self.Has_Model._instance_identifier = self.get_identifier()

			self.Accomplishes.add(Washing())

	# Data fields
	Has_Description: DataField = DataField(
		name='Has_Description',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Manufacturer: DataField = DataField(
		name='Has_Manufacturer',
		rule='max 1 string',
		semantic_manager=semantic_manager)
	Has_Model: DataField = DataField(
		name='Has_Model',
		rule='max 1 string',
		semantic_manager=semantic_manager)

	# Relation fields
	Accomplishes: RelationField = RelationField(
		name='Accomplishes',
		rule='value Washing, min 1 Task',
		inverse_of=['Is_Accomplished_By'],
		semantic_manager=semantic_manager)
	Consists_Of: RelationField = RelationField(
		name='Consists_Of',
		rule='only Device',
		semantic_manager=semantic_manager)
	Controls_Property: RelationField = RelationField(
		name='Controls_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Has_Function: RelationField = RelationField(
		name='Has_Function',
		rule='some Start_Stop_Function, min 1 Function',
		semantic_manager=semantic_manager)
	Has_Profile: RelationField = RelationField(
		name='Has_Profile',
		rule='some Profile, only Profile',
		semantic_manager=semantic_manager)
	Has_State: RelationField = RelationField(
		name='Has_State',
		rule='some Start_Stop_State, only State',
		semantic_manager=semantic_manager)
	Has_Typical_Consumption: RelationField = RelationField(
		name='Has_Typical_Consumption',
		rule='only (Energy or Power)',
		semantic_manager=semantic_manager)
	Is_Used_For: RelationField = RelationField(
		name='Is_Used_For',
		rule='only Commodity',
		semantic_manager=semantic_manager)
	Makes_Measurement: RelationField = RelationField(
		name='Makes_Measurement',
		rule='only Measurement',
		semantic_manager=semantic_manager)
	Measures_Property: RelationField = RelationField(
		name='Measures_Property',
		rule='only Property',
		semantic_manager=semantic_manager)
	Offers: RelationField = RelationField(
		name='Offers',
		rule='only Service',
		inverse_of=['Is_Offered_By'],
		semantic_manager=semantic_manager)


class Water(Commodity):

	def __init__(self, *args, **kwargs):
		is_initialised = 'id' in self.__dict__
		super().__init__(*args, **kwargs)


# ---------Individuals--------- #


class Individual1(SemanticIndividual):
	_parent_classes: List[type] = [Class2, Class1]


class Individual2(SemanticIndividual):
	_parent_classes: List[type] = [Class1]


class Individual3(SemanticIndividual):
	_parent_classes: List[type] = [Class2, Class1, Class3]


class Individual4(SemanticIndividual):
	_parent_classes: List[type] = [Class1, Class2]


class United_States_Dollar(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Bar(SemanticIndividual):
	_parent_classes: List[type] = [Pressure_Unit]


class Degree_Celsius(SemanticIndividual):
	_parent_classes: List[type] = [Temperature_Unit]


class Degree_Fahrenheit(SemanticIndividual):
	_parent_classes: List[type] = [Temperature_Unit]


class Euro(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Kelvin(SemanticIndividual):
	_parent_classes: List[type] = [Temperature_Unit]


class Kilowatt(SemanticIndividual):
	_parent_classes: List[type] = [Power_Unit]


class Kilowatt_Hour(SemanticIndividual):
	_parent_classes: List[type] = [Energy_Unit]


class Lux(SemanticIndividual):
	_parent_classes: List[type] = [Illuminance_Unit]


class Pascal(SemanticIndividual):
	_parent_classes: List[type] = [Pressure_Unit]


class Great_Britain_Pound_Sterling(SemanticIndividual):
	_parent_classes: List[type] = [Currency]


class Watt(SemanticIndividual):
	_parent_classes: List[type] = [Power_Unit]


class Cleaning(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Close(SemanticIndividual):
	_parent_classes: List[type] = [Close_Command, Close_State]


class Comfort(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Drying(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Energyefficiency(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Entertainment(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Get_Current_Meter_Value(SemanticIndividual):
	_parent_classes: List[type] = [Get_Current_Meter_Value_Command]


class Get_Meter_Data(SemanticIndividual):
	_parent_classes: List[type] = [Get_Meter_Data_Command]


class Get_Meter_History(SemanticIndividual):
	_parent_classes: List[type] = [Get_Meter_History_Command]


class Get_Sensing_Data(SemanticIndividual):
	_parent_classes: List[type] = [Get_Sensing_Data_Command]


class Lighting(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Meter_Reading(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Notify(SemanticIndividual):
	_parent_classes: List[type] = [Notify_Command]


class Off_(SemanticIndividual):
	_parent_classes: List[type] = [Off_Command, Off_State]


class On(SemanticIndividual):
	_parent_classes: List[type] = [On_Command, On_State]


class Open(SemanticIndividual):
	_parent_classes: List[type] = [Open_Command, Open_State]


class Pause(SemanticIndividual):
	_parent_classes: List[type] = [Pause_Command]


class Safety(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Set_Absolute_Level(SemanticIndividual):
	_parent_classes: List[type] = [Set_Absolute_Level_Command]


class Set_Relative_Level(SemanticIndividual):
	_parent_classes: List[type] = [Set_Relative_Level_Command]


class Start(SemanticIndividual):
	_parent_classes: List[type] = [Start_Command, Start_State]


class Step_Down(SemanticIndividual):
	_parent_classes: List[type] = [Step_Down_Command]


class Step_Up(SemanticIndividual):
	_parent_classes: List[type] = [Step_Up_Command]


class Stop(SemanticIndividual):
	_parent_classes: List[type] = [Stop_Command, Stop_State]


class Toggle(SemanticIndividual):
	_parent_classes: List[type] = [Toggle_Command]


class Washing(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Wellbeing(SemanticIndividual):
	_parent_classes: List[type] = [Task]


class Watt_Hour(SemanticIndividual):
	_parent_classes: List[type] = [Energy_Unit]


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
	'Actuating_Function': Actuating_Function,
	'Actuator': Actuator,
	'Appliance': Appliance,
	'Building_Related': Building_Related,
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
	'Close_Command': Close_Command,
	'Close_State': Close_State,
	'Coal': Coal,
	'Command': Command,
	'Commodity': Commodity,
	'Currency': Currency,
	'Device': Device,
	'Door_Switch': Door_Switch,
	'Electricity': Electricity,
	'Energy': Energy,
	'Energy_Meter': Energy_Meter,
	'Energy_Related': Energy_Related,
	'Energy_Unit': Energy_Unit,
	'Event_Function': Event_Function,
	'Function': Function,
	'Function_Related': Function_Related,
	'Gas': Gas,
	'Generator': Generator,
	'Gertrude': Gertrude,
	'Get_Command': Get_Command,
	'Get_Current_Meter_Value_Command': Get_Current_Meter_Value_Command,
	'Get_Meter_Data_Command': Get_Meter_Data_Command,
	'Get_Meter_History_Command': Get_Meter_History_Command,
	'Get_Sensing_Data_Command': Get_Sensing_Data_Command,
	'Humidity': Humidity,
	'Hvac': Hvac,
	'Illuminance_Unit': Illuminance_Unit,
	'Level_Control_Function': Level_Control_Function,
	'Light': Light,
	'Light_Switch': Light_Switch,
	'Lighting_Device': Lighting_Device,
	'Load': Load,
	'Measurement': Measurement,
	'Meter': Meter,
	'Metering_Function': Metering_Function,
	'Micro_Renewable': Micro_Renewable,
	'Motion': Motion,
	'Multi_Level_State': Multi_Level_State,
	'Multimedia': Multimedia,
	'Network': Network,
	'Notify_Command': Notify_Command,
	'Occupancy': Occupancy,
	'Off_Command': Off_Command,
	'Off_State': Off_State,
	'On_Command': On_Command,
	'On_Off_Function': On_Off_Function,
	'On_Off_State': On_Off_State,
	'On_State': On_State,
	'Open_Close_Function': Open_Close_Function,
	'Open_Close_State': Open_Close_State,
	'Open_Command': Open_Command,
	'Open_State': Open_State,
	'Pause_Command': Pause_Command,
	'Power': Power,
	'Power_Unit': Power_Unit,
	'Pressure': Pressure,
	'Pressure_Unit': Pressure_Unit,
	'Price': Price,
	'Profile': Profile,
	'Property': Property,
	'Sensing_Function': Sensing_Function,
	'Sensor': Sensor,
	'Service': Service,
	'Set_Absolute_Level_Command': Set_Absolute_Level_Command,
	'Set_Level_Command': Set_Level_Command,
	'Set_Relative_Level_Command': Set_Relative_Level_Command,
	'Smoke': Smoke,
	'Smoke_Sensor': Smoke_Sensor,
	'Start_Command': Start_Command,
	'Start_State': Start_State,
	'Start_Stop_Function': Start_Stop_Function,
	'Start_Stop_State': Start_Stop_State,
	'State': State,
	'Step_Down_Command': Step_Down_Command,
	'Step_Up_Command': Step_Up_Command,
	'Stop_Command': Stop_Command,
	'Stop_State': Stop_State,
	'Storage': Storage,
	'Switch': Switch,
	'Switch_On_Service': Switch_On_Service,
	'Task': Task,
	'Temperature': Temperature,
	'Temperature_Sensor': Temperature_Sensor,
	'Temperature_Unit': Temperature_Unit,
	'Thing': Thing,
	'Time': Time,
	'Toggle_Command': Toggle_Command,
	'Washing_Machine': Washing_Machine,
	'Water': Water,
	}


semantic_manager.individual_catalogue = {
	'Individual1': Individual1,
	'Individual2': Individual2,
	'Individual3': Individual3,
	'Individual4': Individual4,
	'United_States_Dollar': United_States_Dollar,
	'Bar': Bar,
	'Degree_Celsius': Degree_Celsius,
	'Degree_Fahrenheit': Degree_Fahrenheit,
	'Euro': Euro,
	'Kelvin': Kelvin,
	'Kilowatt': Kilowatt,
	'Kilowatt_Hour': Kilowatt_Hour,
	'Lux': Lux,
	'Pascal': Pascal,
	'Great_Britain_Pound_Sterling': Great_Britain_Pound_Sterling,
	'Watt': Watt,
	'Cleaning': Cleaning,
	'Close': Close,
	'Comfort': Comfort,
	'Drying': Drying,
	'Energyefficiency': Energyefficiency,
	'Entertainment': Entertainment,
	'Get_Current_Meter_Value': Get_Current_Meter_Value,
	'Get_Meter_Data': Get_Meter_Data,
	'Get_Meter_History': Get_Meter_History,
	'Get_Sensing_Data': Get_Sensing_Data,
	'Lighting': Lighting,
	'Meter_Reading': Meter_Reading,
	'Notify': Notify,
	'Off_': Off_,
	'On': On,
	'Open': Open,
	'Pause': Pause,
	'Safety': Safety,
	'Set_Absolute_Level': Set_Absolute_Level,
	'Set_Relative_Level': Set_Relative_Level,
	'Start': Start,
	'Step_Down': Step_Down,
	'Step_Up': Step_Up,
	'Stop': Stop,
	'Toggle': Toggle,
	'Washing': Washing,
	'Wellbeing': Wellbeing,
	'Watt_Hour': Watt_Hour,
	}
