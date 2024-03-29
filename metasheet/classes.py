__all__ = ["Workspace", "Resource"]

from collections import OrderedDict
import copy
import string
import random
import re
import uuid

#====================================================================
# WORKSPACE CLASS
#====================================================================
class Workspace:
    def __init__(self):
        self.resources = OrderedDict()
        self.resolver_cache = {}
        self.resolver_cache_hit = 0
        self.resolver_cache_miss = 0
        self.resource_type_count = {}

    def addResource(self, resource):
        self.resources[resource.uid] = resource
        type = resource.getType()
        if type in self.resource_type_count:
            self.resource_type_count[type] += 1
        else:
            self.resource_type_count[type] = 1
            
    def dump(self, type=None):
        print("WORKSPACE DUMP")
        for uid, resource in self.resources.items():
            if type is None or resource.getType() == type:
                resource.dump()

    def generateConcordanceBankId(self, fromId, toId):
        """Helper to generate a concordance bank indentifier using the from and to classification identifiers"""
        return f"{fromId}_TO_{toId}"

    def generateConcordanceMapId(self, fromValue, toValue):
        """Helper to generate a concordance map indentifier using the source and target values"""
        return f"{fromValue}_TO_{toValue}"

    def getResources(self, bank=None, name=None, id=None, type=None):
        """Search and returns resources"""
        resources = []

        # split bank reference
        if bank and '.' in bank:
            tokens = bank.rsplit('.', 1)
            bankId = tokens[1]
        else:
            bankId = bank

        for uid, resource in self.resources.items():
            if bank:
                if "." in resource.getBank():
                    if resource.getBank() != bank:
                        continue
                else: # check bankId match
                    if resource.getBank() != bankId:
                        continue
            if id and resource.getId() != id:
                continue
            if name and resource.getName() != name:
                continue
            if type and resource.getType() != type:
                continue
            # match
            resources.append(resource)
        return resources

    def inheritProperties(self, resource=None, reset=False):
        """Resolve basis and inherit properties. Applies to all resource if none specified"""
        if resource is None:
            # All resources
            if reset:
                for resource in self.resources.values():
                    resource.inheritanceCompleted = False
            for resource in self.resources.values():
                self.inheritProperties(resource)
        else:
            # Resource
            if reset:
                resource.inheritanceCompleted = False
            if not resource.inheritanceCompleted:
                if resource.getBasis() is not None:
                    try:
                        # only inherit from same data type
                        resource_type = resource.getType()
                        if resource_type == "layout": # layout inherit from a variable (not another layout)
                            resource_type = "variable"
                        parent = self.resolve(resource.getBasis(), resource_type)
                    except RuntimeError as err:
                        print("RESOLVING BASIS")
                        resource.dump()
                        raise RuntimeError(err)
                    if parent:
                        if not parent.inheritanceCompleted and parent.hasProperty("basis"):
                            # recurse
                            self.inheritProperties(parent, reset=reset)
                        else:
                            pass # parent has no basis or is inheritance readily completed
                        # add parent inheritable properties on this resource as needed
                        for property, entry in parent.getProperties().items():
                            if not resource.hasProperty(property):
                                if property not in ["basis", "id", "bank"]:
                                    resource.addPropertyEntry(property, entry, inherited=True)
                                else:
                                    pass # not inheritable
                            else:
                                pass
                    else:
                        resource.dump()
                        raise RuntimeError("Unable to resolve basis for "+str(resource.getId()))
                else:
                    pass # resource has no basis
            else:
                pass # inheritance already processed

    def stats(self):
        """Displays workspace statistics"""
        print("#resources:", len(self.resources))
        for resource_type, n in self.resource_type_count.items():
            print("#"+resource_type,n)
        print("Resolver cache: "+str(self.resolver_cache_hit)+" hits / "+str(self.resolver_cache_miss)+" misses")
        
    def resolve(self, reference, type=None):
        """Finds a resource by reference (bank+id).
        A runtime error will be thrown if more than one match if found
        """
        #print("Resolving", reference, "as", type)
        # get reference components

        resolved = None
        if reference in self.resolver_cache:
            # found in cache
            self.resolver_cache_hit += 1
            resolved = self.resolver_cache[reference]
        else:
            # lookup
            self.resolver_cache_miss += 1
            if '.' in reference:
                tokens = reference.rsplit('.', 1)
                bank = tokens[0]
                id = tokens[1]
            else:
                bank = None
                id = reference
            # resolve
            for uid, resource in self.resources.items():
                if type and resource.getType() != type:
                    continue # skip: type mismatch
                if resource.getId() == id:
                    # id matches
                    if bank and resource.getBank() != bank:
                        continue # skip: bank mismatch
                    if resolved is None:
                        resolved = resource
                    else:
                        print("Resolved")
                        resolved.dump()
                        print("Duplicate")
                        resource.dump()
                        raise RuntimeError("Multiple macthes found while resolving "+reference+"["+str(type)+"]")
                else:
                    pass
            # add to cache
            self.resolver_cache[reference] = resolved
        return resolved

