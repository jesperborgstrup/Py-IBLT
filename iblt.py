# MIT License
#
# Copyright (C) 2014 Jesper Borgstrup
# -------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import hashlib, math, struct
from copy import deepcopy

class IBLT:
	# m is amount of cells in underlying lookup table
	m = None
	# k is amount of hash functions
	k = None
	# key_size is maximum size for keys
	key_size = None
	# value_size is maximum size for values
	value_size = None
	# hash_key_sum_size is amount of bytes used for the hashkeySum field
	hash_key_sum_size = None
	# hash is function( i, value ), where i is index of hash function
	# and value is value to be hashed
	hash = None

	empty_key_array = None
	empty_hash_sum_array = None

	RESULT_GET_NO_MATCH = "no_match"
	RESULT_GET_MATCH = "match"
	RESULT_GET_DELETED_MATCH = "deleted_match"
	RESULT_GET_INCONCLUSIVE = "inconclusive"
	RESULT_LIST_ENTRIES_COMPLETE = "complete"
	RESULT_LIST_ENTRIES_INCOMPLETE = "incomplete"

	def __init__( self, m, k, key_size, value_size, hash_key_sum_size=10, hash=None ):
		"""
		m is the amount of cells in underlying lookup table
		k is the amount of hash functions
		key_size is maximum size for keys
		value_size is maximum size for values
		hash_key_sum_size is amount of bytes used for the hashkeySum field
		hash is function( i, value ), where i is index of hash function
		    and value is value to be hashed (or None for default hash functions)
		"""
		self.m = m
		self.k = k
		self.key_size = key_size
		self.value_size = value_size
		self.hash_key_sum_size = hash_key_sum_size
		self.hash = hash if hash is not None else self.__hash
		self.T = [[0,[0 for j in range( key_size )],[0 for j in range( value_size )],[0 for j in range( hash_key_sum_size )]] for i in range( m )]
		self.empty_key_array = [0 for i in range( self.key_size )]
		self.empty_hash_sum_array = [0 for i in range( self.hash_key_sum_size )]

	def insert( self, key, value ):
		"""
		Insert the key/value pair into the IBLT.
		No return value.
		"""
		return self.__insert( self.T, key, value )

	def __insert( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			# Increase count
			T[index][0] += 1
			# Add key to keySum
			T[index][1] = self.__sum_int_arrays( T[index][1], self.__value_to_int_array( key, self.key_size ) )
			# Add value to valueSum
			T[index][2] = self.__sum_int_arrays( T[index][2], self.__value_to_int_array( value, self.value_size ) )
			# Add key hash to hashkeySum
			T[index][3] = self.__sum_int_arrays( T[index][3], self.__value_to_int_array( IBLT.get_key_hash( key ), self.hash_key_sum_size ) )

	def delete( self, key, value ):
		"""
		Delete a key/value pair from the IBLT.
		No return value.
		"""
		return self.__delete( self.T, key, value )

	def __delete( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		key_array = self.__value_to_int_array( key, self.key_size )
		value_array = self.__value_to_int_array( value, self.value_size )
		for index in indices:
			# Decrease count
			T[index][0] -= 1
			# Subtract key from keySum
			T[index][1] = self.__diff_int_arrays( T[index][1], key_array )
			# Subtract value from valueSum
			T[index][2] = self.__diff_int_arrays( T[index][2], value_array )
			# Subtract key hash from hashkeySum
			T[index][3] = self.__diff_int_arrays( T[index][3], self.__value_to_int_array( IBLT.get_key_hash( key ), self.hash_key_sum_size ) )

	def get( self, key ):
		"""
		Try to get a value from the table with the given key.
		This function can return four different responses:

		( IBLT.RESULT_GET_NO_MATCH, None ): The key was definitively not in the table
		( IBLT.RESULT_GET_MATCH, <Value> ): The key was in the table and the value is returned
		( IBLT.RESULT_GET_DELETED_MATCH, <Value> ): The key was deleted without being inserted
		( IBLT.RESULT_GET_INCONCLUSIVE, None ): It couldn't be determined if the key was in the table or not
		"""
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			if self.T[index][0] == 0 and \
					self.T[index][1] == self.empty_key_array and \
					self.T[index][3] == self.empty_hash_sum_array:
				return ( IBLT.RESULT_GET_NO_MATCH, None )
			elif self.T[index][0] == 1 and \
					self.T[index][1] == self.__value_to_int_array( key, self.key_size ) and \
					self.T[index][3] == self.__value_to_int_array( IBLT.get_key_hash( key ), self.hash_key_sum_size ):
				return ( IBLT.RESULT_GET_MATCH, self.__int_array_to_value( self.T[index][2] ) )
			elif self.T[index][0] == -1 and \
					self.T[index][1] == self.__negate_int_array( self.__value_to_int_array( key, self.key_size ) )and \
					self.T[index][3] == self.__negate_int_array( self.__value_to_int_array( IBLT.get_key_hash( key ), self.hash_key_sum_size ) ):
				return ( IBLT.RESULT_GET_DELETED_MATCH, self.__int_array_to_value( self.__negate_int_array( self.T[index][2] ) ) )
		return ( IBLT.RESULT_GET_INCONCLUSIVE, None )

	def list_entries( self ):
		"""
		Tries to list all entries in the table.

		Returns ( <Result>, [<Normal entries>], [<Deleted entries>] )
		where <Result> is either IBLT.RESULT_LIST_ENTRIES_COMPLETE to indicate that the list is complete,
		or IBLT.RESULT_LIST_ENTRIES_INCOMPLETE to indicate that some entries couldn't be recovered
		"""
		T = deepcopy( self.T )
		entries = []
		deleted_entries = []
		# Inefficient worst case O(n^2) loop, the paper says
		# "It is a fairly straightforward exercise to implement this method in O(m) time, say, by
		# using a link-list-based priority queue of cells in T indexed by their count fields and
		# modifying the DELETE method to update this queue each time it deletes an entry from B."
		while True:
			for i in range( len( T ) ):
				entry = T[i]
				if entry[0] == 1 or entry[0] == -1:
					if entry[0] == 1 and \
							entry[3] == self.__value_to_int_array( IBLT.get_key_hash( self.__int_array_to_value( entry[1] ) ), self.hash_key_sum_size ):
						key = self.__int_array_to_value( entry[1] )
						value = self.__int_array_to_value( entry[2] )
						entries.append( ( key, value ) )
						self.__delete( T, key, value )
						break
					elif entry[0] == -1 and \
							self.__negate_int_array( entry[3] ) == self.__value_to_int_array( IBLT.get_key_hash( self.__int_array_to_value( self.__negate_int_array( entry[1] ) ) ), self.hash_key_sum_size ):
						key = self.__int_array_to_value( self.__negate_int_array( entry[1] ) )
						value = self.__int_array_to_value( self.__negate_int_array( entry[2] ) )
						deleted_entries.append( ( key, value ) )
						self.__insert( T, key, value )
						break
			else:
				break

		if any( filter( lambda e: e[0] != 0, T ) ):
			return ( IBLT.RESULT_LIST_ENTRIES_INCOMPLETE, entries, deleted_entries )
		return ( IBLT.RESULT_LIST_ENTRIES_COMPLETE, entries, deleted_entries )

	def is_empty( self ):
		"""
		Returns true if the table is completely empty, i.e. no contains no entries,
		inserted or deleted
		"""
		return all( map( lambda e: e[0] == 0, self.T ) )

	def serialize( self ):
		"""
		Serialize the IBLT for storage or transfer.

		Data format:
			[ Magic bytes ][  Header ][ Data ]
		    	4 bytes      6 bytes    

		Magic bytes: 
			0x49 0x42 0x4C 0x54 (ASCII for IBLT)

		Header:
			[ Cell count (m) ]
			  	32-bit uint

			[ Key sum length ][ Value sum length ]
			  	32-bit uint			32-bit uint

			[ HashKeySum length ][ ValueKeySum length ]
				32-bit uint				32-bit uint

			[ # hash funcs (k) ]
				32-bit uint

		Data:
			For each of the m cells:
				[ 	Count 	 ][ keySum ][ valueSum ][ hashKeySum ][ valueKeySum ]
				  32-bit int

		"""
		magic = struct.pack( ">I", 0x49424C54 )
		header = struct.pack( ">IIIIII", self.m, self.key_size, self.value_size, 
										 self.hash_key_sum_size, 0, self.k )
		data = ""
		for cell in self.T:
			# Count (32-bit signed int)
			data += struct.pack( ">i", cell[0] )
			# keySum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[1] ) )
			# valueSum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[2] ) )
			# hashKeySum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[3] ) )

		return magic + header + data

	@staticmethod
	def unserialize( data ):
		header = struct.unpack( ">IIIIIII", data[:(4*7)] )
		magic = header[0]
		if magic != 0x49424C54:
			raise Exception( "Invalid magic value" )

		m, key_size, value_size, hash_key_sum_size, hash_value_sum_size, k = header[1:7]
		t = IBLT( m, k, key_size, value_size, hash_key_sum_size )

		expected_data_length = m * ( 4 + key_size + value_size + hash_key_sum_size + hash_value_sum_size )
		if len( data ) - 28 != expected_data_length:
			raise Exception( "Invalid data size: Expected %d, was %d" % ( expected_data_length, len( data ) - 28 ) )

		# 4 x 7 bytes offset from magic value and header
		offset = 28
		for i in range( m ):
			t.T[i][0] = struct.unpack( ">i", data[offset:offset+4])[0]
			offset += 4
			t.T[i][1] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+key_size] )
			offset += key_size
			t.T[i][2] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+value_size] )
			offset += value_size
			t.T[i][3] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+hash_key_sum_size] )
			offset += hash_key_sum_size

		return t

	def get_serialized_size( self ):
		# Magic bytes
		result = 4
		# Header
		result += 6 * 4
		# Cells
		result += self.m * ( 4 + self.key_size + self.value_size + self.hash_key_sum_size )
		return result

	def dump( self ):
		IBLT.__dump( self.T )

	@staticmethod
	def __dump( T ):
		print "DUMP START::::::::::::::::::::::"
		print "Count sum: %d" % sum( map( lambda e: e[0], T ) )
		print "Non-empty count: %d" % len( filter( lambda e: e[0] > 0, T ) )
		print "Below-zero sum: %d" % sum( map( lambda e: e[0], filter( lambda e: e[0] < 0, T ) ) )
		print "Below-zero count: %d" % len( filter( lambda e: e[0] < 0, T ) )
		for i in range( len( T ) ):
			e = T[i]
