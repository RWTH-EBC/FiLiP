"""Module contains the RDFParser that can create a Vocabulary object out of a
given ontology"""

import uuid
from enum import Enum
from typing import List, Tuple

import rdflib

from filip.models.base import LogLevel
from filip.semantics.ontology_parser.vocabulary_builder import VocabularyBuilder
from filip.semantics.vocabulary import Source, IdType, \
    Vocabulary,RestrictionType, ObjectProperty, DataProperty, Relation, \
    TargetStatement, StatementType, DatatypeType, Datatype, Class, Individual


specifier_base_iris = ["http://www.w3.org/2002/07/owl",
                       "http://www.w3.org/1999/02/22-rdf-syntax-ns",
                       "http://www.w3.org/XML/1998/namespace",
                       "http://www.w3.org/2001/XMLSchema",
                       "http://www.w3.org/2000/01/rdf-schema"]
"""
Defines a set of base iris, that describe elements that belong to the 
description language not the ontology itself
"""


class Tags(str, Enum):
    """
    Collection of tags used as structures in ontologies, that were used more
    than once in the rdfparser code
    """
    rdf_type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    owl_intersection = 'http://www.w3.org/2002/07/owl#intersectionOf',
    owl_union = 'http://www.w3.org/2002/07/owl#unionOf',
    owl_one_of = 'http://www.w3.org/2002/07/owl#oneOf',
    owl_individual = 'http://www.w3.org/2002/07/owl#NamedIndividual',
    owl_on_class = 'http://www.w3.org/2002/07/owl#onClass',
    owl_on_data_range = 'http://www.w3.org/2002/07/owl#onDataRange'


def get_iri_from_uriref(uriref: rdflib.URIRef) -> str:
    """Give an Uriref object, returns an iri

    Args:
        uriref: Object describing the iri

    Returns:
        str
    """
    return str(uriref)


def get_base_out_of_iri(iri: str) -> str:
    """Give an iri, returns an the ontology base name

       Args:
           iri

       Returns:
           str
       """
    if "#" in iri:
        index = iri.find("#")
        return iri[:index]
    else:
        # for example if uri looks like:
        # http://webprotege.stanford.edu/RDwpQ8vbi7HaApq8VoqJUXH
        index = iri.rfind("/")
        return iri[:index]


