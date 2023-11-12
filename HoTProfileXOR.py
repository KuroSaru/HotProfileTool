#!/bin/python3

import sys, struct, os
from enum import Enum
from pprint import pprint

XOR_Key = 0x04 #Actual Key - Intended Key 38481156 (0x24b2d04)

def main(args):
	if ((len(sys.argv)<=1)):
		fname_in = "HoT_profile.dat"
	else:
		fname_in = sys.argv[1]
	fname_out = fname_in+".xored"

	print("Xoring (in:",fname_in,") to (out:",fname_out,") using key:", hex(XOR_Key))

	with open(fname_in,"rb") as fin:
		FileData = fin.read() #read in whole file.
		with open(fname_out, "wb") as fout:
			for byte in FileData:
				fout.write( struct.pack("<B", byte ^ XOR_Key) )

	with open(fname_out, "r") as fout:
		tmp = fout.read(60)
		if "ProfileVersion" in tmp:
			print("File has been sucessfully Decrypted.")
			ParseProfile(fname_out)
		else:
			print("File has been sucessfully Encrypted.")

GodotSerialiseTypes  = ['NIL','BOOL','INT','FLOAT','STRING','VECTOR2',
						'VECTOR2I','RECT2','RECT2I','VECTOR3','VECTOR3I',
						'TRANSFORM2D','VECTOR4','VECTOR4I','PLANE',
						'QUATERNION','AABB','BASIS','TRANSFORM3D','PROJECTION',
						'COLOR','STRING_NAME','NODE_PATH','RID','OBJECT','CALLABLE',
						'SIGNAL','DICTIONARY','ARRAY','PACKED_BYTE_ARRAY','PACKED_INT32_ARRAY',
						'PACKED_INT64_ARRAY','PACKED_FLOAT32_ARRAY','PACKED_FLOAT64_ARRAY',
						'PACKED_STRING_ARRAY','PACKED_VECTOR2_ARRAY','PACKED_VECTOR3_ARRAY',
						'PACKED_COLOR_ARRAY','VARIANT_MAX','EOF']

def ParseProfile(filename):
	DataArray = []
	print("Parsing contents (",filename,") to readable format.")
	with open(filename, "rb") as fin:
		fin.seek(0, os.SEEK_END)
		fin_EOF = fin.tell() 
		fin.seek(0, os.SEEK_SET)

		DataArray = ReadNextObject(fin)

		while fin.tell() < fin_EOF:
			DataArray = DataArray + ReadNextObject(fin)
	pprint(DataArray)
	print('Done.')

def ReadNextObject(fhandle):
	raw = fhandle.read(4)
	if not raw: return ''
	raw_enum_type = struct.unpack("<i",raw)[0]	

	if raw_enum_type == 27: #Dictionary
		 return ReadDictionary(fhandle)

	elif raw_enum_type == 1: #Bool
		return ReadBool(fhandle)

	elif raw_enum_type == 2: #int
		return ReadInt(fhandle)

	elif raw_enum_type == 4: #String
		return ReadString(fhandle)

	elif raw_enum_type == 28: #Array
		return ReadArray(fhandle)

	else:
		print('unsupported -- ',GodotSerialiseTypes[raw_enum_type],':',str(raw_enum_type),'')
		print('FileOffset: ',fhandle.tell())
		return ''

def ReadDictionary(fhandle):
	Items = {}
	ItemCount = struct.unpack("<i", fhandle.read(4))[0]
	for i in range(0,ItemCount):
		item_name = ReadNextObject(fhandle)
		item_value = ReadNextObject(fhandle)
		Items[item_name] = item_value
	return Items

def ReadString(fhandle):
	Len = struct.unpack("<i", fhandle.read(4))[0]

	#super ugly way to make sure string is 4byte aligned.
	if Len > 4:
		if ((Len % 4) > 0):
			Alignment = (4 - (Len % 4))
		else:
			Alignment = 0
		Raw = fhandle.read(Len + Alignment)
		ret = Raw[:Len].decode('utf-8')
	else:
		if Len == 0:
			ret = ''
		else:
			Raw = fhandle.read(4)
			ret = Raw.decode('utf-8')[:Len]
	return ret

def ReadInt(fhandle):
	return struct.unpack("<i", fhandle.read(4))[0]

def ReadBool(fhandle):
	return ( struct.unpack("<i", fhandle.read(4))[0] == 1)

def ReadArray(fhandle):
	Count = struct.unpack("<i", fhandle.read(4))[0]
	Items = []

	for i in range(0,Count):
		Items = Items + [ReadNextObject(fhandle)]
	return Items

if __name__=="__main__":
	main(sys.argv)
