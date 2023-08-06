import ctypes
import math
import ipaddress
import socket
import sys

import netlink.struct.netlink


class AttributeDecoder:
	AttributeType = netlink.struct.netlink.Attribute
	
	types = {}
	
	@staticmethod
	def ALIGN(size):
		return math.ceil(size / 4) * 4
	
	
	def __init__(self, message = None):
		self.message = message
		
		self.decoders = {}
		self.encoders = {}
		for prop in dir(self):
			if prop.startswith('attribute_decode_'):
				type = prop.split('_', 2)[2]
				func = getattr(self, prop)
				
				self.decoders[type] = func
			
			if prop.startswith('attribute_encode_'):
				type = prop.split('_', 2)[2]
				func = getattr(self, prop)
				
				self.encoders[type] = func
	
	def attribute_decode_str(self, data):
		"""Decode a C byte string to a Python string"""
		return data[:-1].decode('utf-8')
	
	def attribute_encode_str(self, string):
		"""Encode a Python string to a C byte string"""
		return string.encode('utf-8') + b'\x00'
	
	def attribute_decode_bool(self, data):
		"""Decode boolean value from a binary 8-bit number"""
		return bool(self.attribute_decode_int_u8(data))
	
	def attribute_encode_bool(self, state):
		"""Encode boolean value to a binary 8-bit number"""
		return self.attribute_encode_int_u8(int(state))
	
	def attribute_decode_int(self, data):
		"""Decode a binary integer in host byte order into a Python int"""
		return int.from_bytes(data, sys.byteorder)
	attribute_decode_int_u8  = attribute_decode_int
	attribute_decode_int_u16 = attribute_decode_int
	attribute_decode_int_u32 = attribute_decode_int
	attribute_decode_int_u64 = attribute_decode_int
	
	def attribute_encode_int_u8(self, number):
		return int(number).to_bytes(1, sys.byteorder)
	
	def attribute_encode_int_u16(self, number):
		return int(number).to_bytes(2, sys.byteorder)
	
	def attribute_encode_int_u32(self, number):
		return int(number).to_bytes(4, sys.byteorder)
	
	def attribute_encode_int_u64(self, number):
		return int(number).to_bytes(8, sys.byteorder)
	
	def decode_address(self, data, family):
		"""
		Decode a network address
		
		The address will be decoded to an IPv4, IPv6 or MAC address string depending on its length
		and the given address family value.
		
		Parameters
		----------
		data : bytes
			Binary representation of the address
		family : int
			The address family that this address (probably) belongs to
		
		Returns
		-------
		str
		"""
		if len(data) == 4 and family == socket.AF_INET:
			return str(ipaddress.IPv4Address(data))
		elif len(data) == 16 and family == socket.AF_INET6:
			return str(ipaddress.IPv6Address(data))
		else:
			return ':'.join("{0:02X}".format(b) for b in data)
	
	def encode_address(self, address, family):
		if family == socket.AF_INET:
			return ipaddress.IPv4Address(address).packed
		elif family == socket.AF_INET6:
			return ipaddress.IPv6Address(address).packed
		else:
			hex_bytes = address.translate({ord(':'): None, ord('-'): None})
			return int(hex_bytes, 16).to_bytes(len(hex_bytes) / 2, sys.byteorder)
	
	def decode_single_type(self, type):
		"""
		Convert the given type integer constant to (hopefully) a human-readable string
		
		Parameters
		----------
		type : int
			The type constant as Python ``int``
		
		Returns
		-------
		:func:`int` | :func:`str`
		"""
		if hasattr(self.AttributeType, 'TYPE'):
			return self.AttributeType.TYPE.find(type)
		else:
			return type
	
	def encode_single_type(self, type):
		if hasattr(self.AttributeType, 'TYPE'):
			return self.AttributeType.TYPE.get(type)
		else:
			return type
	
	def decode_single(self, type, data):
		"""
		Convert the given type and binary data to Pythonic, human-readable values
		
		This method calls :meth:`~netlink.low.netlinkattrib.AttributeDecoder.decode_single_type`
		internally to decode the ``type`` parameter.
		
		Parameters
		----------
		type : int
			The type constant as Python ``int``
		data : bytes
			Binary data produced by the kernel
		
		Returns
		-------
		( :func:`int` | :func:`str` , :func:`bytes` | :func:`object` )
		"""
		name = self.decode_single_type(type)
		
		# Determine decoder name for this attribute type
		decoder_name = None
		if name in self.types:
			decoder_name = self.types[name]
		
		# Determine decoding function for this attribute type
		decoder_func = lambda data: data
		if decoder_name in self.decoders:
			decoder_func = self.decoders[decoder_name]
		
		# Do the decoding
		value = decoder_func(data)
		
		return (name, value)
	
	def encode_single(self, name, value):
		if isinstance(value, bytes):
			type = self.encode_single_type(name)
			return (type, value)
		else:
			# Determine decoder name for this attribute type
			encoder_name = None
			if name in self.types:
				encoder_name = self.types[name]
		
			# Determine encoding function for this attribute type
			encoder_func = lambda data: data
			if encoder_name in self.encoders:
				encoder_func = self.encoders[encoder_name]
		
			# Do the encoding
			type = self.encode_single_type(name)
			data = bytes(encoder_func(value))
		
			return (type, data)
	
	def decode(self, data):
		"""
		Decode the given attribute stream into a dictionary
		
		Parameters
		----------
		data : bytes
			Byte voodo, as produced by the Linux kernel
		
		Returns
		-------
		dict
		"""
		offset    = 0
		attribute = self.AttributeType()
		
		attributes = {}
		while (offset + ctypes.sizeof(attribute)) <= len(data):
			offset_payload = offset + math.ceil(ctypes.sizeof(attribute) / 4) * 4
			
			# "Parse" attribute header
			ctypes.memmove(
					ctypes.addressof(attribute),
					data[offset : offset_payload],
					ctypes.sizeof(attribute)
			)
			
			# Store attribute type and contents
			data_start = offset_payload
			data_end   = offset_payload + attribute.len - (data_start - offset)
			if len(data) >= data_end:
				# Convert attribute type and data into human-friendly representation
				(name, value) = (attribute.type, data[data_start : data_end])
				(name, value) = self.decode_single(name, value)
				attributes[name] = value
			
			# Move to next attribute
			offset += math.ceil(attribute.len / 4) * 4
		
		return attributes
	
	def encode(self, attributes):
		"""
		Encode the given list of attibutes into a paltform-dependant attribute byte stream
		
		This is the opposite of the :meth:`~netlink.low.netlinkattrib.AttributeDecoder.decode`
		method and the assertion ``encode(decode(data)) == data`` is guaranteed in most cases.
		
		Parameters
		----------
		attributes : dict
			NetLink attribute list, as produced by the
			:meth:`~netlink.low.netlinkattrib.AttributeDecoder.decode` method
		
		Returns
		-------
		bytes
		"""
		result = bytearray()
		for name, value in attributes.items():
			(type, data) = self.encode_single(name, value)
			
			attribute = self.AttributeType()
			attribute.len  = self.ALIGN(ctypes.sizeof(attribute)) + self.ALIGN(len(data))
			attribute.type = type
			
			# Store header with alignment bytes
			result += bytes(attribute)
			result += b'\x00' * (self.ALIGN(ctypes.sizeof(attribute)) - ctypes.sizeof(attribute))
			
			# Store content with alignment bytes
			result += bytes(data)
			result += b'\x00' * (self.ALIGN(len(data)) - len(data))
		return result


