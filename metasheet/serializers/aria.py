#
# MOCKAROO GENERATOR
# runtime options (-mockopts):
# - id=<nnn>: a existing schema numeric identifier (for update instead of create)
#
# metasheet columns:
# - mock[type]: Column data type (see https://api.mockaroo.com/api/types?key={{apiKey}})
# - mock[fx]: Column formula (see https://mockaroo.com/help/formulas)
# - mock[min]: min value for Number (default 1)
# - mock[max]: maxn value for Number (default 100)
#


from datetime import datetime
from dateutil import parser
import json
import os.path
import re
import sys

import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

mockaroo_types = None

def generateClassificationCodes(classification, workspace, file=sys.stdout, options=[]):
    # generates add codes file
    print(f"aria: classification {classification.getId()} (codes)")
    if classification:
        codes = workspace.getResources(bank=classification.getBank()+"."+classification.getId(), type="code")
        header = "Code,Parent Code,Label_en,Label_fr"
        file.write(f"{header}\n")
        for code in codes:
                line = quote(code.getPropertyValue('value'))
                line += f",{quote(code.getPropertyValue('parent'))}"
                line += f",{quote(code.getName())}"
                line += f",{quote(code.getName('fr'))}"
                file.write(f"{line}\n")
    else:
        print(f"WARNING: classifcation {classification} not found")
    return

def generateClassificationCodePropertiesValues(classification, workspace, file=sys.stdout, options=[]):
    # generates upadte codes file
    print(f"aria: classification {classification.getId()} (code properties)")
    if classification:
        codes = workspace.getResources(bank=classification.getBank()+"."+classification.getId(), type="code")
        # collect a unique list of all code properties, ignoring the ones excluded from Aria bulk update
        # - the dictionary key is the property
        # - the value is the map (from the config file) in order to determine is this is faceted or i18n
        code_maps = {}
        for code in codes:
            for (key,prop) in code.getProperties().items():
                # skip properties not used for update
                if key in ('bank','id','parent','level','value'):
                    continue
                # skip allready knwon properties
                if key in code_maps:
                    continue
                code_maps[key] = prop['map']
        # process the code properties and organize in a collection of names and facets                
        code_properties = {}
        regex = re.compile("^(?P<property>\\w*)(\\[(?P<facets>.*)\\])?$")
        for (key,map) in code_maps.items():
            # parse key into name/facets
            m = regex.match(key)
            property_name = m.group('property')
            property_facets = m.group('facets')
            if property_facets:
                # convert to array
                property_facets = property_facets.split(',')
            # if this is a generic property, the first facet must be the name
            if property_name == 'property':
                property_name = property_facets[0] # get the name
                property_facets = property_facets[1:] # keep remaining facets, if any
                if len(property_facets) == 0:
                    property_facets = None
            # add to collection
            code_properties[key] = {    'name': property_name, 'facets':property_facets, 'i18n':bool(map.get('i18n')) }
        # print(code_properties)
        # compose CSV header
        csv_header = "Code"
        for (key, property_info) in code_properties.items():
            csv_name = property_info['name']
            if csv_name == 'name': # change 'name' to 'label'
                csv_name = 'Label'
            # language detection
            lang = None
            facets = property_info.get('facets')
            if facets:
                # look for a language (a 2-letter code)
                for facet in facets:
                    if len(facet) == 2:
                        lang = facet
                        break
            if property_info.get('i18n') and not lang:
                lang = 'en' # default to English
            if lang:
                csv_name += '_'+lang
            # add to headerdsi
            csv_header += ','+csv_name.capitalize()
        # write CSV
        file.write(f"{csv_header}\n")
        for code in codes:
                line = quote(code.getPropertyValue('value'))
                for (key, property_info) in code_properties.items():
                    line += f",{quote(code.getPropertyValue(key))}"
                file.write(f"{line}\n")

