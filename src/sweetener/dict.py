
def omit(mapping, *keys):
     result = dict()
     for k, v in mapping.items():
         if k not in keys:
             result[k] = v
     return result

