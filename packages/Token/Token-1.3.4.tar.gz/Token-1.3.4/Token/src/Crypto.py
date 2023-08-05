import random

def generate_keys():
    return (_gen_hex_string(32), _gen_hex_string(32))

def _gen_hex_string(length):
   keys =  ''.join([random.choice('0123456789abcdef') for x in range(length)])
   if False: print(keys)
   return keys