class AddressAttributeDecoder(AttributeDecoder):
	AttributeType = netlink.struct.netlink.AddressAttribute
	
	types = dict(AttributeDecoder.types)
	types['ADDRESS']   = 'address'   # Peer address (or local address if there is no peer)
	types['LOCAL']     = 'address'   # Actual device address 
	types['LABEL']     = 'str'       # Custom identification label for device
	types['BROADCAST'] = 'address'   # Broadcast address
	types['ANYCAST']   = 'address'   # Anycast address
	types['CACHEINFO'] = 'cacheinfo' # Remaining maximum and preferred time for use
	types['MULTICAST'] = 'address'   # Multicast address
	types['FLAGS']     = 'flags'
	
	def attribute_decode_address(self, data):
		"""
		Decode a network address
		
		The address will be decoded to an IPv4, IPv6 or MAC address string depending on its length
		and the address family of the given address message.
		"""
		return self.decode_address(data, self.message.family)
	
	def attribute_encode_address(self, address):
		return self.encode_address(address, self.message.family)
	
	def attribute_decode_flags(self, data):
		"""
		Decode the flag list bits into a list of human-readable strings
		"""
		return self.AttributeType.FLAG.find_bitmask(self.attribute_decode_int_u32(data))
	
	def attribute_encode_flags(self, flags):
		return self.attribute_encode_int_u32(self.AttributeType.FLAG.get_with_iter(flags))
	
	def attribute_decode_cacheinfo(self, data):
		return netlink.struct.netlink.CacheInformation(data).to_dict()
	
	def attribute_encode_cacheinfo(self, cacheinfo):
		return netlink.struct.netlink.CacheInformation.from_dict(cacheinfo)


