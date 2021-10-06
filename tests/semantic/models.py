from typing import Dict, Union
from filip.semantics.semantic_models import \
	SemanticClass, SemanticIndividual, RelationField, DataField, InstanceRegistry
from filip.semantics.semantic_manager import SemanticManager


semantic_manager: SemanticManager = SemanticManager(
	instance_registry=InstanceRegistry()
)

# ---------CLASSES--------- #


class Thing(SemanticClass):

	def __new__(cls, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		super().__init__(*args, **kwargs)




	# Data fields

	# Relation fields


class Class1(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class1a(Class1):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class1aa(Class1a):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class1b(Class1):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('some', [[Class2]]), ('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='some Class2, some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class2(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('min|1', [[Class1]])]
		self.objProp2._rules = [('only', [[Thing]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='min 1 Class1',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='only Thing',
		semantic_manager=semantic_manager)


class Class3(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dataProp1._rules = [('only', [['customDataType4']])]

		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Data fields
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class123(Class1, Class2, Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dataProp1._rules = [('only', [['customDataType4']])]

		self.oProp1._rules = [('value', [[Individual1]]), ('min|1', [[Class1]]), ('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]]), ('only', [[Thing]]), ('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1, min 1 Class1, some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1, only Thing, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class13(Class1, Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dataProp1._rules = [('min|1', [['int']]), ('only', [['customDataType4']])]
		self.dataProp2._rules = [('exactly|1', [['boolean']])]

		self.oProp1._rules = [('value', [[Individual1]]), ('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]]), ('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='min 1 int, only customDataType4',
		semantic_manager=semantic_manager)
	dataProp2: DataField = DataField(
		name='dataProp2',
		rule='exactly 1 boolean',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1, some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


class Class3a(Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dataProp1._rules = [('only', [['customDataType4']])]

		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Data fields
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class3aa(Class3a):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dataProp1._rules = [('only', [['customDataType4']])]

		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Data fields
	dataProp1: DataField = DataField(
		name='dataProp1',
		rule='only customDataType4',
		semantic_manager=semantic_manager)

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='value Individual1',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager=semantic_manager)


class Class4(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.objProp4._rules = [('min|1', [[Class1]])]

		self.objProp4._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='min 1 Class1',
		semantic_manager=semantic_manager)


class Gertrude(Class1, Class2):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.oProp1._rules = [('min|1', [[Class1]]), ('some', [[Class2], [Class4]])]
		self.objProp2._rules = [('only', [[Thing]]), ('some', [[Class1, Class2]])]
		self.objProp3._rules = [('some', [[Class3]])]
		self.objProp4._rules = [('some', [[Class1, Class2, Class3]])]
		self.objProp5._rules = [('some', [[Class1, Class2], [Class1, Class3]])]

		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()
		self.objProp3._class_identifier = self.get_identifier()
		self.objProp4._class_identifier = self.get_identifier()
		self.objProp5._class_identifier = self.get_identifier()

	# Data fields

	# Relation fields
	oProp1: RelationField = RelationField(
		name='oProp1',
		rule='min 1 Class1, some (Class2 or Class4)',
		semantic_manager=semantic_manager)
	objProp2: RelationField = RelationField(
		name='objProp2',
		rule='only Thing, some (Class1 and Class2)',
		semantic_manager=semantic_manager)
	objProp3: RelationField = RelationField(
		name='objProp3',
		rule='some Class3',
		semantic_manager=semantic_manager)
	objProp4: RelationField = RelationField(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager=semantic_manager)
	objProp5: RelationField = RelationField(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager=semantic_manager)


# ---------Individuals--------- #

class Individual1(SemanticIndividual, Class2, Class1):
	pass

class Individual2(SemanticIndividual, Class1):
	pass

class Individual3(SemanticIndividual, Class2, Class1, Class3):
	pass

class Individual4(SemanticIndividual, Class1, Class2):
	pass





# ---------Datatypes--------- #
semantic_manager.datatypes = {
	'customDataType1': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['0', '15', '30'], 'number_has_range': False, 'type': 'enum'},
	'customDataType2': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'customDataType3': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'customDataType4': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['1', '2', '3', '4'], 'number_has_range': False, 'type': 'enum'},
	'rational': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'real': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'PlainLiteral': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'XMLLiteral': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'Literal': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'anyURI': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'base64Binary': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'boolean': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': ['True', 'False'], 'number_has_range': False, 'type': 'enum'},
	'byte': 	 {'number_range_min': -128, 'number_range_max': 127, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'dateTime': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'date'},
	'dateTimeStamp': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'date'},
	'decimal': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'double': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'float': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': True, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'hexBinary': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'int': 	 {'number_range_min': -2147483648, 'number_range_max': 2147483647, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'integer': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'number'},
	'language': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'long': 	 {'number_range_min': -9223372036854775808, 'number_range_max': 9223372036854775807, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'Name': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'NCName': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [':'], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'negativeInteger': 	 {'number_range_min': '/', 'number_range_max': -1, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'NMTOKEN': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'nonNegativeInteger': 	 {'number_range_min': 0, 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'nonPositiveInteger': 	 {'number_range_min': '/', 'number_range_max': -1, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'normalizedString': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'positiveInteger': 	 {'number_range_min': 0, 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'short': 	 {'number_range_min': -32768, 'number_range_max': 32767, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'string': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'token': 	 {'number_range_min': '/', 'number_range_max': '/', 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': False, 'type': 'string'},
	'unsignedByte': 	 {'number_range_min': 0, 'number_range_max': 255, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'unsignedInt': 	 {'number_range_min': 0, 'number_range_max': 4294967295, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'unsignedLong': 	 {'number_range_min': 0, 'number_range_max': 18446744073709551615, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
	'unsignedShort': 	 {'number_range_min': 0, 'number_range_max': 65535, 'number_decimal_allowed': False, 'forbidden_chars': [], 'allowed_chars': [], 'enum_values': [], 'number_has_range': True, 'type': 'number'},
}

semantic_manager.model_catalogue = {
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
	'Individual1': Individual1,
	'Individual2': Individual2,
	'Individual3': Individual3,
	'Individual4': Individual4,
	}
