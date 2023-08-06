import collections
import errno
import ipaddress
import platform
import socket
import warnings

import netlink.low.netif
import netlink.low.netlink
import netlink.low.ethtool


# In case somebody tries this…
if platform.system() != "Linux":
	warnings.warn("This is a Linux-only library, running it on another platform will very likely fail")


class NetworkDevice:
	def __init__(self, index, name, network):
		self._index   = index
		self._name    = name
		self._network = network
		
		self._low_netlink = network._low_netlink
		self._low_ethtool = netlink.low.ethtool.ETHTool("", network._low_netif)
	
	def __eq__(self, device):
		if not isinstance(device, self.__class__):
			return hash(device)  == self.index
		elif self._index is not None:
			return device._index == self._index
		else:
			return device._name  == self._name
	
	def __hash__(self):
		return self.index
	
	@property
	def index(self):
		if self._index is None:
			self._index = self._network.device_name2index(self._name)
		
		return self._index
	
	@property
	def name(self):
		if self._name is None:
			self._name = self._network.device_index2name(self._index)
		
		return self._name
	
	
	def add_address(self, address, *args, **kwargs):
		"""
		Add a new IP address to this interface
		
		Parameters
		----------
		address : `str` | :func:`ipaddress.ip_interface`
			.. _device-add-address-address:
			
			An IP address (optionally) including the network prefix
			
			The string must be in the form of ``address/prefix_len``. Where ``address`` is an
			IP address in the form of ``a.b.c.d`` or ``a:b:c:d:e::f`` and ``prefix_len`` is
			the number of network address bits. If ``prefix_len`` is omitted then a prefix
			length of 32 bits for IPv4 and 128 bits for IPv6 will be assumed.
		
		flags : collections.abc.Sequence
			.. _device-add-address-flags:
			
			A list of flags to enable for this address
			
			Currently the following flags are known:
			
			 * ``'HomeAddress'``: (IPv6 only)
			   
			   Designate this address the "home address" (as defined in :rfc:`6275#section-6.3`).
			   
			 * ``'ManageTempAddr'``: (IPv6 only)
			   
			   Make the kernel manage temporary addresses created from this one as
			   template on behalf of Privacy Extensions (:rfc:`3041`).
			   
			   For this to become active, the ``use_tempaddr`` sysctl setting has to be set to
			   a value greater than zero and the given address needs to have a prefix length of
			   exactly ``64``. This flag allows to use privacy extensions in a manually
			   configured network, just like if stateless auto-configuration was active.
			   
			 * ``'NoDAD'``: (IPv6 only)
			   
			   Do not perform Duplicate Address Detection (:rfc:`4862#section-5.4`).
			   
			 * ``'NoPrefixRoute'``:
			   
			   Do not automatically create a route for the network prefix of the added address,
			   and don't search for one to delete when removing the address.
			   
			   Modifying an address to add this flag will remove the automatically added prefix
			   route, modifying it to remove this flag will create the prefix route automatically.
		
		scope : int|str
			.. _device-add-address-scope:
			
			The "distance" from this host to the next host on the network represented by `address`
			
			If this is a string is must have one of the following values:
			
			 * ``'Universe'``: (``0``)
			   
			   Address points to some host far, far away (default)
			   
			 * ``'Site'``: (``200``)
			 
			   Address points to a host that is located somewhere on the same network area
			   (like a server in the next room of the same data center)
			 
			 * ``'Link'``: (``253``)
			 
			   Address points to a host that is directly connected to this network host
			   (using this network link)
			 
			 * ``'Host'``: (``254``)
			 
			   Address points to this host (loopback address)
			 
			 * ``'Nowhere'``: (``255``)
			 
			   Reserved for non-existing destinations
			
			Intermediate (numeric) values, that are not listed here, are also possible. This can be
			used, for instance, to declare interior routes between ``'Universe'`` and ``'Link'``.
		
		peer : `str` | :func:`ipaddress.ip_address`
			.. _device-add-address-peer:
			
			The address of the remote endpoint for point-to-point interfaces
		
		broadcast : `str` | :func:`ipaddress.ip_address`
			.. _device-add-address-broadcast:
			
			The broadcast address on the interface
			
			The broadcast address is the address used when your host wants to comunicate with all
			devices on the local network.
		
		anycast : `str` | :func:`ipaddress.ip_address`
			.. _device-add-address-anycast:
		
		label : str
			.. _device-add-address-label:
			
			Custom label that may be used to tag individual addresses
			
			The label may only be up to 16 characters in length.
		
		valid_lft : int
			.. _device-add-address-valid-lft:
			
			The valid lifetime (in seconds) of this address
			
			When this value reaches ``0``, then this address is removed by the kernel.
			
			For details on lifetime handling please read :rfc:`4862#section-5.5.4`
		
		preferred_lft : int
			.. _device-add-address-preferred-lft:
			
			The preferred lifetime (in seconds) of this address
			
			When this value reaches ``0``, then this address won't be used for any new outgoing
			connections. This value must always be smaller than ``valid_lft``.
			
			For details on lifetime handling please read :rfc:`4862#section-5.5.4`.
		
		"""
		self._change_address('NewAddr', ('CREATE', 'EXCL'), address, *args, **kwargs)
	
	
	def modify_address(self, address, *args, create = False, **kwargs):
		"""
		Modify the flags of an existing IP address
		
		Parameters
		----------
		create : bool
			Add a new address to this interface, if no matching address exists
		
			See :meth:`~netlink.NetworkDevice.add_address` for a description of other possible parameters.
		"""
		nl_flags = ('CREATE', 'REPLACE') if create else ('REPLACE',)
		
		self._change_address('NewAddr', nl_flags, address, *args, **kwargs)
	
	
	def remove_address(self, address):
		"""
		Remove the given IP address from this interface
		
		Parameters
		----------
		address : `str` | :func:`ipaddress.ip_interface`
			An IP address (optionally) including the network prefix
			
			The string must be in the form of ``address/prefix_len``. Where ``address`` is an
			IP address in the form of ``a.b.c.d`` or ``a:b:c:d:e::f`` and ``prefix_len`` is
			the number of network address bits. If ``prefix_len`` is omitted then a prefix
			length of 32 bits for IPv4 and 128 bits for IPv6 will be assumed.
		"""
		self._change_address('DelAddr', (), address)
	
	
	def _change_address(self, nl_cmd, nl_flags, address,
				flags         = (),
				scope         = 0,
				peer          = None,
				broadcast     = None,
				anycast       = None,
				label         = None,
				valid_lft     = 0xFFFFFFFF,
				preferred_lft = 0xFFFFFFFF):
		sock = self._low_netlink
		
		# Parse given IP network interface address
		address = ipaddress.ip_interface(address)
		family  = socket.AF_INET if address.version == 4 else socket.AF_INET6
		
		# Create message header
		message = netlink.low.netlink.AddressRequest(sock, nl_cmd, nl_flags + ('REQUEST',))
		message.add_header(family, self.index, address.network.prefixlen, flags, scope)
		message.add_attribute('LOCAL', address.packed)
		
		# Set peer address (must be the same as `address` if not set to something else)
		if peer:
			peer = ipaddress.ip_address(peer)
			assert address.version == peer.version
			message.add_attribute('ADDRESS', peer.packed)
		else:
			message.add_attribute('ADDRESS', address.packed)
		
		# Set broadcast address
		if broadcast:
			broadcast = ipaddress.ip_address(broadcast)
			assert address.version == broadcast.version
			message.add_attribute('BROADCAST', broadcast.packed)
		
		# Set anycast address
		if anycast:
			anycast = ipaddress.ip_address(anycast)
			assert address.version == anycast.version
			message.add_attribute('ANYCAST', anycast.packed)
		
		# Set label address
		if label:
			label = label.encode('utf-8')
			assert len(label) <= 16
			message.add_attribute('LABEL', label)
		
		# Set cache information (maximum/valid and preferred lifetime)
		if valid_lft < 0xFFFFFFFF or preferred_lft < 0xFFFFFFFF:
			assert preferred_lft <= valid_lft, "preferred_lft is greater than valid_lft"
			message.add_attribute('CACHEINFO', {"preferred": preferred_lft, "valid": valid_lft})
		
		message.send()
	
	
	def get_interface(self):
		"""
		
		"""
		request = netlink.low.netlink.InterfaceRequest(self._low_netlink, 'GetLink', ('Request',))
		request.add_header(socket.AF_INET, self.index)
		
		(message, attributes) = request.send()[0]
		return self._process_interface(message, attributes)
	
	_BROKEN_LINK_ATTRIBUTES = (
		'WIRELESS', 'MAP', 'LINKINFO', 'LINKMODE', 'STATS', 'TXQLEN', 'NUM_VF', 'VFINFO_LIST',
		'STATS64', 'VF_PORTS', 'PORT_SELF', 'CARRIER', 'CARRIER_CHANGES'
	)
	#XXX: _BROKEN_LINK_ATTRIBUTES = ()
	@classmethod
	def _process_interface(self, message, attributes):
		# Add message properties as interface attributes
		attributes['FAMILY'] = message.family
		attributes['INDEX']  = message.index
		attributes['TYPE']   = message.TYPE.find(message.type)
		attributes['FLAGS']  = message.FLAG.find_bitmask(message.flags)
		
		# Remove all attributes that we cannot parse properly yet
		# (We don't want to expose half-broken stuff in the high-level API.)
		for name in list(attributes.keys()):
			if not isinstance(name, str) or name in self._BROKEN_LINK_ATTRIBUTES:
				del attributes[name]
		
		return attributes
	

	def get_addresses(self):
		"""
		Obtain all network addresses associated with this interface
		
		Returns a dictionary of network addresses and a dictionary of attributes of each address.
		
		**List of known attributes:**
		
		 * ``'ADDRESS'``: (*str*) – The network address itself
		 
		 * ``'LOCAL'``: (*str*) – The local network address
		   
		   Unless this device is connected to a network tunnel this will always be the same as
		   the value in ``'ADDRESS'``.
		 
		 * ``'PREFIXLEN'`` (*int*) – The length of the common network prefix in bits
		 
		 * ``'FAMILY'`` (*int*) – The address family value as integer
		   
		   Use the ``AF_*`` constants from the :mod:`socket` module to determine the address family
		   type.
		 
		 * ``'FLAGS'`` (*list*) – Flags set on the interface
		 
		   See the :ref:`flags parameter <device-add-address-flags>` of
		   :meth:`~netlink.NetworkDevice.add_address` for a list of possible values.
		
		 * ``'INDEX'`` (*int*) – The numerical index of the network device containing this address
		 
		 * ``'SCOPE'`` (*str* | *int*) – Network address *distance*
		 
		   See the :ref:`scope parameter <device-add-address-scope>` of
		   :meth:`~netlink.NetworkDevice.add_address` for details.
		 
		 * ``'LABEL'`` (*str*) – Custom free-text label attached to this address
		 
		   See the :ref:`label parameter <device-add-address-label>` of
		   :meth:`~netlink.NetworkDevice.add_address` for information.
		 
		 * ``'CACHEINFO'`` (*dict*) – Lifetime related attributes of this address:
		   
		    * ``'preferred'`` (*int*):
		      
		      Number of seconds that this address will be considered new outgoing connections
		      
		      See the :ref:`preferred_lft parameter <device-add-address-preferred-lft>` of
		      :meth:`~netlink.NetworkDevice.add_address` for details.
		    
		    * ``'valid'`` (*int*):
		      
		      Number of secons before this address will be removed entirely
		      
		      See the :ref:`valid_lft parameter <device-add-address-valid-lft>` of
		      :meth:`~netlink.NetworkDevice.add_address` for details.
		    
		    * ``'cstamp'`` (*int*)
		    
		    * ``'tstamp'`` (*int*)
		
		Example result of using :meth:`~netlink.NetworkDevice.get_addresses` on the loopback
		interface (``lo``):
		
		.. code-block:: python
			
			{
				'127.0.0.1': {
					'ADDRESS':   '127.0.0.1',
					'LOCAL':     '127.0.0.1',
					'PREFIXLEN': 8,
					'FAMILY':    2,
					'FLAGS':     ['PERMANENT'],
					'INDEX':     1,
					'SCOPE':     'HOST',
					'LABEL':     'lo',
					'CACHEINFO': {'cstamp': 602, 'preferred': 4294967295, 'tstamp': 1407340, 'valid': 4294967295}
				},
				'::1': {
					'ADDRESS':   '::1',
					'PREFIXLEN': 128,
					'FAMILY':    10,
					'FLAGS':     ['PERMANENT'],
					'INDEX':     1,
					'SCOPE':     'HOST',
					'CACHEINFO': {'cstamp': 602, 'preferred': 4294967295, 'tstamp': 602, 'valid': 4294967295}
				}
			}
		
		See the :ref:`print_all example <example-print-all>` for a more elaborate code sample.
		
		Returns
		-------
		dict
		"""
		sock = self._low_netlink
		
		request = netlink.low.netlink.AddressRequest(sock, 'GetAddr', ('Request', 'Dump'))
		request.add_header(socket.AF_UNSPEC, self.index, 0)
		request.add_attribute('LOCAL', b'\x7F\x00\x00\x01')
		
		response = {}
		for message, attributes in request.send():
			if message.index != self.index or 'ADDRESS' not in attributes:
				continue
			attributes = self._process_addresses(message, attributes)
			response[attributes['ADDRESS']] = attributes
		return response
	
	@classmethod
	def _process_addresses(self, message, attributes):
		# Add message properties as interface attributes
		attributes['FAMILY']    = message.family
		attributes['INDEX']     = message.index
		attributes['PREFIXLEN'] = message.prefixlen
		attributes['SCOPE']     = message.SCOPE.find(message.scope)
		attributes['FLAGS']     = message.FLAG.find_bitmask(message.flags)
		
		# Remove all attributes that we cannot parse properly yet
		# (We don't want to expose half-broken stuff in the high-level API.)
		for name in list(attributes.keys()):
			if not isinstance(name, str):
				del attributes[name]
		
		return attributes
	
	
	def get_statistics(self):
		"""
		Retrieve all available statistical information for the associated network interface
		
		Returns
		-------
		dict
		"""
		try:
			self._low_ethtool.set_device_name(self.name)
			
			# Get list of statistic labels for device
			strings = self._low_ethtool.get_stringset(netlink.struct.ethtool.SSetInfo.STATS)
			
			# Retrieve the actual statistical values from kernel
			import ctypes
			class StatsWithBuf(ctypes.Structure):
				_fields_ = (
					('hdr', netlink.struct.ethtool.Stats),
					('buf', ctypes.c_uint64 * len(strings))
				)
			stats = StatsWithBuf()
			stats.hdr.cmd     = netlink.struct.ethtool.Stats.CMD
			stats.hdr.n_stats = len(strings)
			self._low_ethtool.ioctl(stats)
			
			return collections.OrderedDict(zip(strings, stats.buf))
		except OSError as e:
			if e.errno == errno.ENOTSUP: # Operation not supported
				return collections.OrderedDict()
			else:
				raise


