import ctypes

import netlink.struct.ethtool


class ETHTool:
	def __init__(self, device_name, netif):
		self.netif   = netif
		self.request = netif.create_request(device_name)
		
		self._cache = {}
	
	
	def set_device_name(self, device_name):
		self.request.ifrn_name = device_name.encode('ascii')
	
	
	def ioctl(self, command):
		"""
		Send the given ETHTool command to kernel using the 
		"""
		self.request.ifru.data = ctypes.addressof(command)
		self.netif.ioctl("ethtool", self.request)
	
	
	def get_stringset(self, set_id):
		"""
		Retrieve a list of available strings for the given `set_id` from the kernel
		"""
		if set_id not in self._cache:
			class SSetInfoWithBuf(ctypes.Structure):
				_fields_ = [
					('hdr', netlink.struct.ethtool.SSetInfo),
					('buf', ctypes.c_uint32 * 1),
				]
			sset_info = SSetInfoWithBuf()
			
			# Ask kernel for number of strings
			sset_info.hdr.cmd       = netlink.struct.ethtool.SSetInfo.CMD
			sset_info.hdr.sset_mask = 1 << set_id
			self.ioctl(sset_info)
			length = sset_info.buf[0]
			
			# Actually retrieve the list of strings from the kernel
			class GStringsWithBuf(ctypes.Structure):
				_fields_ = (
					('hdr', netlink.struct.ethtool.GStrings),
					('buf', ctypes.c_char * netlink.struct.ethtool.GStrings.LENGTH * length)
				)
			strings = GStringsWithBuf()
			strings.hdr.cmd        = netlink.struct.ethtool.GStrings.CMD
			strings.hdr.string_set = set_id
			strings.hdr.len        = length
			if strings.hdr.len > 0:
				self.ioctl(strings)
			
			# Extract list of names from result
			array2string = lambda ca: ctypes.cast(ca, ctypes.c_char_p).value.decode('ascii')
			names = list(map(array2string, strings.buf))
			
			self._cache[set_id] = names
		
		return self._cache[set_id]
