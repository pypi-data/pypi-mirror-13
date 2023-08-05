import os, json
from jkspy.modules import hash

class Saveable():
    def __init__(self, *args, **kwargs):
        return super(Saveable, self).__init__(*args, **kwargs)
    
    def save(self):
        attrs = [attr for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self,attr))]
        result = {}
        for attr in attrs:
            aval = getattr(self, attr)
            if type(aval) == Saveable:
                result[attr] = aval.save()
            elif type(aval) in [str, int, float, bool]:
                result[attr] = getattr(self, attr)
        return json.dumps(result)
    
class PWStamp():
    def __init__(self, dtstamp, pw):
        self[dtstamp] = pw

class Keyper():        
    def __init__(self):
        self.status = 'Running'
        return
    
    def save(self):
        newpw = PWStamp('abdadsf','eslkjfleksjf')
        print(json.dumps(newpw))