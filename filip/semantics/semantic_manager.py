
class SemanticManager():

    def create_vocabulary(self):
        pass


    def add_ontology_to_vocabulary_as_file(self, path_to_file: str) -> bool:
        parser = RdfParser()
        parser.parse_source_into_vocabulary()

    def add_ontology_to_vocabulary_as_file(self, source_name: str,
                                           source_content: str):
        source = Source(source_name=source_name,
                        content=source_content,
                        timestamp=datetime.datetime.now())

        backup = copy.deepcopy(self)

        parser = RdfParser()
        parser.parse_source_into_vocabulary(vocabulary=self, source=source)
        self.__dict__.update(backup.__dict__)