#====================================================================
# RESOURCE CLASS
#====================================================================
class Resource:
    
    def __init__(self,type,source):
        self.source=source # where is this resource coming from 
        self._properties=OrderedDict() # local properties
        self._inheritedProperties=set() # the names of the inherited
        #self.uid = uuid.uuid4() # unique id
        self.uid = ''.join([random.choice(string.ascii_letters+string.digits) for ch in range(12)])
        self._type=type # resource type
        self.inheritanceCompleted=False #inheritance has been applied 

    def addProperty(self,property,value,map,inherited=False):
        """Adds a property name/value/map """
        self.addPropertyEntry(property,{"name":property,"value":value,"map":map})
        
    def addPropertyEntry(self,property,entry,inherited=False):
        #print("Adding property",property,entry)
        
        """Adds a property entry"""
        # a property entry contain {name,value,map}
        if not self.validateProperty(property,entry):
            raise RuntimeError(self.getSource(),"- Invalid property or value specified")
        
        self._properties[property]=entry
        # set name as id is not readily set
        if property=="name" and not self.hasProperty("id"):
            self.copyProperty("name","id")

        if inherited:
            self._inheritedProperties.add(property)
        else:
            self._inheritedProperties.discard(property);

    def clone(self):
        """Creates a deep copy of this resources with a new uid"""
        clone = copy.deepcopy(self)
        clone.uid = ''.join([random.choice(string.ascii_letters+string.digits) for ch in range(12)])
        return clone

    def copyProperty(self,source,target):
        prop = self._properties.get(source)
        if prop:
            prop["name"]=target
            self._properties[target]=prop

    def dump(self):
        print(self._type,self.uid,self.source)
        for property in self._properties:
            if property in self.getInheritedPropertiesKeys():
                print("...",property,"*",str(self._properties.get(property)))
            else:
                print("...",property,str(self._properties.get(property)))
                
    def getBank(self):
        return self.getPropertyValue("bank")

    def getBasis(self):
        return self.getPropertyValue("basis")

    def getFacetedPropertyFacets(self, prop):
        "Returns the facets found for the specified property"
        facets = set()
        for key in self.getPropertiesKeys():
            if key.startswith(prop+'['):
                m = re.search(r"\[(.*)\]",key)
                facets.add(m.group(1))
        return facets

    def getFacetedPropertyLanguage(self, prop):
        "Returns the ISO639 language if found for the specified property"
        facets =  self.getFacetedPropertyFacets(prop)
        for facet in facets:
            # simply assume any 2-letter facet value is a language code
            # @todo improve implementation of language
            if len(facet) == 2:
                return facet
        return None

    def getFacetedPropertyValue(self, prop, fallback=True):
        """Return the property or its unfaceted value if fallback is set (default).
           Mulitple facets must be provided unsing the internal syntax prop[facet1][facet2]...[facetN]
        """
        basename = prop.split('[')[0]
        facets = re.findall(r"\[(.*?)\]",prop)
        nFacets = len(facets)
        facetedValues = self.getFacetedPropertyValues(basename)
        matchedValue = None
        nMatchedFacets = 0
        if nFacets > 0: # confirm this is a feceted property
            # iterate over all values and find best match
            for facetedValue in facetedValues:
                valueFacets = facetedValue['facets']
                nValueFacets = len(valueFacets)
                # count how many facets match
                nValueMatchedFacets = 0
                for facet in facets:
                    if facet in valueFacets:
                        nValueMatchedFacets += 1
                # compare
                if nValueMatchedFacets == nFacets:
                    # we have an exact match
                    matchedValue = facetedValue['value']
                    nMatchedFacets = nValueMatchedFacets
                    break # we're done
                elif nValueMatchedFacets <= nFacets:
                    # we have an under match --> use this if it is an improvement
                    if nValueMatchedFacets > nMatchedFacets:
                        matchedValue = facetedValue['value']
                        nMatchedFacets = nValueMatchedFacets
                else:
                    # we have an over match
                    pass
        if matchedValue is None and fallback:
            matchedValue = self.getPropertyValue(basename)
        return matchedValue

    def getFacetedPropertyValues(self, baseprop):
        "Return an array of objects holding the values and their facets found for this base property"
        values = []
        for key in self.getPropertiesKeys():
            if key.startswith(baseprop+'['): 
                facets = re.findall(r"\[(.*?)\]",key)
                values.append({'key':key, 'facets':facets,'value':self.getPropertyValue(key)})
        return values

    def getId(self):
        return self.getPropertyValue("id")

    def getDescription(self,facets=None):
        prop = 'description'
        if facets: prop += f"[{facets}]"
        return self.getFacetedPropertyValue(prop)

    def getName(self,facets=None):
        prop = 'name'
        if facets: prop += f"[{facets}]"
        return self.getFacetedPropertyValue(prop)

    def getLabel(self, facets=None):
        prop = 'name[label]'
        if facets: prop += f"[{facets}]"
        return self.getFacetedPropertyValue(prop)

    def getProperties(self):
        return self._properties

    def getPropertiesKeys(self):
        return self._properties.keys()
        
    def getInheritedPropertiesKeys(self):
        """Set of inherited properties"""
        return self._inheritedProperties;
        
    def getLocalPropertiesKeys(self):
        """Set of locally defined properties"""
        return set(self._properties.keys()) - self._inheritedProperties
        
    #def getPropertiesValues(self):
    #    return self._properties.values()

    def getProperty(self, prop):
        """Returns the specified property"""
        return self.getPropertyEntry(prop)

    def getPropertyEntry(self,prop):
        """Returns the specified property"""
        return self._properties.get(prop)

    def getPropertyValue(self,prop):
        """Returns the specified property value"""
        entry=self.getPropertyEntry(prop)
        if entry:
            return entry.get("value")

    def getReference(self):
        return self.getBank()+"."+self.getId()

    def getSource(self):
        return self.getPropertyValue("source")

    def getType(self):
        return self._type

    def hasProperties(self):
        """Returns true if resource has at least one property"""
        return len(self._properties)>0

    def hasProperty(self,prop):
        """Returns true if resource carries the specified property"""
        return prop in self._properties

    def setProperty(self,property,value,map,inherited=False):
        self.addProperty(property,value,map,inherited)

    def setPropertyValue(self,prop,value):
        """Sets the specified property value"""
        entry=self.getPropertyEntry(prop)
        if entry:
            entry["value"] = value

    def validateProperty(self,property,entry):
        isValid=True
        if "name" not in entry:
            print(self.source,"Invalid: no 'name' provided for "+property)
            isValid=False
        if "value" not in entry:
            print(self.source,"Invalid: no 'value' provided for "+property)
            isValid=False
        if "map" not in entry:
            print(self.source,"Invalid: no 'map' provided for "+property)
            isValid=False
        # positive integers
        if property in ["end","start","width"]:
            value =  entry.get("value")
            if not isinstance(value,int) and (isinstance(value,str) and not value.isdigit()):
                print(self.source,"Invalid: non-numeric value specified for "+property)
                isValid=False
        return isValid
        
