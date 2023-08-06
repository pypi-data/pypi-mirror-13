RIPE Atlas Sagan |Build Status| |Documentation|
===============================================

A parsing library for RIPE Atlas measurement results

Why this exists
---------------

RIPE Atlas generates a **lot** of data, and the format of that data changes over
time. Often you want to do something simple like fetch the median RTT for each
measurement result between date ``X`` and date ``Y``. Unfortunately, there are
dozens of edge cases to account for while parsing the JSON, like the format of
errors and firmware upgrades that changed the format entirely.

To make this easier for our users (and for ourselves), we wrote an easy to use
parser that's smart enough to figure out the best course of action for each
result, and return to you a useful, native Python object.

How to install
--------------

The stable version should always be in PyPi, so you can install it with ``pip``:

.. code:: bash

    $ pip install ripe.atlas.sagan

Better yet, make sure you get ujson and sphinx installed with it:

.. code:: bash

    $ pip install ripe.atlas.sagan[fast,doc]

Troubleshooting
~~~~~~~~~~~~~~~

Some setups (like MacOS) have trouble with building the dependencies required
for reading SSL certificates. If you don't care about SSL stuff and only want to
use sagan to say, parse traceroute or DNS results, then you can tell the
installer to skip building ``pyOpenSSL`` by doing the following:

.. code:: bash

    $ SAGAN_WITHOUT_SSL=1 pip install ripe.atlas.sagan

Quickstart: How To Use It
-------------------------

You can parse a result in a few ways. You can just pass the JSON-encoded string:

.. code:: python

    from ripe.atlas.sagan import PingResult

    my_result = PingResult("<result string from RIPE Atlas ping measurement>")

    print(my_result.rtt_median)
    123.456

    print(my_result.af)
    6

You can do the JSON-decoding yourself:

.. code:: python

    from ripe.atlas.sagan import PingResult

    my_result = PingResult(
        json.loads("<result string from RIPE Atlas ping measurement>")
    )

    print(my_result.rtt_median)
    123.456

    print(my_result.af)
    6

You can let the parser guess the right type for you, though this incurs a small
performance penalty:

.. code:: python

    from ripe.atlas.sagan import Result

    my_result = Result.get("<result string from RIPE Atlas ping measurement>")

    print(my_result.rtt_median)
    123.456

    print(my_result.af)
    6

What it supports
----------------

Essentially, we tried to support everything. If you pass in a DNS result string,
the parser will return a ``DNSResult`` object, which contains a list of
``Response``'s, each with an ``abuf`` property, as well as all of the
information in that abuf: header, question, answer, etc.

.. code:: python

    from ripe.atlas.sagan import DnsResult

    my_dns_result = DnsResult("<result string from a RIPE Atlas DNS measurement>")
    my_dns_result.responses[0].abuf  # The entire string
    my_dns_result.responses[0].abuf.header.arcount  # Decoded from the abuf

We do the same sort of thing for SSL measurements, traceroutes, everything. We
try to save you the effort of sorting through whatever is in the result.

Which attributes are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every result type has its own properties, with a few common between all types.

Specifically, these attributes exist on all ``*Result`` objects:

-  ``created`` An datetime object of the
   ``timestamp`` field
-  ``measurement_id``
-  ``probe_id``
-  ``firmware`` An integer representing the firmware version
-  ``origin`` The ``from`` attribute in the result
-  ``is_error`` Set to ``True`` if an error was found

Additionally, each of the result types have their own properties, like
``packet_size``, ``responses``, ``certificates``, etc. You can take a look at
the classes themselves, or just look at the tests if you're curious. But to get
you started, here are some examples:

