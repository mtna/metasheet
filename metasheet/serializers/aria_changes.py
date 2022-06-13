import os
import csv
from . import aria

# creates version/property change files between versioned classifications
def generateClassificationChanges(parent, workspace, directory, options=[]):
    print(f"aria: {parent} version changes")
    classifications = getClassifications(workspace, parent)
    extended_properties = findExtendedProperties(workspace, classifications)
        
    # generating base files for initial version of classification
    generateInitialVersionFiles(workspace, directory, classifications, extended_properties)
        
    # generating version/property changes between classifications of the same parent
    for i in range(len(classifications)-1):
        classification_from = classifications[i]
        classification_to = classifications[i+1]
        
        # mapping the code's value to the code itself for quicker lookup
        codes_from = getCodeValueToCodeMap(classification_from, workspace)
        codes_to = getCodeValueToCodeMap(classification_to, workspace)
        
        source_id = classification_from.getPropertyValue("id")
        target_id = classification_to.getPropertyValue("id")
        source_to_targets = getSourceToTargetConcordanceMap(source_id, target_id)
        
        # populating the version_changesand property_changes lists for writing to CSV later
        version_changes = []
        property_changes = []
        findCodeChanges(codes_from, codes_to, version_changes, property_changes, source_to_targets)
        
        # "i + 2" gives us the correct version number of the "to" classification
        v_num = f"v{str(i + 2)}"
        writeVersionChanges(v_num, directory, version_changes, source_id, target_id)
        writeVersionPropertyChanges(v_num, directory, property_changes, extended_properties, source_id, target_id)
        
# identifies the differences between the codes of a classification and the next version of a classification
def findCodeChanges(codes_from, codes_to, version_changes, property_changes, source_to_targets):
    # get a map of target to sources from the source to targets map provided 
    target_to_sources = getTargetToSourcesMap(source_to_targets)
    
    # looking for new codes in the old codes
    for (value_to, code_to) in codes_to.items():
        if value_to in codes_from:
            code_from = codes_from[value_to]
            
            # checking for category break (assumed from difference in label)
            category_break = findLabelDifference(code_from, code_to)
            # self mapping due to category break (i.e. new category)
            if category_break:
                version_change = VersionChange(value_to, code_to.getPropertyValue('parent'), 
                                               value_to, code_to.getName(), code_to.getName('fr'))
                version_changes.append(version_change)
                
            if value_to in target_to_sources:
                sources = target_to_sources[value_to]
                for source in sources:
                    if category_break:
                        if source != value_to:
                            # adding mappings from other sources (except self mapping which was done above)
                            version_change = VersionChange(source, code_to.getPropertyValue('parent'), 
                                                           value_to, code_to.getName(), code_to.getName('fr'))
                            version_changes.append(version_change)
                    else:
                        if (source != value_to):
                            if (len(source_to_targets[source]) > 1):
                                    # adding a mapping if source is split into multiple targets
                                    version_change = VersionChange(source, target=value_to)
                                    version_changes.append(version_change)
                            else:
                                version_change = VersionChange(source, code_to.getPropertyValue('parent'), 
                                                           value_to, code_to.getName(), code_to.getName('fr'))
                                version_changes.append(version_change)
                        else:
                            # self map for when source and target are identical (even labels)
                            version_change = VersionChange(source, target=value_to)
                            version_changes.append(version_change)
            
            # a category break means we can assume all properties from the "code_to" are new, no need to compare to "code_from"
            findPropertyChanges(None if category_break else code_from, code_to, property_changes)
        else:
            if value_to in target_to_sources:
                sources = target_to_sources[value_to]
                for source in sources:
                    # new code from existing source
                    version_change = VersionChange(source, code_to.getPropertyValue('parent'), 
                                               value_to, code_to.getName(), code_to.getName('fr'))
                    version_changes.append(version_change)
            else:
                # new code not found in old codes, must have been added
                version_change = VersionChange(None, code_to.getPropertyValue('parent'), 
                                               value_to, code_to.getName(), code_to.getName('fr'))
                version_changes.append(version_change)
            # if a code is added, so was all of its properties
            findPropertyChanges(None, code_to, property_changes)
        
    # looking for old codes in the new codes
    for (value_from, code_from) in codes_from.items():
        # old code not found in new codes, must have been deleted (if in mappings then it was already deleted)
        if (value_from not in codes_to) and (value_from not in source_to_targets):
            version_change = VersionChange(value_from)
            version_changes.append(version_change)
     
