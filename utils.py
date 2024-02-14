from json import JSONEncoder
from typing import Any

def get_safe(obj, key, default = None):
    if obj is None: return default
    # if isinstance(obj, str): return obj.get(key).encode('utf-8')
    if isinstance(obj, bytes): raise Exception(f"{str(obj._)} is bytes!") # return obj.get(key).decode('utf-8')
    return obj.get(key, default)

class jsencoder(JSONEncoder):
        def default(self, o: Any): # lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
            if not o: return None
            print(str(o))
            if isinstance(o, bytes): return o.decode('utf-8')
            elif isinstance(o, dict): return {key: value for key, value in o.items() if value}
            elif isinstance(o, list): return [value for value in o if value]
            elif isinstance(o, tuple): return tuple(value for value in o if value)
            try: return JSONEncoder.default(self, o)
            except: return o.__dict__ 