.. code:: python

    # Ping
    ping_result.packets_sent  # Int
    ping_result.rtt_median    # Float, rounded to 3 decimal places
    ping_result.rtt_average   # Float, rounded to 3 decimal places

    # Traceroute
    traceroute_result.af                   # 4 or 6
    traceroute_result.total_hops           # Int
    traceroute_result.destination_address  # An IP address string

    # DNS
    dns_result.responses                        # A list of Response objects
    dns_result.responses[0].response_time       # Float, rounded to 3 decimal places
    dns_result.responses[0].headers             # A list of Header objects
    dns_result.responses[0].headers[0].nscount  # The NSCOUNT value for the first header
    dns_result.responses[0].questions           # A list of Question objects
    dns_result.responses[0].questions[0].type   # The TYPE value for the first question
    dns_result.responses[0].abuf                # The raw, unparsed abuf string

    # SSL Certificates
    ssl_result.af                        # 4 or 6
    ssl_result.certificates              # A list of Certificate objects
    ssl_result.certificates[0].checksum  # The checksum for the first certificate

    # HTTP
    http_result.af                      # 4 or 6
    http_result.uri                     # A URL string
    http_result.responses               # A list of Response objects
    http_result.responses[0].body_size  # The size of the body of the first response

    # NTP
    ntp_result.af                          # 4 or 6
    ntp_result.stratum                     # Statum id
    ntp_result.version                     # Version number
    ntp_result.packets[0].final_timestamp  # A float representing a high-precision NTP timestamp
    ntp_result.rtt_median                  # Median value for packets sent & received

What it requires
----------------

As you might have guessed, with all of this magic going on under the hood, there
are a few dependencies:

-  `pyOpenSSL`_ (Optional: see "Troubleshooting" above)
-  `python-dateutil`_
-  `pytz`_

Additionally, we recommend that you also install `ujson`_ as it will speed up
the JSON-decoding step considerably, and `sphinx`_ if you intend to build the
documentation files for offline use.

Running Tests
-------------

There's a full battery of tests for all measurement types, so if you've made
changes and would like to submit a pull request, please run them (and update
them!) before sending your request:

.. code:: bash

    $ python setup.py test

You can also install ``tox`` to test everything in all of the supported Python
versions:

.. code:: bash

    $ pip install tox
    $ tox

Further Documentation
---------------------

Complete documentation can always be found on `Read the Docs`_,
and if you're not online, the project itself contains a ``docs`` directory --
everything you should need is in there.


Who's Responsible for This?
---------------------------

Sagan is actively maintained by the RIPE NCC and primarily developed by `Daniel
Quinn`_, while the abuf parser is mostly the responsibility of `Philip Homburg`_
with an assist from Bert Wijnen and Rene Wilhelm who contributed to the original
script. `Andreas Stirkos`_ did the bulk of the work on NTP measurements and
fixed a few bugs, and big thanks go to `Chris Amin`_, `John Bond`_, and
`Pier Carlo Chiodi`_ for finding and fixing stuff where they've run into
problems.


Colophon
--------

But why "`Sagan`_"? The RIPE Atlas team decided to name all of its modules after
explorers, and what better name for a parser than that of the man who spent
decades reaching out to the public about the wonders of the cosmos?

.. _pyOpenSSL: https://pypi.python.org/pypi/pyOpenSSL
.. _python-dateutil: https://pypi.python.org/pypi/python-dateutil
.. _pytz: https://pypi.python.org/pypi/pytz
.. _ujson: https://pypi.python.org/pypi/ujson
.. _sphinx: https://pypi.python.org/pypi/Sphinx
.. _Read the Docs: http://ripe-atlas-sagan.readthedocs.org/en/latest/
.. _Daniel Quinn: https://github.com/danielquinn
.. _Philip Homburg: https://github.com/philiphomburg
.. _Andreas Stirkos: https://github.com/astrikos
.. _Chris Amin: https://github.com/chrisamin
.. _John Bond: https://github.com/b4ldr
.. _Pier Carlo Chiodi: https://github.com/pierky
.. _Sagan: https://en.wikipedia.org/wiki/Carl_Sagan
.. |Build Status| image:: https://travis-ci.org/RIPE-NCC/ripe.atlas.sagan.png?branch=master
   :target: https://travis-ci.org/RIPE-NCC/ripe.atlas.sagan
