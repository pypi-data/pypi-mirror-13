Python bindings for the snappy compression library from Google.

More details about Snappy library: http://code.google.com/p/snappy

This package is statically built against the snappy codebase so that we do not
need to ship libsnappy.so together with the python module. This makes it easier
to host on PyPi.


