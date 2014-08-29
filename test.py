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

from iblt import IBLT

t = IBLT( 30, 4, 10, 10 )
assert t.is_empty()

# Test if inserting and deleting the same pair in an empty table
# results in an empty table again
t.insert( "testkey", "testvalue" )
assert not t.is_empty()
t.delete( "testkey", "testvalue" )
assert t.is_empty()


# Test if inserting 10 key/value pairs can be listed out
pairs = [( "key%d" % i, "value%d" % i ) for i in range( 10 )]
for key, value in pairs:
	t.insert( key, value )
entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
# Get set intersection, should contain all elements from pairs
intersect = set(pairs) & set(entries[1])
assert set( pairs ) == intersect
# Get set union, should contain only the elements from pairs
union = set(pairs) | set(entries[1])
assert set( pairs ) == union


# Test if deleting a key/value pair that hasn't been inserted before
# doesn't result in bad list_entries() or get()
t = IBLT( 30, 4, 10, 10 )
t.delete( "delkey", "delval" )
t.insert( "inskey", "insval" )
entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
# One inserted entry
assert len( entries[1] ) == 1
assert entries[1][0] == ( "inskey", "insval" )
# One deleted entry
assert len( entries[2] ) == 1
assert entries[2][0] == ( "delkey", "delval" )
assert t.get( "inskey" ) == ( IBLT.RESULT_GET_MATCH, "insval" )
assert t.get( "delkey" ) == ( IBLT.RESULT_GET_DELETED_MATCH, "delval" )


# Test if inserting more that m=30 keys/values will result in an incomplete listing
# and then remove some of them again to get a complete listing
t = IBLT( 30, 4, 10, 10 )
pairs = [( "key%d" % i, "value%d" % i ) for i in range( 31 )]
for key, value in pairs:
	t.insert( key, value )

assert t.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_INCOMPLETE
pairs_to_keep = pairs[:15]
pairs_to_delete = pairs[15:]
for key, value in pairs_to_delete:
	t.delete( key, value )

entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
assert len( entries[1] ) == len( pairs_to_keep )
# Check if returned entries are the same as in pairs_to_keep
assert len( set( entries[1] ).difference( set( pairs_to_keep ) ) ) == 0
# Check that returned entries contains none of the pairs_to_delete
assert len( set( entries[1] ).intersection( set( pairs_to_delete ) ) ) == 0