.. |Documentation| image:: https://readthedocs.org/projects/ripe-atlas-sagan/badge/?version=latest
   :target: http://ripe-atlas-sagan.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status


Changelog
=========
* 1.1.10
    * Added a `parse_all_hops` kwarg to the Traceroute class to tell Sagan to stop parsing Hops and Packets once we have all of the last hop statistics (default=True)
    * Remove dependency on IPy: we were using it for IPv6 canonicalization, but all IPv6 addresses in results should be in canonical form to start with.
* 1.1.9
    * Removed the `parse_abuf` script because no one was using it and its
      Python3 support was suspect anyway.
* 1.1.8
    * Handle case where a traceroute result might not have ``dst_addr`` field.
* 1.1.7
    * Change condition of traceroute's ``last_hop_responded`` flag.
    * Add couple of more traceroute's properties. ``is_success`` and ``last_hop_errors``.
    * Add tests to the package itself.
* 1.1.6
    * Fix for `Issue #56`_ a case where the ``qbuf`` value wasn't being properly
      captured.
    * Fixed small bug that didn't accurately capture the ``DO`` property from
      the qbuf.
* 1.1.5
    * We now ignore so-called "late" packets in traceroute results.  This will
      likely be amended later as future probe firmwares are expected to make
      better use of this value, but until then, Sagan will treat these packets
      as invalid.
* 1.1.4
    * Added a ``type`` attribute to all ``Result`` subclasses
    * Added support for a lot of new DNS answer types, including ``NSEC``,
      ``PTR``, ``SRV``, and more.  These answers do not yet have a complete
      string representation however.
* 1.1.3
    * Changed the name of ``TracerouteResult.rtt_median`` to
      ``TracerouteResult.last_rtt_median``.
    * Modified the ``DnsResult`` class to allow the "bubbling up" of error
      statuses.
* 1.1.2
    * We skipped this number for some reason :-/
* 1.1.1
    * Fixed a `string representation bug`_ found by `iortiz`_
* 1.1.0
    * **Breaking Change**: the ``Authority`` and ``Additional`` classes were
      removed, replaced with the appropriate answer types.  For the most part,
      this change should be invisible, as the common properties are the same,
      but if you were testing code against these class types, you should
      consider this a breaking change.
    * **Breaking Change**: The ``__str__`` format for DNS ``RrsigAnswer`` to
      conform the output of a typical ``dig`` binary.
    * Added ``__str__`` definitions to DNS answer classes for use with the
      toolkit.
    * In an effort to make Sagan (along with Cousteau and the toolkit) more
      portable, we dropped the requirement for the ``arrow`` package.
* 1.0.0
    * 1.0! w00t!
    * **Breaking Change**: the ``data`` property of the ``TxtAnswer`` class was
      changed from a string to a list of strings.  This is a correction from
      our own past deviation from the RFC, so we thought it best to conform as
      part of the move to 1.0.0
    * Fixed a bug where non-ascii characters in DNS TXT answers resulted in an
      exception.
* 0.8.2
    * Fixed a bug related to non-ascii characters in SSL certificate data.
    * Added a wrapper for json loaders to handle differences between ujson and
      the default json module.
* 0.8.1
    * Minor fix to make all ``Result`` objects properly JSON serialisable.
* 0.8.0
    * Added `iortiz`_'s patch for flags and ``flags``
      and ``sections`` properties on DNS ``Answer`` objects.
* 0.7.1
    * Changed ``README.md`` to ``README.rst`` to play nice with pypi.
* 0.7
    * Added `pierky`_'s new ``RRSigAnswer`` class to
      the dns parser.
* 0.6.3
    * Fixed a bug in how Sagan deals with inappropriate firmware versions
* 0.6.2
    * Added `pierky`_'s fix to fix AD and CD flags
      parsing in DNS Header
* 0.6.1
    * Added ``rtt_min``, ``rtt_max``, ``offset_min``, and ``offset_max`` to
      ``NTPResult``