class InterfaceAttributeDecoder(AttributeDecoder):
	AttributeType = netlink.struct.netlink.InterfaceAttribute
	
	types = dict(AttributeDecoder.types)
	types['ADDRESS']         = 'address'   # Device MAC address
	types['BROADCAST']       = 'address'   # Broadcast MAC address
	types['IFNAME']          = 'str'       # Device interface name
	types['MTU']             = 'int_u32'   # Maximum Transmission Unit
	types['LINK']            = 'int_u32'   #XXX: Figure what this is
	types['QDISC']           = 'str'       # Traffic Control 'Queuing DISCiplin'
	types['STATS']           = None        #TODO: Parse this format?
	types['COST']            = 'int_u32'   # Bridge interface routing cost
	types['PRIORITY']        = 'int_u16'   # Bridge interface routing priority
	types['MASTER']          = 'int_u32'   # Bridge master device index
	types['WIRELESS']        = None        #TODO: Figure what this is (WEXT is deprecated)
	types['PROTINFO']        = 'protinfo'  #XXX: Figure what this is
	types['TXQLEN']          = None        #TODO: Transfer Queue Length
	types['MAP']             = None        #TODO: Figure what this is
	types['WEIGHT']          = 'int_u8'    #XXX
	types['OPERSTATE']       = 'operstate' # Operational state (DOWN, DORMANT, UP, …)
	types['LINKMODE']        = 'linkmode'  #XXX: Figure what this is
	types['LINKINFO']        = 'linkinfo'  #TODO: Figure what this is
	types['NET_NS_PID']      = 'int_u32'   # Network NameSpace Process ID
	types['IFALIAS']         = 'str'       #XXX: Figure what this is
	types['NUM_VF']          = None        #TODO: Number of VFs if device is SR-IOV PF
	types['VFINFO_LIST']     = None        #TODO: Parse this format?
	types['STATS64']         = None        #TODO: Parse this format?
	types['VF_PORTS']        = None        #TODO: Figure what this is
	types['PORT_SELF']       = 'portself'  #TODO: Parse this format?
	types['AF_SPEC']         = 'int_u32'   #XXX: Figure what this is
	types['GROUP']           = 'int_u32'   # Group the device belongs to
	types['NET_NS_PID']      = 'int_u32'   # Network NameSpace File Descriptor
	types['EXT_MASK']        = 'ext_mask'  # Extended information mask
	types['PROMISCUITY']     = 'int_u32'   # Promiscuity count: > 0 means acts PROMISC
	types['NUM_TX_QUEUES']   = 'int_u32'   # Number of transfer queues
	types['NUM_RX_QUEUES']   = 'int_u8'    # Number of receive queues
	types['CARRIER']         = None        #TODO: Figure what this is
	types['PHYS_PORT_ID']    = 'int_u32'   # ID of the physical network port
	types['CARRIER_CHANGES'] = None        #TODO: Figure what this is
	types['PHYS_SWITCH_ID']  = 'int_u32'   #XXX: Somehow related to PHYS_PORT_ID
	types['LINK_NETNSID']    = 'int_u32'   #XXX: Figure what this is
	types['PHYS_PORT_NAME']  = 'str'       #XXX: Somehow related to PHYS_PORT_ID
	types['PROTO_DOWN']      = 'bool'      #XXX: Figure what this is
	
	def attribute_decode_address(self, data):
		"""
		Decode a network address
		
		The address will be decoded to an IPv4, IPv6 or MAC address string depending on its length
		and the type of link that it is present on.
		"""
		message_type = self.message.TYPE.find(self.message.type)
		if message_type in ('TUNNEL', 'SIT', 'IPGRE'):
			return self.decode_address(data, socket.AF_INET)
		elif message_type in ('TUNNEL6',):
			return self.decode_address(data, socket.AF_INET6)
		else:
			return self.decode_address(data, None)
	
	def attribute_encode_address(self, address):
		message_type = self.message.TYPE.find(self.message.type)
		if message_type in ('TUNNEL', 'SIT', 'IPGRE'):
			return self.encode_address(address, socket.AF_INET)
		elif message_type in ('TUNNEL6',):
			return self.encode_address(address, socket.AF_INET6)
		else:
			return self.encode_address(address, None)
	
	def attribute_decode_operstate(self, data):
		"""
		Decode the operational state of a device from a binary integer to its state name
		"""
		return self.AttributeType.OPER.find(self.attribute_decode_int_u8(data))
	
	def attribute_encode_operstate(self, operstate):
		return self.attribute_encode_int_u8(self.AttributeType.OPER.get(data))
	
	def attribute_decode_protinfo(self, data):
		"""
		Decode the bridge port state of a device from a binary integer to its state name
		"""
		return self.AttributeType.BRIDGE_STATE.find(self.attribute_decode_int_u32(data))
	
	def attribute_encode_protinfo(self, protinfo):
		return self.attribute_encode_int_u32(self.AttributeType.BRIDGE_STATE.get(protinfo))
	
	def attribute_decode_linkmode(self, data):
		return self.AttributeType.LINKMODE.find(self.attribute_decode_int_u8(data))
	
	def attribute_encode_linkmode(self, linkmode):
		return self.attribute_encode_int_u8(self.AttributeType.LINKMODE.get(linkmode))
		
	def attribute_decode_linkinfo(self, data):
		return LinkInfoDecoder(self.message).decode(data)
		
	def attribute_encode_linkinfo(self, linkinfo):
		return LinkInfoDecoder(self.message).encode(linkinfo)
	
	def attribute_decode_portself(self, data):
		return PortSelfDecoder(self.message).decode(data)
	
	def attribute_encode_portself(self, portself):
		return PortSelfDecoder(self.message).encode(portself)
	
	def attribute_decode_ext_mask(self, data):
		return self.AttributeType.EXT_MASK.find_bitmask(self.attribute_decode_int_u32(data))
	
	def attribute_encode_ext_mask(self, ext_mask):
		return self.attribute_encode_int_u32(self.AttributeType.EXT_MASK.find_bitmask(ext_mask))

class LinkInfoDecoder(AttributeDecoder):
	"""
	TODO: Implement proper decoding (and figure out which attribute structure this is related to)
	"""
	types = dict(AttributeDecoder.types)

class PortSelfDecoder(AttributeDecoder):
	"""
	TODO: Implement proper decoding (and figure out which attribute structure this is related to)
	"""
	types = dict(AttributeDecoder.types)
	
	def decode_single(self, type, data):
		# Do standard name decoding
		(type, value) = super().decode_single(type, data)
		
		# Decode value by running it through the attribute parser again
		#TODO: Implement proper decoding for the second round
		value = AttributeDecoder(self.message).decode(value)
		
		return (type, value)
