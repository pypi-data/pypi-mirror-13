import ctypes
import fcntl
import socket
import time

import netlink.struct.netif


class Socket:
	###########################################
	# Public ioctl() calls (from sys/ioctl.h) #
	###########################################
	
	# Routing table calls
	SIOCADDRT = 0x890B # add routing table entry
	SIOCDELRT = 0x890C # delete routing table entry
	SIOCRTMSG = 0x890D # call to routing system
	
	# Socket configuration controls
	SIOCGIFNAME        = 0x8910       # get iface name
	SIOCSIFLINK        = 0x8911       # set iface channel
	SIOCGIFCONF        = 0x8912       # get iface list
	SIOCGIFFLAGS       = 0x8913       # get flags
	SIOCSIFFLAGS       = 0x8914       # set flags
	SIOCGIFADDR        = 0x8915       # get PA address
	SIOCSIFADDR        = 0x8916       # set PA address
	SIOCGIFDSTADDR     = 0x8917       # get remote PA address
	SIOCSIFDSTADDR     = 0x8918       # set remote PA address
	SIOCGIFBRDADDR     = 0x8919       # get broadcast PA address
	SIOCSIFBRDADDR     = 0x891a       # set broadcast PA address
	SIOCGIFNETMASK     = 0x891b       # get network PA mask
	SIOCSIFNETMASK     = 0x891c       # set network PA mask
	SIOCGIFMETRIC      = 0x891d       # get metric
	SIOCSIFMETRIC      = 0x891e       # set metric
	SIOCGIFMEM         = 0x891f       # get memory address (BSD)
	SIOCSIFMEM         = 0x8920       # set memory address (BSD)
	SIOCGIFMTU         = 0x8921       # get MTU size
	SIOCSIFMTU         = 0x8922       # set MTU size
	SIOCSIFNAME        = 0x8923       # set interface name
	SIOCSIFHWADDR      = 0x8924       # set hardware address
	SIOCGIFENCAP       = 0x8925       # get/set encapsulations
	SIOCSIFENCAP       = 0x8926
	SIOCGIFHWADDR      = 0x8927       # Get hardware address
	SIOCGIFSLAVE       = 0x8929       # Driver slaving support
	SIOCSIFSLAVE       = 0x8930
	SIOCADDMULTI       = 0x8931       # Multicast address lists
	SIOCDELMULTI       = 0x8932
	SIOCGIFINDEX       = 0x8933       # name -> if_index mapping
	SIOCSIFPFLAGS      = 0x8934       # set/get extended flags set
	SIOCGIFPFLAGS      = 0x8935
	SIOCDIFADDR        = 0x8936       # delete PA address
	SIOCSIFHWBROADCAST = 0x8937       # set hardware broadcast addr
	SIOCGIFCOUNT       = 0x8938       # get number of devices
	
	SIOCETHTOOL = 0x8946
	
	SIOCGIFBR = 0x8940 # Bridging support
	SIOCSIFBR = 0x8941 # Set bridging options
	
	SIOCGIFTXQLEN = 0x8942 # Get the tx queue length
	SIOCSIFTXQLEN = 0x8943 # Set the tx queue length
	
	# ARP cache control calls
	SIOCDARP = 0x8953 # delete ARP table entry
	SIOCGARP = 0x8954 # get ARP table entry
	SIOCSARP = 0x8955 # set ARP table entry
	
	# RARP cache control calls
	SIOCDRARP = 0x8960 # delete RARP table entry
	SIOCGRARP = 0x8961 # get RARP table entry
	SIOCSRARP = 0x8962 # set RARP table entry
	
	# Driver configuration calls
	SIOCGIFMAP = 0x8970 # Get device parameters
	SIOCSIFMAP = 0x8971 # Set device parameters
	
	# DLCI configuration calls
	SIOCADDDLCI = 0x8980 # Create new DLCI device
	SIOCDELDLCI = 0x8981 # Delete DLCI device
	
	def __init__(self, connection):
		self._connection = connection
		
		# Store sequence counter for NetLink
		self._seq = int(time.time()) & 0xFFFFFFFF
	
	def __del__(self):
		self._connection.close()
	
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		self._connection.close()
	
	
	
	@property
	def bufsize(self):
		return self._bufsize
	
	@bufsize.setter
	def bufsize(self, bufsize):
		self._bufsize = bufsize
		
		self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, bufsize)
		self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
	
	@property
	def sockname(self):
		return self._connection.getsockname()
	
	
	
	def ioctl(self, reqtype, request):
		if isinstance(reqtype, str):
			reqtype = getattr(self, "SIOC{0}".format(reqtype.upper()))
		
		fcntl.ioctl(self._connection.fileno(), reqtype, ctypes.addressof(request))
	
	def next_sequence_number(self):
		self._seq += 1
		self._seq &= 0xFFFFFFFF
		return self._seq
	
	def recvmsg(self, ancbufsize = 0, flags = 0):
		return self._connection.recvmsg(self.bufsize, ancbufsize, flags)
	
	def sendmsg(self, buffer, ancdata = (), flags = 0, address = None):
		return self._connection.sendmsg((buffer,), ancdata, flags, address)
	
	def close(self):
		self._connection.close()



class NetworkDeviceSocket(Socket):
	def __init__(self):
		connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)
		super().__init__(connection)
	
	@classmethod
	def create_request(cls, device_name):
		"""
		Create kernel network interface request structure
		"""
		request           = netlink.struct.netif.RequestData()
		request.ifrn_name = device_name.encode('ascii')
		return request



class RTNetlinkSocket(Socket):
	def __init__(self, subscriptions = 0):
		"""
		
		"""
		connection = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
		connection.bind((0, subscriptions))
		super().__init__(connection)
		
		# Increase send and receive buffer size
		self.bufsize = 32768
