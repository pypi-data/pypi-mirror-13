import ctypes

import netlink.struct.misc
import netlink.struct.routing



class SocketAddress(ctypes.Structure):
	_fields_ = [
		('family', ctypes.c_ushort),
		('pad',    ctypes.c_ushort),
		('pid',    ctypes.c_uint32),
		('groups', ctypes.c_uint32),
	]



class MessageHeader(ctypes.Structure):
	_fields_ = [
		('len',   ctypes.c_uint32),
		('type',  ctypes.c_uint16),
		('flags', ctypes.c_uint16),
		('seq',   ctypes.c_uint32),
		('pid',   ctypes.c_uint32),
	]
	
	class TYPE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("BASE",    16),
			("NEWLINK", 16),
			("DELLINK", 17),
			("GETLINK", 18),
			("SETLINK", 19),
			("NEWADDR", 20),
			("DELADDR", 21),
			("GETADDR", 22),
			
			("NEWROUTE", 24),
			("DELROUTE", 25),
			("GETROUTE", 26),
			
			("NEWNEIGH", 28),
			("DELNEIGH", 29),
			("GETNEIGH", 30),
			
			("NEWRULE", 32),
			("DELRULE", 33),
			("GETRULE", 34),
			
			("NEWQDISC", 36),
			("DELQDISC", 37),
			("GETQDISC", 38),
			
			("NEWTCLASS", 40),
			("DELTCLASS", 41),
			("GETTCLASS", 42),
			
			("NEWTFILTER", 44),
			("DELTFILTER", 45),
			("GETTFILTER", 46),
			
			("NEWACTION", 48),
			("DELACTION", 49),
			("GETACTION", 50),
			
			("NEWPREFIX", 52),
			
			("GETMULTICAST", 58),
			
			("GETANYCAST", 62),
			
			("NEWNEIGHTBL", 64),
			("GETNEIGHTBL", 66),
			("SETNEIGHTBL", 67),
			
			("NEWNDUSEROPT", 68),
			
			("NEWADDRLABEL", 72),
			("DELADDRLABEL", 73),
			("GETADDRLABEL", 74),
			
			("GETDCB", 78),
			("SETDCB", 79),
			
			("NEWNETCONF", 80),
			("GETNETCONF", 82),
			
			("NEWMDB", 84),
			("DELMDB", 85),
			("GETMDB", 86),
			
			("NEWNSID", 88),
			("DELNSID", 89),
			("GETNSID", 90),
		]
	
	class RESPONSE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("NOOP",    0x1, "Nothing"),
			("ERROR",   0x2, "Error"),
			("DONE",    0x3, "End of dump"),
			("OVERRUN", 0x4, "Data lost"),
		]
	
	class FLAG(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("REQUEST",   1,  "It is request message"),
			("MULTI",     2,  "Multipart message, terminated by MSG_DONE"),
			("ACK",       4,  "Reply with ack, with zero or error code"),
			("ECHO",      8,  "Echo this request"),
			("DUMP_INTR", 16, "Dump was inconsistent due to sequence change"),
			
			# Modifiers to GET request
			("ROOT",   0x100, "Specify tree root"),
			("MATCH",  0x200, "Return all matching"),
			("ATOMIC", 0x400, "Atomic GET"),
			("DUMP",   0x300),
			
			# Modifiers to NEW request
			("REPLACE", 0x100, "Override existing"),
			("EXCL",    0x200, "Do not touch, if it exists"),
			("CREATE",  0x400, "Create, if it does not exist"),
			("APPEND",  0x800, "Add to end of list"),
		]


class AddressMessage(ctypes.Structure):
	_fields_ = [
		('family',    ctypes.c_uint8),
		('prefixlen', ctypes.c_uint8),
		('flags',     ctypes.c_uint8),
		('scope',     ctypes.c_uint8),
		('index',     ctypes.c_uint32),
	]
	
	
	class FLAG(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			# ifa_flags
			("SECONDARY", 0x01),
			("TEMPORARY", 0x01),
			
			("NODAD",          0x0002),
			("OPTIMISTIC",     0x0004),
			("DADFAILED",      0x0008),
			("HOMEADDRESS",    0x0010),
			("DEPRECATED",     0x0020),
			("TENTATIVE",      0x0040),
			("PERMANENT",      0x0080),
			("MANAGETEMPADDR", 0x0100),
			("NOPREFIXROUTE",  0x0200),
			("MCAUTOJOIN",     0x0400),
			("STABLE_PRIVACY", 0x0800),
		]
	
	SCOPE = netlink.struct.routing.Message.SCOPE

