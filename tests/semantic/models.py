from pydantic import BaseModel, Field
from typing import List, Union
from filip.semantics.semantic_models import SemanticClass, SemanticIndividual, Relationship

##CLASSES##

class Thing(SemanticClass):
	#Relation fields
	 pass

class Class1(SemanticClass, Thing):
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

class Class1a(SemanticClass, Class1):
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

class Class1aa(SemanticClass, Class1a):
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

class Class1b(SemanticClass, Class1):
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

class Class2(SemanticClass, Thing):
	#Relation fields

	oProp1: Relationship = Relationship(
		rule='min 1 Class1',
		_rules=[('min|1', [['Class1']])],
	)

	objProp2: Relationship = Relationship(
		rule='only Thing',
		_rules=[('only', [['Thing']])],
	)

class Class3(SemanticClass, Thing):
	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class123(SemanticClass, Class1, Class2, Class3):
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

class Class13(SemanticClass, Class1, Class3):
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

class Class3a(SemanticClass, Class3):
	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class3aa(SemanticClass, Class3a):
	#Relation fields

	oProp1: Relationship = Relationship(
		rule='value Individual1',
		_rules=[('value', [['Individual1']])],
	)

	objProp2: Relationship = Relationship(
		rule='some Class1, value Individual1',
		_rules=[('some', [['Class1']]), ('value', [['Individual1']])],
	)

class Class4(SemanticClass, Thing):
	#Relation fields

	objProp4: Relationship = Relationship(
		rule='min 1 Class1',
		_rules=[('min|1', [['Class1']])],
	)

class Gertrude(SemanticClass, Class1, Class2, Class1, Class2):
	#Relation fields

	oProp1: Relationship = Relationship(
		rule='min 1 Class1, some (Class2 or Class4), min 1 Class1, some (Class2 or Class4)',
		_rules=[('min|1', [['Class1']]), ('some', [['Class2'], ['Class4']]), ('min|1', [['Class1']]), ('some', [['Class2'], ['Class4']])],
	)

	objProp2: Relationship = Relationship(
		rule='only Thing, some (Class1 and Class2), only Thing, some (Class1 and Class2)',
		_rules=[('only', [['Thing']]), ('some', [['Class1', 'Class2']]), ('only', [['Thing']]), ('some', [['Class1', 'Class2']])],
	)

	objProp3: Relationship = Relationship(
		rule='some Class3, some Class3',
		_rules=[('some', [['Class3']]), ('some', [['Class3']])],
	)

	objProp4: Relationship = Relationship(
		rule='some (Class1 and Class2) and Class3), some (Class1 and Class2) and Class3)',
		_rules=[('some', [['Class1', 'Class2', 'Class3']]), ('some', [['Class1', 'Class2', 'Class3']])],
	)

	objProp5: Relationship = Relationship(
		rule='some (Class1 and (Class2 or Class3)), some (Class1 and (Class2 or Class3))',
		_rules=[('some', [['Class1', 'Class2'], ['Class1', 'Class3']]), ('some', [['Class1', 'Class2'], ['Class1', 'Class3']])],
	)


##Individuals##

class Individual1(SemanticIndividual, Class2, Class1):
	@oProp1.setter
	def oProp1(self, value):
		assert False, 'Individuals have no values'
	@objProp2.setter
	def objProp2(self, value):
		assert False, 'Individuals have no values'
	@objProp3.setter
	def objProp3(self, value):
		assert False, 'Individuals have no values'
	@objProp4.setter
	def objProp4(self, value):
		assert False, 'Individuals have no values'
	@objProp5.setter
	def objProp5(self, value):
		assert False, 'Individuals have no values'

class Individual2(SemanticIndividual, Class1):
	@oProp1.setter
	def oProp1(self, value):
		assert False, 'Individuals have no values'
	@objProp2.setter
	def objProp2(self, value):
		assert False, 'Individuals have no values'
	@objProp3.setter
	def objProp3(self, value):
		assert False, 'Individuals have no values'
	@objProp4.setter
	def objProp4(self, value):
		assert False, 'Individuals have no values'
	@objProp5.setter
	def objProp5(self, value):
		assert False, 'Individuals have no values'

class Individual3(SemanticIndividual, Class2, Class1, Class3):
	@oProp1.setter
	def oProp1(self, value):
		assert False, 'Individuals have no values'
	@objProp2.setter
	def objProp2(self, value):
		assert False, 'Individuals have no values'
	@objProp3.setter
	def objProp3(self, value):
		assert False, 'Individuals have no values'
	@objProp4.setter
	def objProp4(self, value):
		assert False, 'Individuals have no values'
	@objProp5.setter
	def objProp5(self, value):
		assert False, 'Individuals have no values'

class Individual4(SemanticIndividual, Class1, Class2):
	@oProp1.setter
	def oProp1(self, value):
		assert False, 'Individuals have no values'
	@objProp2.setter
	def objProp2(self, value):
		assert False, 'Individuals have no values'
	@objProp3.setter
	def objProp3(self, value):
		assert False, 'Individuals have no values'
	@objProp4.setter
	def objProp4(self, value):
		assert False, 'Individuals have no values'
	@objProp5.setter
	def objProp5(self, value):
		assert False, 'Individuals have no values'


