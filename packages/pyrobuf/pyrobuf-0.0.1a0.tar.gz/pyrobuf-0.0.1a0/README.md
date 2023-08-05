# Pyrobuf Library

### Introduction

Pyrobuf is an alternative to Google's Python Protobuf library. Pyrobuf generates
lightning-fast Cython code that's 2-4x faster than Google's Python Protobuf
library using their C++ backend and 20-40x faster than Google's pure-python
implementation. What's more, Pyrobuf is self-contained and easy to install.

### Requirements

Pyrobuf requires Cython (`sudo pip install cython`), setuptools (`sudo pip
install setuptools`), and Jinja2 (`sudo pip install Jinja2`). Pyrobuf *does
not* require protoc. Pyrobuf has been tested with Python 2.7 and Python 3.4.

### Compiling

When you `pip install pyrobuf` you get the pyrobuf CLI tool ...:

    $ pyrobuf --help
    usage: pyrobuf [-h] [--out-dir OUT_DIR] [--build-dir BUILD_DIR] [--install]
                   source

    a Cython based protobuf compiler

    positional arguments:
      source                filename.proto or directory containing proto files

    optional arguments:
      -h, --help            show this help message and exit
      --out-dir OUT_DIR     cythonize output directory [default: out]
      --build-dir BUILD_DIR
                            C compiler build directory [default: build]
      --install             install the extension [default: False]

### Use

Suppose you have installed `test_message.proto` which contains a spec for the
message `Test`. In Python, you can import your new message class by running:
```
from test_message_proto import Test
```

With the message class imported, we can create a new message:
```
test = Test()
```

Now that we have instantiated a message `test`, we can fill individual fields:
```
>>> test.field = 5
>>> test.req_field = 2
>>> test.string_field = "hello!"
>>> test.list_fieldx.append(12)
>>> test.test_ref.field2 = 3.14
```

And access those same fields:
```
>>> test.string_field
'hello!'
```

Once we have at least filled out any "required" fields, we can serialize to a
byte array:
```
>>> test.SerializeToString()
bytearray(b'\x10\x05\x1a\x06hello! \x0c2\t\x19\x1f\x85\xebQ\xb8\x1e\t@P\x02')
```

We can also deserialize a protobuf message to our message instance:
```
>>> test.ParseFromString('\x10\x05\x1a\x06hello! \x0c2\t\x19\x1f\x85\xebQ\xb8\x1e\t@P\x02')
25
```
Note that the `ParseFromString` method returns the number of bytes consumed.

In addition to serializing and deserializing to and from protobuf messages,
Pyrobuf also allows us to serialize and deserialize to and from JSON and native
Python dictionaries:
```
>>> test.SerializeToJson()
'{"field": 5, "req_field": 2, "list_fieldx": [12], "string_field": "hello!", "test_ref": {"field2": 3.14}}'

>>> test.ParseFromJson('{"field": 5, "req_field": 2, "list_fieldx": [12], "string_field": "hello!", "test_ref": {"field2": 3.14}}')

>>> test.SerializeToDict()
{'field': 5,
 'list_fieldx': [12],
 'req_field': 2,
 'string_field': 'hello!',
 'test_ref': {'field2': 3.14}}

>>> test.ParseFromDict({'field': 5, 'list_fieldx': [12], 'req_field': 2, 'string_field': 'hello!', 'test_ref': {'field2': 3.14}})
```

### Performance

On my development machine (Ubuntu 14.04), Pyrobuf is roughly 2.0x as fast as
Google's library for message serialization and 2.3x as fast for message
deserialization when using the C++ backend for Google's library:
```
> python tests/perf_test.py
Google took 1.649168 seconds to serialize
Pyrobuf took 0.825525 seconds to serialize
Google took 1.113041 seconds to deserialize
Pyrobuf took 0.466113 seconds to deserialize
```

When not using the C++ backend, Pyrobuf is roughly 25x as fast for serialization
and 55x as fast for deserialization:
```
Google took 20.215662 seconds to serialize
Pyrobuf took 0.819555 seconds to serialize
Google took 24.990137 seconds to deserialize
Pyrobuf took 0.455732 seconds to deserialize
```

### Differences from the Google library

For the most part, Pyrobuf should be a drag-and-drop replacement for the Google
protobuf library. There are a few differences, though. First, Pyrobuf does not
currently implement the `MergeFrom` and `MergeFromString` methods that allow you
to populate a message class from multiple protobuf messages. We may add these
methods later.

Second, Pyrobuf simply assumes that the schema being used for a given message
is the same on the send and receive ends, so changing the type of a field on
one end without changing it on the other may cause bugs; adding or removing
fields will not break anything.
