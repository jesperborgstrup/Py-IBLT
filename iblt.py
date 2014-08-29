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

import hashlib, math
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
	# hash is function( i, value ), where i is index of hash function
	# and value is value to be hashed
	hash = None

	def __init__( self, m, k, key_size, value_size, hash=None ):
		"""
		m is the amount of cells in underlying lookup table
		k is the amount of hash functions
		key_size is maximum size for keys
		value_size is maximum size for values
		hash is function( i, value ), where i is index of hash function
		    and value is value to be hashed (or None for default hash functions)
		"""
		self.m = m
		self.k = k
		self.T = [[0,[0 for j in range( key_size )],[0 for j in range( value_size )]] for i in range( m )]
		self.key_size = key_size
		self.value_size = value_size
		self.hash = hash if hash is not None else self.__hash

	def insert( self, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			# Increase count
			self.T[index][0] += 1
			# Add key to keySum
			self.T[index][1] = self.__sum_int_arrays( self.T[index][1], self.__value_to_int_array( key, self.key_size ) )
			# Add value to valueSum
			self.T[index][2] = self.__sum_int_arrays( self.T[index][2], self.__value_to_int_array( value, self.value_size ) )

	def delete( self, key, value ):
		return self.__delete( self.T, key, value )

	def __delete( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		key_array = self.__value_to_int_array( key, self.key_size )
		value_array = self.__value_to_int_array( value, self.value_size )
		for index in indices:
			# Decrease count
			T[index][0] -= 1
			# Add key to keySum
			T[index][1] = self.__diff_int_arrays( T[index][1], key_array )
			# Add value to valueSum
			T[index][2] = self.__diff_int_arrays( T[index][2], value_array )

	def get( self, key ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			if self.T[index][0] == 0:
				return None
			elif self.T[index][0] == 1:
				if self.T[index][1] == self.__value_to_int_array( key, self.key_size ):
					return self.__int_array_to_value( self.T[index][2] )
				else:
					return None
		return "not found"

	def list_entries( self ):
		T = deepcopy( self.T )
		result = []
		# Inefficient worst case O(n^2) loop, the paper says
		# "It is a fairly straightforward exercise to implement this method in O(m) time, say, by
		# using a link-list-based priority queue of cells in T indexed by their count fields and
		# modifying the DELETE method to update this queue each time it deletes an entry from B."
		while True:
			for i in range( len( T ) ):
				entry = T[i]
				if entry[0] == 1:
					key = self.__int_array_to_value( entry[1] )
					value = self.__int_array_to_value( entry[2] )

					result.append( ( key, value ) )
					self.__delete( T, key, value )
					break
			else:
				break

		if any( filter( lambda e: e[0] != 0, T ) ):
			return ( "incomplete", result )
		return ( "complete", result )

	def is_empty( self ):
		return all( map( lambda e: e[0] == 0, self.T ) )

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