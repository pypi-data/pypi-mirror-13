import ctypes
import errno
import ipaddress
import os
import socket
import sys

import netlink.low.netlinkattrib

import netlink.struct.netlink



class NetLinkError(OSError):
	def __init__(self, code, message, response):
		super().__init__(code, message)
		self.response = response

class NetLinkEOFError(NetLinkError):
	def __init__(self, message, response):
		super().__init__(errno.ENODATA, message, response)

class NetLinkTruncatedError(NetLinkError):
	def __init__(self, message, response):
		super().__init__(errno.EMSGSIZE, message, response)

class NetLinkInterruptedError(NetLinkError):
	def __init__(self, message, response):
		super().__init__(errno.EINTR, message, response)

class NetLinkNotAcknowledged(NetLinkError):
	def __init__(self, message, response):
		super().__init__(errno.ENOMSG, message, response)


class Request:
	AttributeCoderType = netlink.low.netlinkattrib.AttributeDecoder
	MessageType        = None
	
	def __init__(self, netif, cmd, flags = (), pid = 0):
		self._netif = netif
		
		self.header = netlink.struct.netlink.MessageHeader()
		self.header.type  = self.header.TYPE.get(cmd)
		self.header.pid   = pid # Send messages to kernel (pid 0) by default
		self.header.len   = self.AttributeCoderType.ALIGN(ctypes.sizeof(self.header))
		self.header.flags = self.header.FLAG.get_with_iter(flags)
		
		self.coder = self.AttributeCoderType()
		
		self._buffer = bytearray()
		self._buffer += b'\x00' * (self.header.len - ctypes.sizeof(self.header))
	
	
	def add_attributes(self, attributes):
		self._buffer += self.coder.encode(attributes)
		return self
	
	def add_attribute(self, type, data = None):
		return self.add_attributes({type: data})
	
	def add_raw(self, data):
		# Store given raw data
		self._buffer += data
		
		# Store additional alignment bytes (header alignment is responsibility of the caller)
		self._buffer += b'\x00' * (self.coder.ALIGN(len(data)) - len(data))
		
		return self
		
	
	def send(self, require_acknowledgement = True):
		pid = self._netif.sockname[0]
		
		self.header.seq = self._netif.next_sequence_number()
		self.header.len = ctypes.sizeof(self.header) + len(self._buffer)
		
		# Prepare acknowledgement response tracking
		acknowledged = False
		if require_acknowledgement:
			self.header.flags |= self.header.FLAG.ACK
		
		# Send assembled request packet
		data = bytearray(self.header.len)
		data[:ctypes.sizeof(self.header)] = bytes(self.header)
		data[ctypes.sizeof(self.header):] = self._buffer
		self._netif.sendmsg(data)
		
		response = []
		
		finished = False
		while not finished:
			try:
				(data, _, msg_flags, _) = self._netif.recvmsg()
			except OSError as e:
				if e.errno == errno.EINTR or e.errno == errno.EAGAIN:
					# Read was interrupted by signal – retry
					continue
				else:
					# Serious error during `recvmsg`
					raise
			
			if (msg_flags & socket.MSG_TRUNC) != 0:
				# NetLink message was too big for buffer
				raise NetLinkTruncatedError("Truncated NetLink message", response)
			
			if len(data) < 1:
				# Empty NetLink message received (may never happen)
				raise NetLinkEOFError("EOF on NetLink read", response)
			
			# Iterate of all response messages
			offset = 0
			header = netlink.struct.netlink.MessageHeader()
			while (offset + ctypes.sizeof(header)) <= len(data):
				# Populate header with next data set
				ctypes.memmove(ctypes.addressof(header), data[offset:], ctypes.sizeof(header))
				
				offset_payload = offset + self.coder.ALIGN(ctypes.sizeof(header))
				
				if header.pid != pid or header.seq != self.header.seq:
					# Skip responses that were not intended for us
					offset += header.len
					
					if not hasattr(self, '_allow_recv_other_destination'):
						assert False
					
					continue
				
				if (header.flags & header.FLAG.DUMP_INTR) != 0:
					raise NetLinkInterruptedError("Message interrupted", response)
				
				if header.type == header.RESPONSE.ERROR:
					# Whoops
					
					error = netlink.struct.netlink.MessageError()
					if (len(data) - offset_payload) < ctypes.sizeof(error):
						# Sanity check to make sure the error message was not truncated
						raise NetLinkTruncatedError("Truncated NetLink error message", response)
					ctypes.memmove(ctypes.addressof(error), data[offset_payload:], ctypes.sizeof(error))
					
					if error.error == 0:
						# Acknowledgement received
						acknowledged = True
						finished     = True
						
						# Move to next message
						offset += header.len
					else:
						message = "RTNETLINK answers: {0}".format(os.strerror(-error.error))
						raise NetLinkError(-error.error, message, response)
				elif header.type == header.RESPONSE.DONE:
					finished = True
					break
				else:
					data_start = offset_payload
					data_end   = offset_payload + header.len - (offset_payload - offset)
					response.append(self.parse_response(data[data_start : data_end]))
					
					# Any received message is also an acknowledgement that data has been sent
					acknowledged = True
					
					if (header.flags & header.FLAG.MULTI) == 0:
						# Single message only – don't expect any DONE response message
						finished = True
						break
					
					# Move to next message
					offset += self.coder.ALIGN(header.len)
		
		if not acknowledged and require_acknowledgement:
			raise NetLinkNotAcknowledged("Missing acknowledgement", response)
		
		return response
	
	
	@classmethod
	def parse_response(cls, data):
		message = cls.MessageType()
		ctypes.memmove(ctypes.addressof(message), data, ctypes.sizeof(message))
		
		# Add attribute decoder to message for attribute parsing later on
		offset     = cls.AttributeCoderType.ALIGN(ctypes.sizeof(message))
		attributes = cls.AttributeCoderType(message).decode(data[offset:])
		
		return message, attributes


class AddressRequest(Request):
	AttributeCoderType = netlink.low.netlinkattrib.AddressAttributeDecoder
	MessageType        = netlink.struct.netlink.AddressMessage
	
	def add_header(self, family, dev_index, prefixlen, flags = 0, scope = 0):
		# Create and populate address message header
		message = self.MessageType()
		message.family    = family
		message.prefixlen = prefixlen
		message.scope     = message.SCOPE.get(scope)
		message.index     = dev_index
		
		# Make attributes from the extended header available to the message coder
		self.coder.message = message
		
		flags = message.FLAG.get_with_iter(flags)
		
		# The flags list eventually got larger than 1 byte so a custom u32 attribute has to be added
		# if any extra flags need to be sent
		if (flags & 0xFF) != flags:
			self.add_raw(bytes(message))
			
			flags = int(flags).to_bytes(4, sys.byteorder)
			return self.add_attribute(netlink.struct.netlink.Attribute.TYPE.FLAGS, flags) 
		else:
			message.flags = flags
			return self.add_raw(bytes(message))


class InterfaceRequest(Request):
	AttributeCoderType = netlink.low.netlinkattrib.InterfaceAttributeDecoder
	MessageType        = netlink.struct.netlink.InterfaceMessage
	
	
	def add_header(self, family, dev_index, type = 0, flags = 0, change = 0):
		# Create and populate interface message header
		message = self.MessageType()
		message.family = family
		message.type   = message.TYPE.get(type)
		message.index  = dev_index
		message.flags  = message.FLAG.get_with_iter(flags)
		message.change = message.FLAG.get_with_iter(change)
		
		# Make attributes from the extended header available to the message coder
		self.coder.message = message
		
		return self.add_raw(bytes(message))
