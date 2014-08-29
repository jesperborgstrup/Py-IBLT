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

# Test if inserting and deleting results in an empty table
#print t
#print t.T
#print
for i in range( 24 ):
	t.insert( "key%d" % i, "val%d" % i )
#t.dump()
#print t.T
print t.list_entries()
print len( t.list_entries() )
print t.get( "ksey" )
print t.get( "key" )
print
#t.delete( "ksey", "val" )
#print t.T
#print
#print t.get( "ksey" )
#print t.get( "key" )

#t.list_entries()

#for i in range( 5 ):
#print  "%d: %s" % ( i, t.hash( i, "hej") )