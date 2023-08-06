import ctypes

import netlink.struct.misc
import netlink.struct.routing


class RequestData(ctypes.Structure):
	"""
	Interface request structure for generic request data pointers
	"""
	IFNAMSIZ = 16
	
	class IFRU(ctypes.Union):
		IFNAMSIZ = 16
		
		_fields_ = [
			('flags',   ctypes.c_short),
			('ivalue',  ctypes.c_int),
			('mtu',     ctypes.c_int),
			('slave',   ctypes.c_char * IFNAMSIZ),
			('newname', ctypes.c_char * IFNAMSIZ),
			('data',    ctypes.c_void_p),
		]
	
	_fields_ = [
		('ifrn_name', ctypes.c_char * IFNAMSIZ),
		('ifru',      IFRU),
	]
