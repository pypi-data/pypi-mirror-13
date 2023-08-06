import ctypes

import netlink.struct.misc



class MessageHeader(ctypes.Structure):
	"""
	Structure describing messages sent by `sendmsg` and received by `recvmsg`
	"""
	
	_fields_ = [
		('name',       ctypes.c_void_p), # Address to send to/receive from
		('namelen',    ctypes.c_uint32), # Length of address data
		
		('iov',        ctypes.c_void_p), # Vector of data to send/receive (netlink.struct.misc.IOVector *)
		('iovlen',     ctypes.c_size_t), # Number of elements in the vector
		
		('control',    ctypes.c_void_p), # Ancillary data
		('controllen', ctypes.c_size_t), # Ancillary data buffer length
		
		('flags',      ctypes.c_int),    # Flags on received messages
		
	]
