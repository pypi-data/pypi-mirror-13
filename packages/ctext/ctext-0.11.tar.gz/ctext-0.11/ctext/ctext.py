import requests
import json
import re

apiappend = ""

def searchtexts(title):
    global apiappend
    response = requests.get("http://api.ctext.org/searchtexts?title="+title+apiappend).text
    data = json.loads(response)
    return data

def gettext(urn):
    global apiappend
    response = requests.get("http://api.ctext.org/gettext?urn="+urn+apiappend).text
    chapterdata = json.loads(response)
    if('error' in chapterdata):
        raise Exception('CTP API Error', chapterdata['error']['code'], chapterdata['error']['description'])
#    length = None
#    if 'fulltext' in chapterdata:
#        length = len(chapterdata['fulltext'])
#    print("gettext(" + urn + "): " + str(length))
    return chapterdata

#
# Get a text as an array of strings of its subsections
#
def gettextasarray(urn):
    data = gettext(urn)
    asarray = []
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            asarray.append(gettextasstring(data['subsections'][subsec]))
    return asarray


#
# Get a text as an array of strings of all of its paragraphs
#
def gettextasparagrapharray(urn):
    data = gettextasstring(urn)
    asarray = re.compile("\n+").split(data)
    if len(asarray)>0:
        if asarray[-1] == '':
            asarray.pop()
    return asarray


def gettextinfo(urn):
    global apiappend
    response = requests.get("http://api.ctext.org/gettextinfo?urn="+urn+apiappend).text
    chapterdata = json.loads(response)
    return chapterdata

def gettextasobject(urn):
    data = gettext(urn)
    asarray = []
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            subtitle = None
            info = gettextinfo(data['subsections'][subsec])
            if('title' in info):
                subtitle = info['title']
#            print("Will add: " + (data['subsections'][subsec]))
            asarray.append({'title': subtitle, 'fulltext': gettextasstring(data['subsections'][subsec])})
    if('fulltext' in data):
        title = None
        info = gettextinfo(urn)
        if('title' in info):
            title = info['title']
        asstring = ""
        for para in range(0, len(data['fulltext'])):
            asstring = asstring + data['fulltext'][para] + "\n\n"
        asarray.append({'title': title, 'fulltext': asstring})
        return asarray
    return asarray

def gettextasstring(urn):
    data = gettext(urn)
    asstring = ""
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            asstring = asstring + gettextasstring(data['subsections'][subsec])
    if('fulltext' in data):
        for para in range(0, len(data['fulltext'])):
            asstring = asstring + data['fulltext'][para] + "\n\n"
    return asstring

def setapikey(key):
    global apiappend
    apiappend = "&apikey=" + key
    