#			if e[0] > 0:
			print "%d: %s" % ( i, e )
		print "DUMP END::::::::::::::::::::::::"

	@staticmethod
	def get_key_hash( key ):
		return hashlib.sha512( key ).digest()

	hash_hex_length = None
	def __hash( self, i, value ):
		if self.hash_hex_length == None:
			# Find the shortest length to extract from the hash,
			# get the bit length of m and divide by four to get hex length
			self.hash_hex_length = int( math.ceil( math.log( self.m, 2 ) / 4.0 ) )
		if not 0 <= i < self.k:
			raise Exception( 'Hash i must be between 0 and %d (%d)' % ( self.k, i ) )
		return int( hashlib.sha512( str( i ) + value ).hexdigest()[:self.hash_hex_length], 16 ) % self.m

	def __sum_int_arrays( self, arr1, arr2 ):
		assert len( arr1 ) == len( arr2 )
		result = [0 for i in range( len( arr1 ) ) ]
		for i in range( len( arr1 ) ):
			result[i] = ( arr1[i] + arr2[i] ) % 256
		return result

	def __diff_int_arrays( self, arr1, arr2 ):
		assert len( arr1 ) == len( arr2 )
		result = [0 for i in range( len( arr1 ) ) ]
		for i in range( len( arr1 ) ):
			result[i] = ( arr1[i] - arr2[i] ) % 256
		return result

	def __value_to_int_array( self, value, length ):
		return [ord(value[i]) if i < len( value ) else 0 for i in range( length )]

	def __int_array_to_value( self, arr ):
		return "".join( [ chr(i) for i in arr if i != 0 ] )

	def __negate_int_array( self, arr ):
		return map( lambda i: (256-i) % 256, arr )

	def __eq__( self, other ):
		# Check if correct class
		if not isinstance( other, IBLT ):
			return False

		# Check if variables match
		if not all( ( ( self.m == other.m ),
					  ( self.k == other.k ),
				      ( self.key_size == other.key_size ),
				 	  ( self.value_size == other.value_size ),
					  ( self.hash_key_sum_size == other.hash_key_sum_size ),
					  ( len( self.T ) == len( other.T ) ) ) ):
			return False

		# Check if actual data match
		for i in xrange( self.m ):
			c1, c2 = self.T[i], other.T[i]
			if c1 != c2:
				return False
		return True