# identifies the differences between the properties of two codes
def findPropertyChanges(code_from, code_to, property_changes):
    property_change = PropertyChange(code_to.getPropertyValue('value'))
    
    # mapping the propertie's name keyed the value for each property in a code for quicker lookup
    properties_from = getPropertyNameToValueMap(code_from)
    properties_to = getPropertyNameToValueMap(code_to)
    
    # looking for new properties in the old properties
    for (name_to, value_to) in properties_to.items():
        # property was added if it didn't exist in the old code or value changed from old code
        if (name_to not in properties_from or (name_to in properties_from and value_to != properties_from[name_to])):
            property_change.addProperty(name_to, value_to)
    
    # looking for old properties in the new properties
    for (name_from, value_from) in properties_from.items():
        # old property is not in new properties, must have been deleted
        if name_from not in properties_to:
            property_change.addProperty(name_from, None)
        
    # only add to list if there were differences in the properties
    if len(property_change.properties) != 0:
        property_changes.append(property_change)
        return True
    return False
            
# writing the version changes
def writeVersionChanges(v_num, directory, version_changes, source_id, target_id):
    print(f"aria: classification {source_id} to {target_id} (version changes)")
    with open(os.path.join(directory, f"{v_num}_changes.csv"), 'w', encoding="utf-8") as outfile:
        # TODO will need changing for dynamic languages
        changes_header = "Source,Parent,Target,Label_en,Label_fr"
        outfile.write(f"{changes_header}\n")
        for version_change in version_changes:
            line = f"{aria.quote(version_change.source)}"
            line += f",{aria.quote(version_change.parent)}"
            line += f",{aria.quote(version_change.target)}"
            line += f",{aria.quote(version_change.label_en)}"
            line += f",{aria.quote(version_change.label_fr)}"
            outfile.write(f"{line}\n")

# writing the version property changes
def writeVersionPropertyChanges(v_num, directory, property_changes, header_properties, source_id, target_id):
    if len(header_properties) != 0:
        print(f"aria: classification {source_id} to {target_id} (version property changes)")
        with open(os.path.join(directory, f"{v_num}_properties.csv"), 'w', encoding="utf-8") as outfile:
            properties_header = "Code"
            # appending possible property names to header
            for header_property in header_properties:
                properties_header += f",{header_property}"
            outfile.write(f"{properties_header}\n")
            
            for property_change in property_changes:
                # only write lines if the codes actually have properties
                line = f"{aria.quote(property_change.code)}"
                for header_property in header_properties:
                    properties = property_change.properties
                    if header_property in properties:
                        line += f",{aria.quote(properties[header_property])}"
                    else:
                        line += ","
                outfile.write(f"{line}\n")
        
# for a code, creates a map of its properties where the property name is keyed to the value
def getPropertyNameToValueMap(code):
    if code is None:
        return {}
    
    properties = {}
    for (key, prop) in code.getProperties().items():
        # skip duplicate/generic properties
        if key not in ('bank','id','parent','level','value') and key not in properties:
            properties[key] = prop['value']
    return properties

