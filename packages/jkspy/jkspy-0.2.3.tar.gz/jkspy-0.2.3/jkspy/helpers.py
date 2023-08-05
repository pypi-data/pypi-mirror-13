import os, random, string, datetime, base64, requests, pytz, PIL, re, json, io

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