from typing import Dict, Union
from filip.semantics.semantic_models import \
	SemanticClass, SemanticIndividual, Relationship, ModelCatalogue, InstanceRegistry
from filip.semantics.semantic_manager import SemanticManager


semantic_manager: SemanticManager = SemanticManager(
	instance_registry=InstanceRegistry()
)

# ---------CLASSES--------- #


class Thing(SemanticClass):

	def __init__(self, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		super().__init__(*args, **kwargs)

	def __new__(cls, *args, **kwargs):
		kwargs['semantic_manager'] = semantic_manager
		return super().__new__(cls, *args, **kwargs)
		pass

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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='some Class2, some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


class Class2(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.oProp1._rules = [('min|1', [[Class1]])]
		self.objProp2._rules = [('only', [[Thing]])]
		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='min 1 Class1',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='only Thing',
		semantic_manager = semantic_manager)


class Class3(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]
		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='value Individual1',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager = semantic_manager)


class Class123(Class1, Class2, Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='value Individual1, min 1 Class1, some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some Class1, value Individual1, only Thing, some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


class Class13(Class1, Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='value Individual1, some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some Class1, value Individual1, some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


class Class3a(Class3):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]
		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='value Individual1',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager = semantic_manager)


class Class3aa(Class3a):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.oProp1._rules = [('value', [[Individual1]])]
		self.objProp2._rules = [('some', [[Class1]]), ('value', [[Individual1]])]
		self.oProp1._class_identifier = self.get_identifier()
		self.objProp2._class_identifier = self.get_identifier()

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='value Individual1',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='some Class1, value Individual1',
		semantic_manager = semantic_manager)


class Class4(Thing):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.objProp4._rules = [('min|1', [[Class1]])]
		self.objProp4._class_identifier = self.get_identifier()

	# Relation fields
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='min 1 Class1',
		semantic_manager = semantic_manager)


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

	# Relation fields
	oProp1: Relationship = Relationship(
		name='oProp1',
		rule='min 1 Class1, some (Class2 or Class4)',
		semantic_manager = semantic_manager)
	objProp2: Relationship = Relationship(
		name='objProp2',
		rule='only Thing, some (Class1 and Class2)',
		semantic_manager = semantic_manager)
	objProp3: Relationship = Relationship(
		name='objProp3',
		rule='some Class3',
		semantic_manager = semantic_manager)
	objProp4: Relationship = Relationship(
		name='objProp4',
		rule='some (Class1 and Class2) and Class3)',
		semantic_manager = semantic_manager)
	objProp5: Relationship = Relationship(
		name='objProp5',
		rule='some (Class1 and (Class2 or Class3))',
		semantic_manager = semantic_manager)


# ---------Individuals--------- #

class Individual1(SemanticIndividual, Class2, Class1):
	pass

class Individual2(SemanticIndividual, Class1):
	pass

class Individual3(SemanticIndividual, Class2, Class1, Class3):
	pass

class Individual4(SemanticIndividual, Class1, Class2):
	pass


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