def generateConcordance(concordance, workspace, file=sys.stdout, options=[]):
    print(f"aria: concordance {concordance.getId()}")
    header = "Source,Target"
    file.write(f"{header}\n")
    # initialize sets to keep track of source and target codes covered by the maps
    mapped_source_codes = set()
    mapped_target_codes = set()
    # 1. generate entries from the concordance maps
    for map in workspace.getResources(bank=concordance.getId(), type="map"):
        source = map.getPropertyValue('source')
        target = map.getPropertyValue('target')
        mapped_source_codes.add(source)
        mapped_target_codes.add(target)
        file.write(f"{source},{target}\n")
    # 2. supplement the concordance map with 1-1 code pairs that were not included (if any)
    # collect 'from' classification source code values
    source_codes = set()
    for code in workspace.getResources(bank=concordance.getPropertyValue("from"), type="code"):
        source_codes.add(code.getPropertyValue("value"))
    # collect 'to' classification source code values
    target_codes = set()
    for code in workspace.getResources(bank=concordance.getPropertyValue("to"), type="code"):
        target_codes.add(code.getPropertyValue("value"))
    # lopp over all codes in 'from' classification
    n_skipped = 0
    n_added = 0
    for code_value in source_codes:
        if code_value in mapped_source_codes:
            # skip as this code is already mapped
            n_skipped += 1
            continue
        if code_value in target_codes:
            # add this pair as the code exist in both classifications
            n_added += 1
            file.write(f"{code_value},{code_value}\n")
    print(f"aria: --> Source codes: {len(source_codes)} | In concordance: {n_skipped} | Autogenerated: {n_added} | Target codes: {len(target_codes)} | Deleted: {len(source_codes - target_codes)} | New: {len(target_codes - source_codes)}")
    return

def generateClassificationLevels(classification, workspace, file=sys.stdout, options=[]):
    print(f"aria: classification {classification.getId()} (levels)")
    if classification:
        levels = workspace.getResources(bank=classification.getBank()+"."+classification.getId(), type="level")
        header = "Level,Concept,Name_en,Name_fr,Auto Sort"
        file.write(f"{header}\n")
        if levels: # hierarchical
            for level in levels:
                line = f"{quote(level.getId())}" # level
                line += f",{quote(level.getPropertyValue('concept') or '?')}" # concept
                line += f",{quote(level.getName())}" # en
                line += f",{quote(level.getName('fr'))}" # fr
                line += f",x" # Auto sort
                file.write(f"{line}\n")
        else: # flat 
            level = classification.getPropertyValue('level') or 'Level 1'
            line = "1" # level
            line += f",{quote(classification.getPropertyValue('concept') or '?')}" # concept
            line += f",{quote(level)}" # en
            line += f",{quote(level)}" # fr
            line += f",x" # Auto sort
            file.write(f"{line}\n")
    else:
        print(f"WARNING: classifcation {classification} not found")
    return

def generateClassificationVersions(classifications, workspace, file=sys.stdout, options=[]):
    if not isinstance(classifications,list):
        classifications = [classifications]
    print(f"aria: classification versions")
    header = "Name_en,Name_fr,Abbreviation_en,Abbreviation_fr,ID,Version,Valid From,Valid To,Audience,Status"
    file.write(f"{header}\n")
    count = 0
    for classification in classifications:
        count += 1
        # version
        version = classification.getPropertyValue('version') or f"{count}.0.0"
        # validFrom
        validFrom_date = datetime(1900,1,count)
        if classification.getPropertyValue('validFrom'):
            validFrom_date = parser.isoparse(str(classification.getPropertyValue('validFrom')))
        else:
            print(f"   warning:{classification.getId()} dateFrom property not set!")
        validFrom = validFrom_date.strftime('%Y%m%d')
        # validTo
        validTo = ""
        if classification.getPropertyValue('validTo'):
            validTo_date = parser.isoparse(str(classification.getPropertyValue('validTo')))
            validTo = validTo_date.strftime('%Y%m%d')
        # write
        line = f"{quote(classification.getName())}" # en
        line += f",{quote(classification.getName('fr'))}" # fr
        line += f"," # abbr en
        line += f"," # abbr fr
        line += f"," # ID
        line += f",{version}" # version
        line += f",{validFrom}" # valid from 
        line += f",{validTo}" # valid to
        line += f",Public" # audience
        line += f",Released" # status
        file.write(f"{line}\n")
    return

def quote(value):
    if(value):
        if isinstance(value, str):
            csv_value = value.replace("\"","\"\"")
        else:
            csv_value = value
        return(f"\"{csv_value}\"")
    else:
        return ""

