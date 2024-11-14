"""
Tests for filip.cb.client
"""
import unittest
import logging
from collections.abc import Iterable
from requests import RequestException
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.context import ActionTypeLD, ContextLDEntity, ContextProperty, \
    NamedContextProperty, NamedContextRelationship
from tests.config import settings
import re
import math
from random import Random


# Setting up logging
logging.basicConfig(
    level='ERROR',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


class TestLDQueryLanguage(unittest.TestCase):
    """
    Test class for ContextBrokerClient
    """
    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        #Extra size parameters for modular testing
        self.cars_nb = 10
        self.period = 3
        
        #client parameters
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                        url=settings.LD_CB_URL)
        #base id
        self.base='urn:ngsi-ld:'
        
        #Some entities for relationships
        self.garage = ContextLDEntity(id=f"{self.base}garage0",type=f"{self.base}gar")
        self.cam = ContextLDEntity(id=f"{self.base}cam0",type=f"{self.base}cam")
        
        #Entities to post/test on
        self.cars = [ContextLDEntity(id=f"{self.base}car0{i}",type=f"{self.base}car") for i in range(0,self.cars_nb-1)]
        
        #Some dictionaries for randomizing properties
        self.brands = ["Batmobile","DeLorean","Knight 2000"]
        self.addresses = [
            {
                "country": "Germany",
                "street-address": {
                    "street":"Mathieustr.",
                    "number":10},
                "postal-code": 52072
            },
            {
                "country": "USA",
                "street-address": {
                    "street":"Goosetown Drive",
                    "number":810},
                "postal-code": 27320
            },
            {
                "country": "Nigeria",
                "street-address": {
                    "street":"Mustapha Street",
                    "number":46},
                "postal-code": 65931
            },
        ]

        #base properties/relationships
        self.humidity = NamedContextProperty(name="humidity",value=1)
        self.temperature = NamedContextProperty(name="temperature",value=0);
        self.isParked = NamedContextRelationship(name="isParked",object="placeholder")
        self.isMonitoredBy = NamedContextRelationship(name="isMonitoredBy",object="placeholder")
        
        #q Expressions to test
        #Mixing single checks with op (e.g : isMonitoredBy ; temperature<30)
        #is not implemented
        self.qs = [
            'temperature > 0',
            'brand != "Batmobile"',
            '(isParked | isMonitoredBy); address[stree-address.number]'
            'isParked == "urn:ngsi-ld:garage0"',
            'temperature < 60; isParked == "urn:ngsi-ld:garage"',
            '(temperature >= 59 | humidity < 3); brand == "DeLorean"',
            '(temperature > 30; temperature < 90)| humidity <= 5',
            'temperature.observedAt >= "2020-12-24T12:00:00Z"',
            'address[country] == "Germany"',
            'address[street-address.number] == 810'
        ]
        self.post()
        

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        try:
            entity_list = True
            while entity_list:
                entity_list = self.cb.get_entity_list(limit=1000)
                self.cb.entity_batch_operation(action_type=ActionTypeLD.DELETE,
                                                   entities=entity_list)
        except RequestException:
            pass
        self.cb.close()
    
    def test_ld_query_language(self):
        #Itertools product actually interferes with test results here
        for q in self.qs:
            entities = self.cb.get_entity_list(q=q)
            tokenized,keys_dict = self.extract_keys(q)
            f = self.expr_eval_func
            
            #This means that q expression contains no comparaison operators
            #And should be dealt with as such
            if re.fullmatch('[$\d();|][^<>=!]',tokenized) is not None:
                f = self.single_eval_func
            
            for e in entities:
                bool = f(tokenized,keys_dict,e)
                self.assertTrue(bool)
                
    def extract_keys(self,q:str):
        '''
        Extract substring from string expression that is likely to be the name of a 
        property/relationship of a given entity
        Returns:
            str,dict
        '''
        #First, trim empty spaces
        n=q.replace(" ","")
        
        #Find all literals that are not logical operators or parentheses -> keys/values
        res = re.findall('[^<>=)()|;!]*', n)
        keys = {}
        i=0
        for r in res:
            #Remove empty string from the regex search result
            if len(r) == 0:
                continue
            
            #Remove anything purely numeric -> Definitely a value
            if r.isnumeric():
                continue
            
            #Remove anything with a double quote -> Definitely a string value
            if '"' in r:
                continue
            
            #Replace the key name with a custom token in the string
            token=f'${i}'
            n= n.replace(r,token)
            i+=1
            
            #Flatten composite keys by chaining them together
            l = []
            #Composite of the form x[...]
            if '[' in r:
                idx_st = r.index('[')
                idx_e = r.index(']')
                outer_key = r[:idx_st]
                l.append(outer_key)
                inner_key = r[idx_st+1:idx_e]
                
                #Composite of the form x[y.z...]
                if '.' in inner_key:
                    rest = inner_key.split('.')
                #Composite of the form x[y]
                else :
                    rest = [inner_key]
                l+=rest
            #Composite of the form x.y...
            elif '.' in r:
                l+=r.split('.')
            #Simple key
            else:
                l=[r]
            
            #Associate each chain of nested keys with the token it was replaced with
            keys[token] = l
        
        return n,keys
    
    def sub_key_with_val(self,q:str,entity:ContextLDEntity,keylist:list[str],token:str):
        '''
        Substitute key names in q expression with corresponding entity property/
        relationship values. All while accounting for access of nested properties
        Returns:
            str
        '''
        obj = entity.model_dump()
        for key in keylist:
            if 'value' in obj:
                obj = obj['value']
            obj = obj[key]
            
        if isinstance(obj,Iterable):
            if 'value' in obj:
                obj=obj['value']
            elif 'object' in obj:
                obj=obj['object']
        
        #Enclose value in double quotes if it's a string ( contains at least one letter)
        if re.compile('[a-zA-Z]+').match(str(obj)):
            obj = f'"{str(obj)}"'
        
        #replace key names with entity values
        n = q.replace(token,str(obj))
        
        #replace logical operators with python ones
        n = n.replace("|"," or ")
        n = n.replace(";"," and ")
        
        return n
    
    def expr_eval_func(self,tokenized,keys_dict,e):
        '''
        Check function for the case of q expression containing comparaison operators
        Have to replace the keys with values then call Eval
        '''
        for token,keylist in keys_dict.items():
            tokenized = self.sub_key_with_val(tokenized,e,keylist,token)
        return eval(tokenized)
    
    def single_eval_func(self,tokenized,keys_dict,e):
        '''
        Check function for the case of q expression containing NO comparaison operators
        Only have to check if entity has the key
        '''
        for token,keylist in keys_dict.items():
            level = e.model_dump()
            for key in keylist:
                if 'value' in level:
                    level = level['value']
                if key not in level:
                    return False
                level = level[key]
        
        return True
    
    def post(self):
        '''
        Somewhat randomized generation of data. Can be made further random by 
        Choosing a bigger number of cars, and a more irregular number for remainder
        Calculations (self.cars_nb & self.period)
        Returns:
            None
        '''
        for i in range(len(self.cars)):
            r = i%self.period
            a=r*30
            b=a+30

            #Every car will have temperature, humidity, brand and address
            t = self.temperature.model_copy()
            t.value = Random().randint(a,b)
            
            h = self.humidity.model_copy()
            h.value = Random().randint(math.trunc(a/10),math.trunc(b/10))
            
            self.cars[i].add_properties([t,h,NamedContextProperty(name="brand",value=self.brands[r]),
                                         NamedContextProperty(name="address",value=self.addresses[r])])

            p = self.isParked.model_copy()
            p.object = self.garage.id

            m = self.isMonitoredBy.model_copy()
            m.object = self.cam.id

            #Every car is endowed with a set of relationships , periodically
            r = i % self.period
            if r==0:
                self.cars[i].add_relationships([p])
            elif r==1:
                self.cars[i].add_relationships([m])
            elif r==2:
                self.cars[i].add_relationships([p,m])
    
        #Post everything
        for car in self.cars:
            self.cb.post_entity(entity=car)