class Network:
	def __init__(self):
		self._low_netif   = netlink.low.netif.NetworkDeviceSocket()
		self._low_netlink = netlink.low.netif.RTNetlinkSocket()
	
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		self.close()
	
	def close(self):
		self._low_netif.close()
		self._low_netlink.close()
	
	
	def device(self, identifier):
		"""
		Obtain `NetworkDevice` instance for this network interface client
		
		Parameters
		----------
		identifier : int|str
			The name or index of the network device
		
		Returns
		-------
		:class:`~netlink.NetworkDevice`
		"""
		# Convert string network device names to network device indexes
		if isinstance(identifier, str):
			return NetworkDevice(None, identifier, self)
		else:
			return NetworkDevice(identifier, None, self)
	
	
	def device_index2name(self, index):
		"""
		Obtain the name for the network device with the given interface number
		
		Parameters
		----------
		index : int
			The interface number of the network device
		
		Raises
		------
		OSError
			System error reported during look up
			
			This usually means that there is no device with such number or that the interface does
			not have a name (since it is in another container for instance).
		
		Returns
		-------
		str
		"""
		request             = self._low_netif.create_request("")
		request.ifru.ivalue = index
		
		# GEIfName:  Get Interface Name
		self._low_netif.ioctl("GIfName", request)
		return request.ifrn_name.decode("ascii")
	
	
	def device_name2index(self, name):
		"""
		Obtain the index of the network device with the given interface name
		
		Parameters
		----------
		name : str
			The name of the network interface
		
		Raises
		------
		OSError
			System error reported during look up
			
			This usually means that there is no device with such number or that the interface does
			not have a name (since it is in another container for instance).
		
		Returns
		-------
		int
		"""
		request = self._low_netif.create_request(name)
		
		# GIfIndex: Get Interface Index
		self._low_netif.ioctl("GIFIndex", request)
		return request.ifru.ivalue
	
	
	def get_interfaces(self):
		"""
		
		"""
		sock = self._low_netlink
		
		request = netlink.low.netlink.InterfaceRequest(sock, 'GetLink', ('Request', 'Dump'))
		request.add_header(socket.AF_INET, 0)
		
		information = collections.OrderedDict()
		for message, attributes in request.send():
			# Unify network interface information
			attributes = NetworkDevice._process_interface(message, attributes)
			if 'IFNAME' not in attributes:
				continue
			
			# Create network device instance
			device = NetworkDevice(attributes['INDEX'], attributes['IFNAME'], self)
			
			# Store network device instance with its attributes
			information[device] = attributes
		return information
	
	def get_addresses(self):
		"""
		Get all network addresses of all devices
		
		Returns
		-------
		collections.OrderedDict
			Dictionary of device objects and addresses
			
			*Keys* (:class:`~netlink.NetworkDevice`):
				:class:`~netlink.NetworkDevice` objects, each representing a network interface
			
			*Values* (:class:`collections.OrderedDict`):
				Network address to attribute mappings as described in the documentation of the
				:meth:`netlink.NetworkDevice.get_addresses` method
		"""
		sock = self._low_netlink
		
		request = netlink.low.netlink.AddressRequest(sock, 'GetAddr', ('Request', 'Dump'))
		request.add_header(socket.AF_UNSPEC, 0, 0)
		
		information = collections.OrderedDict()
		for message, attributes in request.send():
			if 'ADDRESS' not in attributes:
				continue
			
			# Look for network device instance for device index referenced in the current message
			device = None
			for device in information.keys():
				if device.index == message.index:
					break
			if not device or device.index != message.index:
				device = NetworkDevice(message.index, None, self)
			
			if device not in information:
				information[device] = collections.OrderedDict()
			
			attributes = NetworkDevice._process_addresses(message, attributes)
			information[device][attributes['ADDRESS']] = attributes
		return information
	
	def get_interfaces_with_addresses(self):
		"""
		Get all network device along with their interface attributes and their addresses
		
		This is a convinience method that merges the results of
		:meth:`~netlink.Network.get_addresses` and :meth:`~netlink.Network.get_interfaces`. This
		method is a lot more efficient to use when performing look up of both network interface
		and network address information compared to using :meth:`~netlink.Network.get_interfaces`
		to obtain the network device list and then calling
		:meth:`netlink.NetworkDevice.get_addresses` on each result.
		
		
		"""
		# Obtain all interface information
		interfaces = self.get_interfaces()
		
		# Obtain all known address entries
		address_info = self.get_addresses()
		
		# Insert address list for every interface in its attributes
		for device, addresses in address_info.items():
			interfaces[device]["ADDRESSES"] = addresses
		
		# Add address slot in every interface attribute dict
		for device, attributes in interfaces.items():
			if "ADDRESSES" not in attributes:
				attributes["ADDRESSES"] = collections.OrderedDict()
		
		return interfaces