class InterfaceMessage(ctypes.Structure):
	_fields_ = [
		('family',   ctypes.c_uint8),  # Address family
		('unused_1', ctypes.c_char),
		('type',     ctypes.c_ushort),
		('index',    ctypes.c_int),   # Link index
		('flags',    ctypes.c_uint),
		('change',   ctypes.c_uint),  # Flag change mask
	]
	
	
	class TYPE(metaclass = netlink.struct.misc.Enumeration):
		"""
		ARP header types (0-255) and constants for many other network protocols (256-65535)
		"""
		_fields_ = [
			("NETROM",     0,  "from KA9Q: NET/ROM pseudo"),
			("ETHER",      1,  "Ethernet 10Mbps"),
			("EETHER",     2,  "Experimental Ethernet"),
			("AX25",       3,  "AX.25 Level 2"),
			("PRONET",     4,  "PROnet token ring"),
			("CHAOS",      5,  "Chaosnet"),
			("IEEE802",    6,  "IEEE 802.2 Ethernet/TR/TB"),
			("ARCNET",     7,  "ARCnet"),
			("APPLETLK",   8,  "APPLEtalk"),
			("DLCI",       15, "Frame Relay DLCI"),
			("ATM",        19, "ATM"),
			("METRICOM",   23, "Metricom STRIP (new IANA id)"),
			("IEEE1394",   24, "IEEE 1394 IPv4 - RFC 2734"),
			("EUI64",      27, "EUI-64"),
			("INFINIBAND", 32, "InfiniBand"),

			# Dummy types for non ARP hardware
			("SLIP",    256),
			("CSLIP",   257),
			("SLIP6",   258),
			("CSLIP6",  259),
			("RSRVD",   260,   "Notional KISS type"),
			("ADAPT",   264),
			("ROSE",    270),
			("X25",     271,   "CCITT X.25"),
			("HWX25",   272,   "Boards with X.25 in firmware"),
			("CAN",     280,   "Controller Area Network"),
			("PPP",     512),
			("CISCO",   513,   "Cisco HDLC"),
			("HDLC",    513,   "Cisco HDLC"),
			("LAPB",    516,   "LAPB"),
			("DDCMP",   517,   "Digital's DDCMP protocol"),
			("RAWHDLC", 518,   "Raw HDLC"),

			("TUNNEL",   768, "IPIP tunnel"),
			("TUNNEL6",  769, "IP6IP6 tunnel"),
			("FRAD",     770, "Frame Relay Access Device"),
			("SKIP",     771, "SKIP vif"),
			("LOOPBACK", 772, "Loopback device"),
			("LOCALTLK", 773, "Localtalk device"),
			("FDDI",     774, "Fiber Distributed Data Interface"),
			("BIF",      775, "AP1000 BIF"),
			("SIT",      776, "sit0 device - IPv6-in-IPv4"),
			("IPDDP",    777, "IP over DDP tunneller"),
			("IPGRE",    778, "GRE over IP"),
			("PIMREG",   779, "PIMSM register interface"),
			("HIPPI",    780, "High Performance Parallel Interface"),
			("ASH",      781, "Nexus 64Mbps Ash"),
			("ECONET",   782, "Acorn Econet"),
			("IRDA",     783, "Linux-IrDA"),
			("FCPP",     784, "Point to point fibrechannel"),
			("FCAL",     785, "Fibrechannel arbitrated loop"),
			("FCPL",     786, "Fibrechannel public loop"),
			("FCFABRIC", 787, "Fibrechannel fabric"),
			# 787->799 reserved for fibrechannel media types
			("IEEE802_TR",         800, "Magic type ident for TR"),
			("IEEE80211",          801, "IEEE 802.11"),
			("IEEE80211_PRISM",    802, "IEEE 802.11 + Prism2 header"),
			("IEEE80211_RADIOTAP", 803, "IEEE 802.11 + radiotap header"),
			("IEEE802154",         804),
			("IEEE802154_MONITOR", 805, "IEEE 802.15.4 network monitor"),

			("PHONET",      820, "PhoNet media type"),
			("PHONET_PIPE", 821, "PhoNet pipe header"),
			("CAIF",        822, "CAIF media type"),
			("IP6GRE",      823, "GRE over IPv6"),
			("NETLINK",     824, "Netlink header"),
			("IP6LOWPAN",   825, "IPv6 over LoWPAN"),
			
			("VOID", 0xFFFF, "Void type, nothing is known"),
			("NONE", 0xFFFE, "zero header length"),
		]
	
	class FLAG(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("UP",          1<<0,  "Interface is up"),
			("BROADCAST",   1<<1,  "Broadcast address is valid"),
			("DEBUG",       1<<2,  "Debugging enabled"),
			("LOOPBACK",    1<<3,  "Interface is a loopback network"),
			("POINTOPOINT", 1<<4,  "Interface is a Point-to-Point link"),
			("NOTRAILERS",  1<<5,  "Avoid the use of trailers"),
			("RUNNING",     1<<6,  "Interface has operating status UP (:rfc:`2863#section-3.1.14`)"),
			("NOARP",       1<<7,  "ARP protocol is not used"),
			("PROMISC",     1<<8,  "Receive all packets (even if they are for another host)"),
			("ALLMULTI",    1<<9,  "Receive all Multicast packets"),
			("MASTER",      1<<10, "Master of a load balancer"),
			("SLAVE",       1<<11, "Slave of a load balancer"),
			("MULTICAST",   1<<12, "Supports Multicast"),
			("PORTSEL",     1<<13, "Media type selectable"),
			("AUTOMEDIA",   1<<14, "Automatic media selection active"),
			("DYNAMIC",     1<<15, "Is dail-up device with changing addresses"),
			("LOWER_UP",    1<<16, "Device signals L1 up"),
			("DORMANT",     1<<17, "Driver signals dormant"),
			("ECHO",        1<<18, "Echo sent packets"),
		]



