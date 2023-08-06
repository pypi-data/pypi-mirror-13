import ctypes



class GStrings(ctypes.Structure):
	CMD = 0x0000001b
	
	LENGTH = 32
	
	_fields_ = [
		('cmd',        ctypes.c_uint32),
		('string_set', ctypes.c_uint32),
		('len',        ctypes.c_uint32),
	]

class SSetInfo(ctypes.Structure):
	CMD = 0x00000037
	
	STATS = 1
	
	_fields_ = [
		('cmd',       ctypes.c_uint32),
		('reserved',  ctypes.c_uint32),
		('sset_mask', ctypes.c_uint64),
	]

class Stats(ctypes.Structure):
	CMD = 0x0000001d
	
	_fields_ = [
		('cmd',     ctypes.c_uint32),
		('n_stats', ctypes.c_uint32),
	]