class RdfParser:
    """
    Class that parses a given source into a vocabulary.
    """
    def __init__(self):
        self.current_source = None
        """Current source which is parsed, used for Log entries"""
        self.current_class_iri = None
        """Iri of class which is currently parsed, used for Log entries"""

    def _add_logging_information(self, level: LogLevel,
                                 entity_type: IdType, entity_iri: str,
                                 msg: str):
        """Add an entry to the parsing log

        Args:
            level (LogLevel): severe, warning or info
            entity_type (IdType)
            entity_iri (str)
            msg (str): Message to inform the user about the occurred issue

        Returns:
            None
        """
        if self.current_source is not None:
            self.current_source.add_parsing_log_entry(level, entity_type,
                                                      entity_iri, msg)

    def parse_source_into_vocabulary(self, source: Source,
                                     vocabulary: Vocabulary) -> bool:
        """ Parse a Source into the given vocabulary
        Args:
            source (Source)
            vocabulary (Vocabulary)

        Returns:
            bool, True if success, False if Error occurred, as an invalid File
        """

        # if this is the predefined source don't parse it, just pretend it
        # was successful
        if source.predefined:
            return True

        voc_builder = VocabularyBuilder(vocabulary=vocabulary)
        g = rdflib.Graph()

        # format = rdflib.util.guess_format(source.source_path)
        voc_builder.add_source(source)
        voc_builder.set_current_source(source.id)

        g.parse(data=source.content, format="turtle")

        ontology_nodes = list(g.subjects(
            object=rdflib.term.URIRef("http://www.w3.org/2002/07/owl#Ontology"),
            predicate=rdflib.term.URIRef(Tags.rdf_type.value)))

        # a source may have no ontology iri defined
        # if wanted on this place more info about the ontology can be extracted
        if len(ontology_nodes) > 0:
            source.ontology_iri = get_iri_from_uriref(ontology_nodes[0])

        self.current_source = source

        self._parse_to_vocabulary(g, voc_builder)

        return True

    def _is_object_defined_by_other_source(self, a: rdflib.term,
                                           graph: rdflib.Graph) -> bool:
        """ Test if the term is defined outside the current source

        Args:
            a (rdflib.term): Term to check
            graph (rdflib.graph): graph extracted from source

        Returns:
            bool
        """

        # if an object is defined by an other source it carries the predicate
        # ("isDefinedBy"). Then don't parse the object
        defined_tags = list(graph.objects(
            subject=a, predicate=rdflib.term.URIRef(
                "http://www.w3.org/2000/01/rdf-schema#isDefinedBy")))
        return len(defined_tags) > 0

    def _parse_to_vocabulary(self, graph: rdflib.Graph,
                             voc_builder: VocabularyBuilder):
        """Parse an graph that was extracted from a TTL file into the vocabulary

        Args:
            graph (rdflib.Graph)
            voc_builder (VocabularyBuilder): Builder object to manipulate a
                vocabulary

        Returns:
            None
        """

        # OWLClasses
        for a in graph.subjects(
                object=rdflib.term.URIRef(
                    "http://www.w3.org/2002/07/owl#Class"),
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):

            if isinstance(a, rdflib.term.BNode):
                pass
                # owl:Class can also occure in complex target statements of
                # relations as BNode, ignore it here
            else:

                # defined in other source -> ignore
                if self._is_object_defined_by_other_source(a, graph=graph):
                    continue

                iri, label, comment = self._extract_annotations(graph, a)
                c = Class(iri=iri, label=label, comment=comment)
                voc_builder.add_class(class_=c)

        # Class properties
        found_class_iris = set()
        for class_node in graph.subjects(
                predicate=rdflib.term.URIRef(
                    "http://www.w3.org/2000/01/rdf-schema#subClassOf")):

            class_iri = get_iri_from_uriref(class_node)
            found_class_iris.add(class_iri)

        for class_iri in found_class_iris:
            # parent class / relation parsing
            for sub in graph.objects(
                    subject=rdflib.term.URIRef(class_iri),
                    predicate=rdflib.term.URIRef
                        ('http://www.w3.org/2000/01/rdf-schema#subClassOf')):
                self.current_class_iri = class_iri  # used only for logging
                self._parse_subclass_term(graph=graph,
                                          voc_builder=voc_builder,
                                          node=sub,
                                          class_iri=class_iri)

        # OWlObjectProperties
        for a in graph.subjects(
                object=rdflib.term.URIRef(
                    "http://www.w3.org/2002/07/owl#ObjectProperty"),
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):

            if isinstance(a, rdflib.term.BNode):
                self._add_logging_information(LogLevel.WARNING,
                                              IdType.object_property,
                                              "unknown",
                                              "Found unparseable statement")

            else:
                # defined in other source -> ignore
                if self._is_object_defined_by_other_source(a, graph):
                    continue

                iri, label, comment = self._extract_annotations(graph, a)

                obj_prop = ObjectProperty(iri=iri, label=label, comment=comment)
                voc_builder.add_object_property(obj_prop)
                # extract inverse properties, it can be multiple but only
                # URIRefs allowed no union/intersection
                for inverse_iri_node in graph.objects(subject=a,
                        predicate=rdflib.term.URIRef(
                        'http://www.w3.org/2002/07/owl#inverseOf')):
                    if isinstance(inverse_iri_node, rdflib.term.BNode):
                        self._add_logging_information(
                            LogLevel.CRITICAL, IdType.object_property, iri,
                            "Complex inverseProperty statements aren't allowed")
                    else:
                        inverse_iri = get_iri_from_uriref(inverse_iri_node)
                        obj_prop.add_inverse_property_iri(inverse_iri)

        # OWlDataProperties
        for a in graph.subjects(
                object=rdflib.term.URIRef(
                    "http://www.w3.org/2002/07/owl#DatatypeProperty"),
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):

            if isinstance(a, rdflib.term.BNode):
                self._add_logging_information(LogLevel.WARNING,
                                              IdType.data_property, "unknown",
                                             "Found unparseable statement")

            else:
                # defined in other source -> ignore
                if self._is_object_defined_by_other_source(a, graph):
                    continue

                iri, label, comment = self._extract_annotations(graph, a)

                data_prop = DataProperty(iri=iri, label=label, comment=comment)
                voc_builder.add_data_property(data_prop)

        # OWLDataTypes
        # only the custom created datatype_catalogue are listed in the file,
        # the predefined are automatically added at the start
        # of post processing
        for a in graph.subjects(
                object=rdflib.term.URIRef(
                    "http://www.w3.org/2000/01/rdf-schema#Datatype"),
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):

            if isinstance(a, rdflib.term.BNode):
                # self._add_logging_information(LogLevel.WARNING,
                #                              IdType.datatype, "unknown",
                #                              "Found unparseable statement")
                pass
                #e.g: :
                # customDataType4 rdf:type rdfs:Datatype ;
                # owl:equivalentClass [ rdf:type rdfs:Datatype ;....
                # the second Datatype triggers this if condition,
                # but we can ignore this statement

            else:
                # defined in other source -> ignore
                if self._is_object_defined_by_other_source(a, graph):
                    continue

                iri, label, comment = self._extract_annotations(graph, a)

                datatype = Datatype(iri=iri, label=label, comment=comment)
                voc_builder.add_datatype(datatype=datatype)

                # a datatype can be empty -> use string
                # a datatype can have multiple equivalent classes
                # (predefined types) -> ignore for now
                # a datatype can contain an enum of possible values ->
                # most interesting
                # under the predicate owl:equivalentClass is than a
                # list(first, rest, nil) under the pred.
                # oneOf with the values

                enum_values = []
                for equivalent_class in graph.objects(
                        subject=a,
                        predicate=rdflib.term.URIRef(
                            "http://www.w3.org/2002/07/owl#equivalentClass")):

                    if isinstance(equivalent_class, rdflib.term.URIRef):
                        # points to an other defined datatype, ignore
                        pass
                    else:
                        # is a bNode and points to owl:oneOf
                        enum_literals = self.\
                            _extract_objects_out_of_single_combination(
                                graph, equivalent_class, accept_and=False,
                                accept_or=False, accept_one_of=True)
                        for literal in enum_literals:
                            enum_values.append(str(literal))
                datatype.enum_values = enum_values
                if len(enum_values) > 0:
                    datatype.type = DatatypeType.enum
                else:
                    datatype.type = DatatypeType.string

        # OWLIndividuals

        for a in graph.subjects(
                object=rdflib.term.URIRef(Tags.owl_individual.value),
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):

            if isinstance(a, rdflib.term.BNode):
                self._add_logging_information(LogLevel.WARNING,
                                              IdType.individual, "unknown",
                                             "Found unparseable statement")

            else:
                # defined in other source -> ignore
                if self._is_object_defined_by_other_source(a, graph):
                    continue

                iri, label, comment = self._extract_annotations(graph, a)
                objects = graph.objects(subject=a,
                                        predicate=
                                        rdflib.term.URIRef(Tags.rdf_type.value))
                # superclasses = types
                types = []
                for object in objects:
                    if not object == \
                           rdflib.term.URIRef(Tags.owl_individual.value):
                        types.extend(self.
                            _extract_objects_out_of_layered_combination(
                                        graph, object, True, False))

                individual = Individual(iri=iri, label=label, comment=comment)
                for type in types:
                    individual.parent_class_iris.append(
                        get_iri_from_uriref(type))
                voc_builder.add_individual(individual=individual)

        # As seen for example in the bricks ontology an individual can be
        # declared with :individual1 rdf:type :Class1
        # this type of declaration is hard to completly detect
        # we need to see that the object is a class iri and not a specifier iri.
        # as we may not have loaded all dependencies we can not simply look it
        # up in vocabulary
        # -> getbase uri of statement and filter all known specifier uris
        for sub in graph.subjects(
                predicate=rdflib.term.URIRef(Tags.rdf_type.value)):
            for obj in graph.objects(subject=sub,
                                     predicate=
                                     rdflib.term.URIRef(Tags.rdf_type.value)):

                if isinstance(obj, rdflib.term.BNode):
                    continue
                obj_iri = get_iri_from_uriref(obj)

                obj_base_iri = get_base_out_of_iri(iri=obj_iri)
                if obj_base_iri not in specifier_base_iris:
                    iri, label, comment = \
                        self._extract_annotations(graph, sub)
                    if not voc_builder.entity_is_known(iri):
                        iri, label, comment = \
                            self._extract_annotations(graph, sub)
                        individual = Individual(iri=iri,
                                                label=label,
                                                comment=comment)
                        individual.parent_class_iris.append(obj_iri)
                        voc_builder.add_individual(individual)

    def _extract_annotations(self, graph: rdflib.Graph,
                             node: rdflib.term.URIRef) -> Tuple[str, str, str]:
        """ Extract out of a node term the owl annotations (iri, label, comment)

        Args:
            graph (rdflib.graph): Graph describing ontology
            node (rdflib.term.URIRef): Entity node

        Returns:
            [str,str,str]: [iri, label, comment]
        """
        iri = str(node)
        label = graph.label(node).title()
        comment = graph.comment(node).title()

        return iri, label, comment

    def _parse_subclass_term(self, graph: rdflib.Graph,
                             voc_builder: VocabularyBuilder,
                             node: rdflib.term, class_iri: str):
        """Parse a subclass term of the given node and class_iri

        Args:
            graph (rdflib.graph): Graph describing ontology
            vocabulary (Vocabulary): Vocabualry to parse into
            node (rdflib.term)
            class_iri (str)

        Returns:
            None
        """

        # class could have been only defined in other source, than no class
        # is defined, but as we have found a relation for a class, the class
        # needs to exist
        if class_iri not in voc_builder.vocabulary.classes:
            voc_builder.add_class(class_=Class(iri=class_iri))

        # node can be 1 of 3 things:
        #   - a parentclass statment -> UriRef
        #   - a relation statment -> BNode
        #   - an intersection of parentclasses ,
        #   relations and intersections -> BNode
        if isinstance(node, rdflib.term.BNode):
            # sub has no IRI and is therefore a relation

            # extract the subpredicates and subobjects as statments
            # if node is a relation:
            #      in total there should be 3-4 statments:
            #      rdf:type pointing to owl:Restriction
            #      owl:onProperty pointing to a data or object property
            #      1-2 staments which values are exepted, this can point to an
            #      URIRef or BNode

            # if node is a intersection:
            #      it has the predicate owl:intersectionOf
            #      and a set of objects

            predicates = []
            objects = []
            for p in graph.predicates(subject=node):
                predicates.append(p)
            for o in graph.objects(subject=node):
                objects.append(o)

            # Combination of statements
            if rdflib.term.URIRef(Tags.owl_intersection.value) in predicates:
                objects = self._extract_objects_out_of_single_combination(
                    graph, node, True, False)
                for object in objects:
                    self._parse_subclass_term(graph=graph,
                                              voc_builder=voc_builder,
                                              node=object, class_iri=class_iri)

            elif rdflib.term.URIRef(Tags.owl_union.value) in predicates:
                self._add_logging_information(
                    LogLevel.CRITICAL, IdType.class_, class_iri,
                    "Relation statements combined with or")

            elif rdflib.term.URIRef(Tags.owl_one_of.value) in predicates:
                self._add_logging_information(
                    LogLevel.CRITICAL, IdType.class_, class_iri,
                    "Relation statements combined with oneOf")

            # Relation statement
            else:

                additional_statements = {}
                rdf_type = ""
                owl_on_property = ""

                for i in range(len(predicates)):
                    if predicates[i] == rdflib.term.URIRef(Tags.rdf_type.value):
                        rdf_type = get_iri_from_uriref(objects[i])
                    elif predicates[i] == rdflib.term.URIRef(
                            "http://www.w3.org/2002/07/owl#onProperty"):
                        owl_on_property = get_iri_from_uriref(objects[i])
                    else:
                        additional_statements[
                            get_iri_from_uriref(predicates[i])] = objects[i]

                relation_is_ok = True
                if not rdf_type == "http://www.w3.org/2002/07/owl#Restriction":
                    self._add_logging_information(
                        LogLevel.CRITICAL, IdType.class_, class_iri,
                        "Class has an unknown subClass statement")
                    relation_is_ok = False

                if owl_on_property == "":
                    self._add_logging_information(
                        LogLevel.CRITICAL, IdType.class_, class_iri,
                        "Class has a relation without a property")
                    relation_is_ok = False

                # object or data relation?
                if relation_is_ok:
                    relation = None
                    id = uuid.uuid4().hex
                    # this id can and should be random. a class_iri can have a
                    # property_iri multiple times, to assign always the same id
                    # for the same relation is not worth the trouble

                    relation = Relation(property_iri=owl_on_property, id=id)
                    voc_builder.add_relation_for_class(class_iri, relation)

                    # go through the additional statement to figure out the
                    # targetIRI and the restrictionType/cardinality
                    self._parse_relation_type(graph, relation,
                                              additional_statements)

        # parent-class statement or empty list element
        else:
            # owlThing is the root object, but it is not declared as a class
            # in the file to prevent None pointer when looking up parents,
            # a class that has a parent owlThing simply has no parents
            if not get_iri_from_uriref(node) == \
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                # ignore empty lists
                if not get_iri_from_uriref(node) == \
                       "http://www.w3.org/2002/07/owl#Thing":
                    voc_builder.vocabulary.\
                        get_class_by_iri(class_iri).parent_class_iris.\
                        append(get_iri_from_uriref(node))

    def _parse_relation_type(self, graph: rdflib.Graph,
                             relation: Relation, statements: {}):
        """
        Parse the relation type and depending on the result the
        cardinality or value of relation
        
        Args:
            graph: underlying ontology graph
            relation: Relation object into which the information are saved
            statements: Ontology statements concerning the relation
        
        Returns:
            None
        """
        treated_statements = []
        for statement in statements:
            if statement == "http://www.w3.org/2002/07/owl#someValuesFrom":
                relation.restriction_type = RestrictionType.some
                self._parse_relation_values(graph, relation,
                                            statements[statement])
            elif statement == "http://www.w3.org/2002/07/owl#allValuesFrom":
                relation.restriction_type = RestrictionType.only
                self._parse_relation_values(graph, relation,
                                            statements[statement])
            elif statement == "http://www.w3.org/2002/07/owl#hasValue":
                relation.restriction_type = RestrictionType.value
                # has Value can only point to a single value
                self._parse_has_value(graph, relation,
                                      statements[statement])
            elif statement == "http://www.w3.org/2002/07/owl#maxCardinality":
                relation.restriction_type = RestrictionType.max
                self._parse_cardinality(graph, relation, statement,
                                        statements, treated_statements)
            elif statement == "http://www.w3.org/2002/07/owl#minCardinality":
                relation.restriction_type = RestrictionType.min
                self._parse_cardinality(graph, relation, statement,
                                        statements, treated_statements)
            elif statement == "http://www.w3.org/2002/07/owl#cardinality":
                relation.restriction_type = RestrictionType.exactly
                self._parse_cardinality(graph,  relation, statement,
                                        statements, treated_statements)
            elif statement == \
                    "http://www.w3.org/2002/07/owl#maxQualifiedCardinality":
                relation.restriction_type = RestrictionType.max
                self._parse_cardinality(graph, relation, statement,
                                        statements, treated_statements)
            elif statement == \
                    "http://www.w3.org/2002/07/owl#minQualifiedCardinality":
                relation.restriction_type = RestrictionType.min
                self._parse_cardinality(graph, relation, statement,
                                        statements, treated_statements)
            elif statement == \
                    "http://www.w3.org/2002/07/owl#qualifiedCardinality":
                relation.restriction_type = RestrictionType.exactly
                self._parse_cardinality(graph, relation, statement,
                                        statements, treated_statements)

            treated_statements.append(statement)

        for statement in statements:
            if statement not in treated_statements:
                self._add_logging_information(
                  LogLevel.CRITICAL, IdType.class_, self.current_class_iri,
                  "Relation with property {} has an untreated restriction "
                  "{}".format(relation.property_iri, statement))

    def _parse_cardinality(self, graph: rdflib.Graph,
                           relation: Relation, statement, statements,
                           treated_statements):
        """Parse the cardinality of a relation

        Args:
            graph: underlying ontology graph
            relation: Relation object into which the information are saved
            statement: The statement that is actively treated
            statements: Ontology statements concerning the relation
            treated_statements: Statements that were already treated

        Returns:
            None
        """
        if Tags.owl_on_class.value in statements:
            relation.restriction_cardinality = str(statements[statement])
            target = statements[Tags.owl_on_class.value]
            self._parse_relation_values(graph, relation, target)
            treated_statements.append(Tags.owl_on_class.value)
        elif Tags.owl_on_data_range.value in statements:
            relation.restriction_cardinality = str(statements[statement])
            target = statements[Tags.owl_on_data_range.value]
            self._parse_relation_values(graph, relation, target)
            treated_statements.append(Tags.owl_on_data_range.value)
        else:
            # has From:
            # in File: owl:maxCardinality "1"^^xsd:nonNegativeInteger
            # e.g.: {'http://www.w3.org/2002/07/owl#maxCardinality':
            #        rdflib.term.Literal('1', datatype=
            #        rdflib.term.URIRef('
            #        http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))}

            # in this case the file does not state a datarange that is allowed.
            # Therefore the target gets set to the universal string

            relation.restriction_cardinality = statements[statement].value
            datatype = "http://www.w3.org/2001/XMLSchema#string"
            target_statement = TargetStatement(type=StatementType.LEAF,
                                               target_iri=datatype)
            relation.target_statement = target_statement

    def _parse_has_value(self, graph: rdflib.Graph, relation: Relation,
                         node: rdflib.term):
        """Parse the value of a relation

        Args:
           graph: underlying ontology graph
           relation: Relation object into which the information are saved
           node: (complex) Graph node containing the value
        
        Returns:
           None
        """
        self._parse_relation_values(graph, relation, node)
        # for hasValue only a target-statement that is a leaf is allowed
        if not relation.target_statement.type == StatementType.LEAF:
            self._add_logging_information(
                LogLevel.CRITICAL,
                IdType.class_,
                self.current_class_iri,
                f"In hasValue relation with property {relation.property_iri} "
                f"target is a complex expression")

    def _parse_relation_values(self, graph: rdflib.Graph,
                               relation: Relation, node: rdflib.term):
        """
        Parse the value of a relation out of a node that can be complex;
        consisting out of a combination of multiple other nodes

        Args:
           graph: underlying ontology graph
           relation: Relation object into which the information are saved
           node: (complex) Graph node containing the value

        Returns:
           None
        """
        target_statement = TargetStatement()
        relation.target_statement = target_statement

        queue = [(node, target_statement)]
        while not len(queue) == 0:
            current_term, current_statement = queue.pop(0)
            if isinstance(current_term, rdflib.URIRef):
                target_iri = get_iri_from_uriref(current_term)

                current_statement.set_target(target_iri=target_iri)
            else:
                if rdflib.term.URIRef(Tags.owl_intersection.value) in \
                        graph.predicates(subject=current_term):

                    current_statement.type = StatementType.AND
                elif rdflib.term.URIRef(Tags.owl_union.value) in \
                        graph.predicates(subject=current_term):

                    current_statement.type = StatementType.OR
                else:
                    current_statement.set_target(
                        target_iri="Target statement has no iri",
                        target_data_value=str(current_term))

                    continue

                child_nodes = self._extract_objects_out_of_single_combination(
                    graph, current_term, True, True)
                for child_node in child_nodes:
                    new_statement = TargetStatement()
                    current_statement.target_statements.append(new_statement)
                    queue.append((child_node, new_statement))

    # an intersection/union is a basic list, it consists out of a chain of
    # bnode, where each bnode has the "first"and "rest" predicate, first
    # contains our object, rest is a pointer to the next part of the chain.
    # the list is over if rest points to "NIL"
    # this methode extracts all objects of a single layered intersection,
    # if the intersection contains further intersections these are contained in
    # the result list as BNode
    def _extract_objects_out_of_single_combination(self, graph: rdflib.Graph,
                                                   node: rdflib.term.BNode,
                                                   accept_and: bool,
                                                   accept_or: bool,
                                                   accept_one_of: bool = False):
        """
        An intersection/union is a basic list, it consits out of a chain of
        bnode,where each bnode has the "first"and "rest" predicate,
        first contains our object, rest is a pointer to the next part of the
        chain. The list is over if rest points to "NIL"
        This methode extracts all objects of a single layered intersection,
        if the intersection contains further intersections these are contained
        in the result list as BNode

        Args:
            graph: underlying ontology graph
            node: (complex) Graph node containing the value
            accept_or (bool): true, if combinations with "or" are allowed to be
                parsed
            accept_and (bool): true, if combinations with "and" are allowed
                to be parsed
            accept_one_of (bool): true, if ne_of statements are allowed
                to be parsed

        Returns:
           None
        """
        predicates = list(graph.predicates(subject=node))

        # the passed startnode needs to contain an intersection or a union
        # both at the same time should not be possible
        start_node = None
        if rdflib.term.URIRef(Tags.owl_intersection.value) \
                in predicates:
            if accept_and:
                start_node = next(graph.objects(
                    subject=node,
                    predicate=rdflib.term.URIRef(Tags.owl_intersection.value)))
        elif rdflib.term.URIRef(Tags.owl_union.value) \
                in predicates:
            if accept_or:
                start_node = next(graph.objects(
                    subject=node,
                    predicate=rdflib.term.URIRef(Tags.owl_union.value)))
        elif rdflib.term.URIRef(Tags.owl_one_of.value) \
                in predicates:
            if accept_one_of:
                start_node = next(graph.objects(
                    subject=node,
                    predicate=rdflib.term.URIRef(Tags.owl_one_of.value)))
        else:
            self._add_logging_information(
                LogLevel.CRITICAL, IdType.class_, self.current_class_iri,
                f"Intern Error - invalid {node} passed to list extraction")

        result = []
        rest = start_node
        if start_node is None:
            return []

        while not rest == rdflib.term.URIRef(
                'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'):

            first = next(graph.objects(predicate=rdflib.term.URIRef(
                'http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),
                subject=rest))
            result.append(first)
            rest = next(graph.objects(predicate=rdflib.term.URIRef(
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),
                                      subject=rest))

        return result

    def _extract_objects_out_of_layered_combination(
            self, graph: rdflib.Graph, node: rdflib.term.BNode,
            accept_and: bool, accept_or: bool) -> List[rdflib.term.URIRef]:
        """Extract all nodes out of a complex combination

        Args:
            graph: underlying ontology graph
            node: (complex) Graph node containing the complex combination
            accept_or (bool): true, if combinations with "or" are allowed to be
                parsed
            accept_and (bool): true, if combinations with "and" are allowed
                to be parsed

        Returns:
           List[rdflib.term.URIRef], list of terms out of combination
        """
        result = []
        queue = [node]

        while len(queue) > 0:
            node = queue.pop()
            if isinstance(node, rdflib.term.URIRef):
                result.append(node)
            else:
                queue.extend(self._extract_objects_out_of_single_combination
                             (graph, node, accept_and, accept_or))
        return result

