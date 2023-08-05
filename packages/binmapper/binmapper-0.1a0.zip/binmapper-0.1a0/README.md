# Binmapper

Python package for mapping objects to binary data.
It works with Python 2.7+

## Installation

Binmapper is available from https://pypi.python.org/pypi/binmapper and can be installed using pip

```sh
pip install binmapper
```

## Example usage

```python

import binmapper
import textwrap

definition = u"""\
    bintype BinX:
        field: uint8
    bintype Bin:
        fieldX: BinX
    """
definition = textwrap.dedent(definition)
binmap = binmapper.compile(definition)
bin = binmap.Bin()
input = io.BytesIO("\x01")
bin.parse(input)
print(bin.fieldX.field)
```

## Data types

Type    | Byte Size | Description
--------|-----------|--------------
uint8   |   1       |  Unsigned byte
uint16  |   2       |  Unsigned short
uint32  |   4       |  Unsigned short
sint8   |   1       |  Signed byte
sint16  |   2       |  Signed short
sint32  |   4       |  Signed word
float   |   4       |  Floating point with single-precision
string  |   n       |  String
array   |   n       |  Array

## Common class template

```python

bintype CLASS_NAME:
    FIELD_NAME : FIELD_TYPE &FIELD_ATTRIBUTE
    ...
    &CLASS_ATTRIBUTE = CLASS_ATTRIBUTE_VALUE
    ...
    &LET_FIELD_NAME = EXPRESSION
    ...
```
    
## Fields

## Byteorder

Value       | Description
------------|------------
littlendian | Increasing numeric significance with increasing memory addresses
bigendian   | Decreasing numeric significance with increasing memory addresses 

Byteorder can be specified 3-way

- Field attribute

    `field: uint8 &byteorder=littlendian`

    Apply only to field
  
- BinType attribute

        :::python
        field: uint8
        &byteorder=littlendian
    
    Apply to all fields in BinType, except having attribute byteorder
    
- Parse argument

        :::python
        bin.parse(input, byteorder='littlendian')

    Apply to all parsed data, except having attribute byteorder or BinType byteorder

Byteorder apply order:

    `field byteorder > class byteorder > parse byteorder`
 
## Class Usage

## Array Usage

## String Usage

## Let Field Usage

## Change elements in runtime 

   