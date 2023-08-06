import ctypes

import netlink.struct.misc


class Message(ctypes.Structure):
	_fields_ = [
		('family',   ctypes.c_ubyte),
		('dst_len',  ctypes.c_ubyte),
		('src_len',  ctypes.c_ubyte),
		('tos',      ctypes.c_ubyte),
		('table',    ctypes.c_ubyte),
		('protocol', ctypes.c_ubyte),
		('scope',    ctypes.c_ubyte),
		('type',     ctypes.c_ubyte),
		('flags',    ctypes.c_uint),
	]
	
	class FLAG(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("NOTIFY",   0x100, "Notify user of route change"),
			("CLONED",   0x200, "This route is cloned"),
			("EQUALIZE", 0x400, "Multipath equalizer: NI"),
			("PREFIX",   0x800, "Prefix addresses"),
		]

	class TYPE(metaclass = netlink.struct.misc.Enumeration):
		"""
		Possible routing types
		"""
		_fields_ = [
			("UNSPEC",      0),
			("UNICAST",     1,  "Gateway or direct route"),
			("LOCAL",       2,  "Accept locally"),
			("BROADCAST",   3,  "Accept locally as broadcast, sens as broadcast"),
			("ANYCAST",     4,  "Accept locally as broadcast, but send as unicast"),
			("MULTICAST",   5,  "Multicast route"),
			("BLACKHOLE",   6,  "Drop"),
			("UNREACHABLE", 7,  "Destination is unreachable"),
			("PROHIBIT",    8,  "Administratively prohibited"),
			("THROW",       9,  "Not in this table"),
			("NAT",         10, "Translate this address"),
			("XRESOLVE",    11, "Use external resolver"),
		]

	class PROTOCOL(metaclass = netlink.struct.misc.Enumeration):
		"""
		Possible route creation protocols
	
		These constants describe how the route came to be and how it should be treated by miscellaneous
		routing modification software (such as DHCP/NDP clients).  
		"""
		_fields_ = [
			("UNSPEC",   0),
			("REDIRECT", 1, "Route installed by ICMP redirects (not used by current IPv4)"),
			("KERNEL",   2, "Route installed by kernel"),
			("BOOT",     3, "Route installed during boot"),
			("STATIC",   4, "Route installed by administrator"),
			
			# Values above STATIC are not interpreted by kernel:
			# They are just passed from user and back as is and are be used by different routing daemons to
			# mark "their" routes. New protocol values should be standardized in order to avoid conflicts.
			("GATED",    8,  "GateD"),
			("RA",       9,  "RDISC/ND router advertisements"),
			("MRT",      10, "Merit MRT"),
			("ZEBRA",    11, "Zebra"),
			("BIRD",     12, "BIRD"),
			("DNROUTED", 13, "DECnet routing daemon"),
			("XORP",     14, "XORP"),
			("NTK",      15, "Netsukuku"),
			("DHCP",     16, "DHCP client"),
			("MROUTED",  17, "Multicast daemon"),
			("BABEL",    18, "Babel daemon"),
		]

	class SCOPE(metaclass = netlink.struct.misc.Enumeration):
		"""
		Enumeration class of possible link scopes
	
		The name "scope" is somewhat misleading, as these constants actually attempt to describe the
		distance from this host to the next hop.
	
		Intermediate values, not listed here, are also possible. This can be used, for instance, to
		declare interior routes between UNIVERSE and LINK.
		"""
		_fields_ = [
			("UNIVERSE", 0,   "Some place far, far away"),
			("SITE",     200),
			("LINK",     253, "Destinations attached directly to this system"),
			("HOST",     254, "Local addresses"),
			("NOWHERE",  255, "None-existing destinations"),
		]

	class TABLE(metaclass = netlink.struct.misc.Enumeration):
		"""
		Enumeration class of reserved routing table class identifiers
		"""
		_fields_ = [
			("UNSPEC",  0),
			("COMPAT",  252),
			("DEFAULT", 253),
			("MAIN",    254),
			("LOCAL",   255),
		]
