import collections.abc
import ctypes


class IOVector(ctypes.Structure):
	"""
	Some generic "thing that points somewhere" structure from linux/uio.h
	
	© 1994 Allon Cox :-)
	"""
	_fields_ = [
		('base', ctypes.c_void_p),
		('len',  ctypes.c_size_t),
	]
	
	def __init__(self, base = 0, length = 0):
		super().__init__()
		
		self.base = base
		self.len  = length


class Structure(ctypes.Structure):
	def __init__(self, data = None):
		super().__init__()
		
		if data:
			ctypes.memmove(ctypes.addressof(self), data, ctypes.sizeof(self))
	
	def to_dict(self):
		result = {}
		for name, type in self.__class__._fields_:
			result[name] = getattr(self, name)
		return result
	
	@classmethod
	def from_dict(cls, attributes):
		struct = cls()
		for name, type in cls._fields_:
			if name in attributes:
				setattr(struct, name, attributes[name])
		return struct


class EnumerationBase:
	"""
	Base class for all users of the :class:`netlink.struct.misc.Enumeration` meta-class
	"""
	@classmethod
	def get(cls, name):
		if isinstance(name, str):
			return cls[name]
		else:
			return name
	
	@classmethod
	def get_with_iter(cls, names):
		if isinstance(names, str):
			names = (names,)
		if not isinstance(names, collections.abc.Iterable):
			return names
		
		value = 0
		for name in names:
			value |= cls[name]
		return value
	
	@classmethod
	def find(cls, value):
		for name, value2 in cls.__items__.items():
			if value2 == value:
				return name
		
		return value
	
	@classmethod
	def find_bitmask(cls, value):
		names = []
		for name, mask in cls.__items__.items():
			if (value & mask) != 0:
				# Add name to list
				names.append(name)
				
				# Remove bit from value
				value ^= mask
		
		# Add remaining bits as integers to the list
		shift = 0
		while value != 0:
			if (value & 0x01) != 0:
				names.append(1 << shift)
			
			value >>= 1
			shift  += 1
		
		return names


class Enumeration(type):
	"""
	Common base class for all constant list classes
	"""
	def __new__(cls, name, bases, namespace, **kwargs):
		# Add our helper base class as class decendant for this class
		bases += (EnumerationBase,)
		
		# Obtain list of enumeration fields
		fields = namespace['_fields_']
		del namespace['_fields_']
		
		namespace['__items__'] = dict()
		for field in fields:
			if len(field) > 2:
				# Wrapper for the standard integer that adds uses the given documentation string
				# as `__doc__` value
				class Integer(int):
					__slots__ = ()
					__doc__   = field[2]
				
				field_name  = field[0]
				field_value = Integer(field[1])
			else:
				field_name  = field[0]
				field_value = field[1]
			
			field_name = field_name.upper().replace('-', '_')
			namespace['__items__'][field_name] = field_value
		
		# Construct class object
		return type.__new__(cls, name, bases, namespace)
	
	def __getitem__(self, name):
		if isinstance(name, str):
			name = name.upper().replace('-', '_')
		return self.__items__[name]
	
	def __getattr__(self, name):
		return self[name]