class MessageError(ctypes.Structure):
	_fields_ = [
		('error', ctypes.c_int),
		('msg',   MessageHeader),
	]



class Attribute(ctypes.Structure):
	_fields_ = [
		('len',  ctypes.c_ushort),
		('type', ctypes.c_ushort),
	]

class AddressAttribute(Attribute):
	class TYPE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("UNSPEC",    0),
			("ADDRESS",   1, 'Peer address (or local address if there is no peer)'),
			("LOCAL",     2, 'Actual device address'),
			("LABEL",     3, 'Custom identification label for device'),
			("BROADCAST", 4, 'Broadcast address'),
			("ANYCAST",   5, 'Anycast address'),
			("CACHEINFO", 6, 'Remaining maximum and preferred time for use'),
			("MULTICAST", 7, 'Multicast address'),
			("FLAGS",     8),
		]
	
	FLAG = AddressMessage.FLAG

class InterfaceAttribute(Attribute):
	class TYPE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("UNSPEC",          0),
			("ADDRESS",         1),
			("BROADCAST",       2),
			("IFNAME",          3),
			("MTU",             4),
			("LINK",            5),
			("QDISC",           6),
			("STATS",           7),
			("COST",            8),
			("PRIORITY",        9),
			("MASTER",          10),
			("WIRELESS",        12, "Wireless Extension event"),
			("PROTINFO",        13, "Protocol specific information for a link"),
			("TXQLEN",          14),
			("MAP",             15),
			("WEIGHT",          16),
			("OPERSTATE",       17),
			("LINKINFO",        18),
			("LINKMODE",        19),
			("NET_NS_PID",      20),
			("IFALIAS",         21),
			("NUM_VF",          22, "Number of VFs if device is SR-IOV PF"),
			("VFINFO_LIST",     23),
			("STATS64",         24),
			("VF_PORTS",        25),
			("PORT_SELF",       26),
			("AF_SPEC",         27),
			("GROUP",           28, "Group the device belongs to"),
			("NET_NS_FD",       29),
			("EXT_MASK",        30, "Extended info mask =  VFs =  etc"),
			("PROMISCUITY",     31, "Promiscuity count: > 0 means acts PROMISC"),
			("NUM_TX_QUEUES",   32),
			("NUM_RX_QUEUES",   33),
			("CARRIER",         34),
			("PHYS_PORT_ID",    35),
			("CARRIER_CHANGES", 36),
			("PHYS_SWITCH_ID",  37),
			("LINK_NETNSID",    38),
			("PHYS_PORT_NAME",  39),
			("PROTO_DOWN",      40),
		]
	
	class OPER(metaclass = netlink.struct.misc.Enumeration):
		"""
		RFC 2863 operational status
		"""
		_fields_ = [
			("UNKNOWN",        0),
			("NOTPRESENT",     1),
			("DOWN",           2),
			("LOWERLAYERDOWN", 3),
			("TESTING",        4),
			("DORMANT",        5),
			("UP",             6),
		]
	
	class BRIDGE_STATE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			("DISABLED",   0),
			("LISTENING",  1),
			("LEARNING",   2),
			("FORWARDING", 3),
			("BLOCKING",   4),
		]
	
	class LINKMODE(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			('DEFAULT', 0),
			('DORMANT', 1, 'Limit upward transition to dormant'),
		]
	
	class EXT_MASK(metaclass = netlink.struct.misc.Enumeration):
		_fields_ = [
			('VF',                1<<0),
			('BRVLAN',            1<<1),
			('BRVLAN_COMPRESSED', 1<<2),
		]


class CacheInformation(netlink.struct.misc.Structure):
	_fields_ = [
		('preferred', ctypes.c_uint32),
		('valid',     ctypes.c_uint32),
		('cstamp',    ctypes.c_uint32), # Creation timestamp (hundredths of seconds)
		('tstamp',    ctypes.c_uint32), # Update timestamp (hundredths of seconds)
	]
