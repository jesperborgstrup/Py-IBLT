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
assert entries[0] == 'complete'
# Get set intersection, should contain all elements from pairs
intersect = set(pairs) & set(entries[1])
assert set( pairs ) == intersect
# Get set union, should contain only the elements from pairs
union = set(pairs) | set(entries[1])
assert set( pairs ) == union
