# Py-IBLT

A Python implementation of [Invertible Bloom Lookup Tables](http://arxiv.org/abs/1101.2245)

## Invertible Bloom Lookup Table
From the abstract of the paper (2011):

We present a version of the Bloom filter data structure that supports not only the insertion, deletion, and lookup of key-value pairs, but also allows a complete listing of its contents with high probability, as long the number of key-value pairs is below a designed threshold. Our structure allows the number of key-value pairs to greatly exceed this threshold during normal operation. Exceeding the threshold simply temporarily prevents content listing and reduces the probability of a successful lookup. If later entries are deleted to return the structure below the threshold, everything again functions appropriately. We also show that simple variations of our structure are robust to certain standard errors, such as the deletion of a key without a corresponding insertion or the insertion of two distinct values for a key. The properties of our structure make it suitable for several applications, including database and networking applications that we highlight. 

## Notes

* Records that are deleted without a corresponding insert operation can be recovered with the `get` and `list_entries` functions. 
* Duplicate keys are not supported.

## Usage

### Constructor

Use the constructor to create a new IBLT:
```
from iblt import IBLT
t = IBLT( m, k, key_size, value_size, hash_key_sum_size=10, hash=None )
```

*m* is the amount of cells in underlying lookup table, and is closely related to the threshold value that determines how many key/value pairs the IBLT can hold before giving inconclusive answers to queries.
*k* is the amount of hash functions to be used.
*key_size* is maximum size for keys.
*value_size* is maximum size for values.
*hash_key_sum_size* is amount of bytes used for the hashkeySum field.
*hash* is function( i, value ), where i is index of hash function and value is value to be hashed (or None for default hash functions).

### Insert and delete

The `insert` function inserts a key/value pair into the IBLT.

```
t.insert( key, value )
```

The `delete` function likewise deletes a key/value pair from the IBLT.

```
t.delete( key, value )
```

The `insert` and `delete` functions do not have any return values.

### Retrieving a value based on a key

The `get` function tries to retrieve a value by key and gives you additional information on how the operation went:

```
t.get( key )
```

For the `get` function, the return value is `( <Result>, <Value> )`.
The `<Result>` value can be one of the following four possibilities:

* `IBLT.RESULT_GET_NO_MATCH` It is certain that no such key exists in the table. `<Value>` is `None`.
* `IBLT.RESULT_GET_MATCH` The key was previously inserted into the table and the value is returned in `<Value>`.
* `IBLT.RESULT_GET_DELETED_MATCH` The key was found, but it had been deleted instead of inserted and the value is returned in `<Value>`.
* `IBLT.RESULT_GET_INCONCLUSIVE` It wasn't possible to determine if the key was in the table or not. `<Value>` is `None`.

### Listing entries

The `list_entries` function tries to extract a complete list of all entries in the table. It either returns all entries or an incomplete list:

```
t.list_entries()
```

The return value of `list_entries` is `( <Result>, [<Entries>], [<Deleted entries>] )`.

The `<Result>` value is one of two possibilities:

* `IBLT.RESULT_LIST_ENTRIES_COMPLETE` The entries lists are complete.
* `IBLT.RESULT_LIST_ENTRIES_INCOMPLETE`: It wasn't possible to extract a complete listing. Only the returned entries were recoverable.

The `<Entries>` list contains all recoverable entries that have been inserted into the table.
Likewise, the `<Deleted entries>` list contains all recoverable entries that have been deleted from the table without being inserted.

### Serializing and unserializing

Table instances have a `serialize` function, that takes no argument and serializes the data and metadata of the table for into a bitstring storage or communication.

Likewise, the IBLT class has a static `unserialize` function that takes the serialized bitstring and constructs a copy of the table from the bitstring.

```
# t is an IBLT instance
s = t.serialize()

# Prints True
print IBLT.unserialize( s ) == t
```