* 0.6.0
    * Support for NTP measurements
    * Fixes for how we calculate median values
    * Smarter setup.py
* 0.5.0
    * Complete Python3 support!
* 0.4.0
    * Added better Python3 support.  Tests all pass now for ping, traceroute,
      ssl, and http measurements.
    * Modified traceroute results to make use of ``destination_ip_responded``
      and ``last_hop_responded``, deprecating ``target_responded``.  See the
      docs for details.
* 0.3.0
    * Added support for making use of some of the pre-calculated values in DNS
      measurements so you don't have to parse the abuf if you don't need it.
    * Fixed a bug in the abuf parser where a variable was being referenced by
      never defined.
    * Cleaned up some of the abuf parser to better conform to pep8.
* 0.2.8
    * Fixed a bug where DNS ``TXT`` results with class ``IN`` were missing a
      ``.data`` value.
    * Fixed a problem in the SSL unit tests where ``\n`` was being
      misinterpreted.
* 0.2.7
    * Made abuf more robust in dealing with truncation.
* 0.2.6
    * Replaced ``SslResult.get_checksum_chain()`` with the
      ``SslResult.checksum_chain`` property.
    * Added support for catching results with an ``err`` property as an actual
      error.
* 0.2.5
    * Fixed a bug in how the ``on_error`` and ``on_malformation`` preferences
      weren't being passed down into the subcomponents of the results.
* 0.2.4
    * Support for ``seconds_since_sync`` across all measurement types
* 0.2.3
    * "Treat a missing Type value in a DNS result as a malformation" (Issue #36)
* 0.2.2
    * Minor bugfixes
* 0.2.1
    * Added a ``median_rtt`` value to traceroute ``Hop`` objects.
    * Smarter and more consistent error handling in traceroute and HTTP
      results.
    * Added an ``error_message`` property to all objects that is set to ``None``
      by default.
* 0.2.0
    * Totally reworked error and malformation handling.  We now differentiate
      between a result (or portion thereof) being malformed (and therefore
      unparsable) and simply containing an error such as a timeout.  Look for
      an ``is_error`` property or an ``is_malformed`` property on every object
      to check for it, or simply pass ``on_malformation=Result.ACTION_FAIL`` if
      you'd prefer things to explode with an exception.  See the documentation
      for more details
    * Added lazy-loading features for parsing abuf and qbuf values out of DNS
      results.
    * Removed the deprecated properties from ``dns.Response``.  You must now
      access values like ``edns0`` from ``dns.Response.abuf.edns0``.
    * More edge cases have been found and accommodated.
* 0.1.15
    * Added a bunch of abuf parsing features from
      `b4ldr`_ with some help from
      `phicoh`_.
* 0.1.14
    * Fixed the deprecation warnings in ``DnsResult`` to point to the right
      place.
* 0.1.13
    * Better handling of ``DNSResult`` errors
    * Rearranged the way abufs were handled in the ``DnsResult`` class to make
      way for ``qbuf`` values as well.  The old method of accessing ``header``,
      ``answers``, ``questions``, etc is still available via ``Response``, but
      this will go away when we move to 0.2.  Deprecation warnings are in place.
* 0.1.12
    * Smarter code for checking whether the target was reached in
      ``TracerouteResults``.
    * We now handle the ``destination_option_size`` and
      ``hop_by_hop_option_size`` values in ``TracerouteResult``.
    * Extended support for ICMP header info in traceroute ``Hop`` class by
      introducing a new ``IcmpHeader`` class.
* 0.1.8
    * Broader support for SSL checksums.  We now make use of ``md5`` and
      ``sha1``, as well as the original ``sha256``.

.. _Issue #56: https://github.com/RIPE-NCC/ripe.atlas.sagan/issues/56
.. _string representation bug: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/1
.. _b4ldr: https://github.com/b4ldr
.. _phicoh: https://github.com/phicoh
.. _iortiz: https://github.com/iortiz
.. _pierky: https://github.com/pierky


