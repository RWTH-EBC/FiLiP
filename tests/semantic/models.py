import inspect, sys
from pydantic import BaseModel, Field
from typing import List, Union, Dict
from filip.semantics.semantic_models import SemanticClass, SemanticIndividual, Relationship

##CLASSES##

class Thing(SemanticClass):

	def __init__(self):
		super().__init__()
		pass

	#Relation fields

class Class1(Thing):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='some (Class2 or Class4)',
		_rules=[('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some (Class1 and Class2)',
		_rules=[('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class1a(Class1):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='some (Class2 or Class4)',
		_rules=[('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some (Class1 and Class2)',
		_rules=[('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class1aa(Class1a):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='some (Class2 or Class4)',
		_rules=[('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some (Class1 and Class2)',
		_rules=[('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class1b(Class1):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='some Class2, some (Class2 or Class4)',
		_rules=[('some', [['Class2']]), ('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some (Class1 and Class2)',
		_rules=[('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class2(Thing):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='min 1 Class1',
		_rules=[('min|1', [['Class1']])],
	)

	objProp2: Relationship = Relationship(
		rule='only Thing',
		_rules=[('only', [['Thing']])],
	)

class Class3(Thing):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class123(Class1, Class2, Class3):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1, min 1 Class1, some (Class2 or Class4)',
		_rules=[('value', [['Individual1']]), ('min|1', [['Class1']]), ('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1, only Thing, some (Class1 and Class2)',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']]), ('only', [['Thing']]), ('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class13(Class1, Class3):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1, some (Class2 or Class4)',
		_rules=[('value', [['Individual1']]), ('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1, some (Class1 and Class2)',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']]), ('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)

class Class3a(Class3):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class3aa(Class3a):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class4(Thing):

	def __init__(self):
		super().__init__()
		self.objProp4._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	objProp4: Relationship = Relationship(
		rule='min 1 Class1',
		_rules=[('min|1', [['Class1']])],
	)

class Gertrude(Class1, Class2):

	def __init__(self):
		super().__init__()
		self.oProp1._model_catalogue = ModelCatalogue.catalogue
		self.objProp2._model_catalogue = ModelCatalogue.catalogue
		self.objProp3._model_catalogue = ModelCatalogue.catalogue
		self.objProp4._model_catalogue = ModelCatalogue.catalogue
		self.objProp5._model_catalogue = ModelCatalogue.catalogue

	#Relation fields

	oProp1: Relationship = Relationship(
		rule='min 1 Class1, some (Class2 or Class4)',
		_rules=[('min|1', [['Class1']]), ('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='only Thing, some (Class1 and Class2)',
		_rules=[('only', [['Thing']]), ('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3',
		_rules=[('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)


##Individuals##

class Individual1(SemanticIndividual, Class2, Class1):
	pass

class Individual2(SemanticIndividual, Class1):
	pass

class Individual3(SemanticIndividual, Class2, Class1, Class3):
	pass

class Individual4(SemanticIndividual, Class1, Class2):
	pass


class ModelCatalogue:
	catalogue: Dict[str, type] = {
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