# finds any extended properties outside of the generic aria ones to build out the header of the <v#>_properties.csv file
def findExtendedProperties(workspace, classifications):
    header_properties = []
    for classification in classifications:
        codes = workspace.getResources(bank=classification.getBank()+"."+classification.getId(), type="code")
        for code in codes:
            for (prop_name, prop_value) in code.getProperties().items():
                # skip not needed properties
                if prop_name in ('bank','id','parent','level','value') or str.startswith(prop_name, 'name') :
                    continue
                # skip already known properties
                if prop_name in header_properties:
                    continue
                header_properties.append(prop_name)
    return header_properties

# creating the typical files for the initial version of a classification
def generateInitialVersionFiles(workspace, directory, classifications, header_properties):
    # Generate base versions
    with open(os.path.join(directory,"versions.csv"), 'w', encoding="utf-8") as outfile:
        aria.generateClassificationVersions(classifications, workspace, file=outfile)
        
    # Generate base levels
    with open(os.path.join(directory,"levels.csv"), 'w', encoding="utf-8") as outfile:
        aria.generateClassificationLevels(classifications[0], workspace, file=outfile)
        
    # Generate base codes
    with open(os.path.join(directory,"codes.csv"), 'w', encoding="utf-8") as outfile:
        aria.generateClassificationCodes(classifications[0], workspace, file=outfile)
        
    # Generate base code properties
    with open(os.path.join(directory,"properties.csv"), 'w', encoding="utf-8") as outfile:
        aria.generateClassificationCodePropertiesValues(classifications[0], workspace, file=outfile)

# retrieves all classifications belonging to a parent from the workspace
def getClassifications(workspace, parent):
    classifications = []
    for resource in workspace.getResources(type="classification"):
        if parent == resource.getPropertyValue("parent"):
            order = str(resource.getPropertyValue("order"))
            if order:
                classifications.append(resource)
    
    classifications.sort(key=lambda x: x.getPropertyValue("order"))
    return classifications
        
def findLabelDifference(code_from, code_to):
    return (code_to.getName() != code_from.getName() or code_to.getName('fr') != code_from.getName('fr'))

# for a classification, maps all of its codes such that the code's value is keyed to the code object itself
def getCodeValueToCodeMap(classification, workspace):
    codes = workspace.getResources(bank=classification.getBank()+"."+classification.getId(), type="code")
    
    codes_map = {}
    for code in codes:
        value = code.getPropertyValue('value')
        if isinstance(value, int):
            value = str(value)
            
        codes_map[value] = code
    return codes_map

# attempts to find and read a concordance file between two versions of a classification
def getSourceToTargetConcordanceMap(source_version, target_version):
    mappings = {}
    mapping_path = source_version + "_TO_" + target_version + ".maps.csv"
    if os.path.isfile(mapping_path):
        with open(mapping_path, 'r') as mapping_file:
            reader = csv.reader(mapping_file, delimiter=",", quotechar='"')
            # skip header
            next(reader, None)
            for row in reader:
                source = row[0]
                target = row[1]
                if source is not None and target is not None:
                    if source not in mappings:
                        targets = []
                    else:
                        targets = mappings[source]
                    targets.append(target)
                    mappings[source] = targets
    return mappings
        
# maps the target code values to their source code values
def getTargetToSourcesMap(mappings):
    target_to_sources = {}
    for (source, targets) in mappings.items():
        for target in targets:
            if target not in target_to_sources:
                sources = []
            else:
                sources = target_to_sources[target]
            sources.append(source)
            target_to_sources[target] = sources
    return target_to_sources

# object that holds the values to be written to a single row of the <v#>_changes.csv file
class VersionChange:
    def __init__(self, source, parent=None, target=None, label_en=None, label_fr=None):
        self.source = source
        self.parent = parent
        self.target = target
        self.label_en = label_en
        self.label_fr = label_fr
        
# object that holds the values to be written to a single row of the <v#>_properties.csv file
class PropertyChange:
    def __init__(self, code):
        self.code = code
        self.properties = {}
        
    def addProperty(self, name, value):
        self.properties[name] = value
        