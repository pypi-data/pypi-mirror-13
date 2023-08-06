import os, random, math, string, datetime, base64, \
        requests, re, json, io, importlib, \
        pytz, PIL

## Code Helpers
def importFromString(pyurl):
    """ Imports python module from the string argument """
    return importlib.import_module(pyurl)

## File functions
def readFile(filepath, bytestring=False):
    if bytestring:
        f = open(filepath, 'rb')
    else:
        f = open(filepath, 'r')
    content = f.read()
    f.close()
    return content

def writeFile(filepath, content, bytestring=False):
    if bytestring:
        cfile = open(filepath, 'wb')
    else:
        cfile = open(filepath, 'w')
    cfile.write(content)
    cfile.close()
    print("File ["+filepath+"] successfully created.")


## CORS functions
def imageToDataURL(image_url):
    response = requests.get(image_url)
    image = PIL.Image.open(io.BytesIO(response.content))
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    contents = buffer.getvalue()
    b64str = 'data:image/png;base64,'+str( base64.b64encode(contents).decode() )
    buffer.close()
    return b64str

##### Maths
def roundFloat(fnum, digits=2):
    return float(('{0:.'+str(digits)+'f}').format(fnum))


##### List Processing Functions
def shuffleList(old_list):
    new_list = old_list.copy()
    random.shuffle(new_list)
    return new_list


#### Validators
#### returns True or False
def validateEmail(email):
    validated = re.match('^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                         email)
    return not not validated

#### For Debugging
def dprint(obj, depth=2, obj_key='', indent=''):
    """ for debugging purposes d(ebug)print """
    if depth >= 0:
        if hasattr(obj, '__dict__') or type(obj) == dict:
            if type(obj) == dict:
                items = obj.items()
            else:
                items = obj.__dict__.items()            
            print(indent+'('+str(type(obj))+') '+obj_key+': {')
            for key, val in items:
                dprint(val, depth-1, key, indent+'    ')
            print(indent+'},')
        
        elif hasattr(obj, '__call__'):
            print(indent+'(function) '+obj_key+': '+str(obj)+',')
                
        else:
            print(indent+'('+str(type(obj))+') '+obj_key+': '+str(obj)+',')
            
    #     return { key: getattr(obj, key) for key in dir(obj) }
        return obj

def strToInt (s):
    return int.from_bytes(s.encode(), 'little')

def intToStr (n):
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()