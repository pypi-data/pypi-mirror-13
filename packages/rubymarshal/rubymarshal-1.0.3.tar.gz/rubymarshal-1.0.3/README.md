RubyMarshal
===========

Read and write Ruby-marshalled data.
Only basics Ruby data types can be read and written: 

  * `float`,
  * `bool`,
  * `int`,
  * `str` (mapped to `unicode` in Python 2),
  * `nil` (mapped to `None` in Python),
  * `array` (mapped to `list`),
  * `hash` (mapped to `dict`),
  * symbols and other classes are mapped to specific Python classes.

Installation
------------

    pip install rubymarshal

Usage
-----


    from rubymarshal.reader import loads, load
    from rubymarshal.writer import writes, write
    with open('my_file', 'rb') as fd:
        content = load(fd)
    with open('my_file', 'wb') as fd:
        write(fd, my_object)
    loads(b"\x04\bi\xfe\x00\xff")
    writes(-256)
  
Infos
-----

Code is on github: https://github.com/d9pouces/RubyMarshal 
Documentation is on readthedocs: http://rubymarshal.readthedocs.org/en/latest/ 
Tests are on travis-ci: https://travis-ci.org/d9pouces/RubyMarshal