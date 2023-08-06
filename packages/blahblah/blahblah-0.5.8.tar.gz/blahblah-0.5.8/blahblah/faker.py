import random
import string
import exrex
import district42.json_schema
from time import time
from datetime import datetime


class Faker(district42.json_schema.AbstractVisitor):

  primitives = (
    district42.json_schema.integer,
    district42.json_schema.float,
    district42.json_schema.string
  )

  def __get_length(self, schema):
    if 'length' in schema._params:
      return schema._params['length']

    min_length, max_length = 0, 64

    if ('contains' in schema._params) or ('contains_one' in schema._params):
      min_length = 1
    if 'contains_many' in schema._params:
      min_length = 2

    if 'min_length' in schema._params:
      min_length = schema._params['min_length']
    if 'max_length' in schema._params:
      max_length = schema._params['max_length']

    return random.randint(min_length, max_length)

  def __get_alphabet(self, schema):
    if 'lowercase' in schema._params:
      alphabet = string.ascii_lowercase
    elif 'uppercase' in schema._params:
      alphabet = string.ascii_uppercase
    else:
      alphabet = string.ascii_letters
    
    if 'alphabetic' in schema._params:
      return alphabet
      
    if 'alpha_num' in schema._params:
      return alphabet + string.digits

    return alphabet + string.digits + '-_'

  def __get_object_key(self):
    return district42.json_schema.string.alphabetic.lowercase.length(1).accept(self) + \
           district42.json_schema.string.alpha_num.lowercase.length(1, 15).accept(self)
  
  def __is_required(self, schema):
    return 'required' not in schema._params or schema._params['required']

  def __is_undefined(self, schema):
    return type(schema) is district42.json_schema.types.Undefined

  def __get_predicate(self, schema):
    if 'predicate' in schema._params:
      return schema._params['predicate']
    return (lambda a, b: a != b)

  def __is_elem_unique(self, elem, array, predicate):
    for x in array:
      if not predicate(elem, x):
        return False
    return True

  def __generate_unique_elem(self, schema, array, predicate):
    elem = schema.accept(self)
    if self.__is_elem_unique(elem, array, predicate):
      return elem
    return self.__generate_unique_elem(schema, array, predicate)

  def visit_null(self, schema, *args):
    return None

  def visit_boolean(self, schema, *args):
    if args: return args[0]

    if 'value' in schema._params:
      return schema._params['value']

    if 'examples' in schema._params:
      return random.choice(schema._params['examples']) 

    return random.choice((True, False))

  def visit_number(self, schema, *args):
    if args: return args[0]

    if 'value' in schema._params:
      return schema._params['value']

    if 'examples' in schema._params:
      return random.choice(schema._params['examples'])

    min_value, max_value = -2147483648, 2147483647
    if 'min_value' in schema._params:
      min_value = schema._params['min_value']
    if 'max_value' in schema._params:
      max_value = schema._params['max_value']
    if 'float' in schema._params:
      min_value, max_value = float(min_value), float(max_value)
      return random.uniform(min_value, max_value)

    if 'multiple' in schema._params:
      base = schema._params['multiple']
      return random.randint(min_value // base, max_value // base) * base
    
    return random.randint(min_value, max_value)

  def visit_string(self, schema, *args):
    if args: return args[0]

    if 'value' in schema._params:
      return schema._params['value']

    if 'examples' in schema._params:
      return random.choice(schema._params['examples'])

    if 'uri' in schema._params:
      return 'http://localhost/'

    if 'pattern' in schema._params:
      return exrex.getone(schema._params['pattern'])

    if 'numeric' in schema._params:
      return str(random.randint(0, 9223372036854775807))

    length = self.__get_length(schema)
    alphabet = self.__get_alphabet(schema)
    return ''.join([random.choice(alphabet) for x in range(length)])

  def visit_timestamp(self, schema, *args):
    if args: return args[0]

    if 'examples' in schema._params:
      return random.choice(schema._params['examples'])

    min_value, max_value = 0, int(time())
    if 'min_value' in schema._params:
      min_value = int(schema._params['min_value'].epoch())
    if 'max_value' in schema._params:
      max_value = int(schema._params['max_value'].epoch())

    if 'value' in schema._params:
      timestamp = datetime.utcfromtimestamp(schema._params['value'].epoch())
    else:
      timestamp = datetime.utcfromtimestamp(random.randint(min_value, max_value))

    if 'iso' in schema._params:
      return timestamp.isoformat()

    if 'format' in schema._params:
      return timestamp.strftime(schema._params['format'])

    return str(timestamp)

  def visit_array(self, schema, *args):
    if args: return args[0]

    if 'examples' in schema._params:
      return random.choice(schema._params['examples'])

    if 'items' in schema._params:
      if 'unique' in schema._params and schema._params['unique']:
        predicate = self.__get_predicate(schema)
        unique_array = []
        for item in schema._params['items']:
          unique_array += [self.__generate_unique_elem(item, unique_array, predicate)]
        return unique_array
      return [item.accept(self) for item in schema._params['items']]

    length = self.__get_length(schema)

    if 'contains_one' in schema._params:
      array = [schema._params['contains_one'].accept(self)]
      while len(array) < length:
        primitive = random.choice(self.primitives).accept(self)
        if primitive not in array:
          array.append(primitive)
      if length > 1:
        index = random.randint(1, length - 1)
        array[0], array[index] = array[index], array[0]
      return array

    array = []
    if 'contains' in schema._params:
      count = random.randint(1, length)
      array += [schema._params['contains'].accept(self) for x in range(count)]
    elif 'contains_many' in schema._params:
      count = random.randint(2, length)
      array += [schema._params['contains_many'].accept(self) for x in range(count)]
    elif 'unique' in schema._params and schema._params['unique']:
      primitive = random.choice(self.primitives)
      predicate = self.__get_predicate(schema)
      unique_array = [primitive.accept(self)]
      while len(unique_array) != length:
        elem = primitive.accept(self)
        if self.__is_elem_unique(elem, unique_array, predicate):
          unique_array.append(elem)
      return unique_array

    length -= len(array)
    return array + [random.choice(self.primitives).accept(self) for x in range(length)]

  def visit_array_of(self, schema, *args):
    if args: return args[0]

    if 'examples' in schema._params:
      return random.choice(schema._params['examples'])

    length = self.__get_length(schema)
    if 'unique' in schema._params and schema._params['unique']:
      predicate = self.__get_predicate(schema)
      unique_array = [schema._params['items_schema'].accept(self)]
      while len(unique_array) != length:
        elem = schema._params['items_schema'].accept(self)
        if self.__is_elem_unique(elem, unique_array, predicate):
          unique_array.append(elem)
      return unique_array
    
    return [schema._params['items_schema'].accept(self) for x in range(length)]

  def visit_object(self, schema, *args):
    if not args and 'examples' in schema._params:
      return random.choice(schema._params['examples'])
    
    obj = {}
    if 'keys' in schema._params:
      for key, item_schema in schema._params['keys'].items():
        if args and key in args[0]:
          if self.__is_undefined(item_schema):
            obj[key] = args[0][key]
          else:
            obj[key] = item_schema.accept(self, args[0][key])
        elif not self.__is_undefined(item_schema) and self.__is_required(item_schema):
          obj[key] = item_schema.accept(self)

    if ('keys' not in schema._params) or (len(schema._params['keys']) > 0):
      if len(obj) == 0 or any(x in schema._params for x in ['length', 'min_length', 'max_length']):
        length = self.__get_length(schema) - len(obj)
        for x in range(length):
          key = self.__get_object_key()
          obj[key] = random.choice(self.primitives).accept(self)

    return obj

  def visit_any(self, schema, *args):
    if args: return args[0]
    return random.choice(self.primitives).accept(self)

  def visit_any_of(self, schema, *args):
    if args: return args[0]
    return random.choice(schema._params['options']).accept(self)

  def visit_one_of(self, schema, *args):
    if args: return args[0]
    return random.choice(schema._params['options']).accept(self)

  def visit_enum(self, schema, *args):
    if args: return args[0]
    return random.choice(schema._params['enumerators'])

  def visit_undefined(self, schema, *args):
    raise NotImplementedError()
