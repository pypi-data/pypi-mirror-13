
Package versions
-------------------------------

Implements version numbers, e.g. for use in your custom package/module/extension/addon system.

Version ranges are stored as VersionRange and can be created using syntax similar to pip:

.. code-block:: python

    VersionRange('==3')
    # >=3.0,<4.0
    VersionRange('<=2.5,>1')
    # >=2.0,<=2.5
    VersionRange('==2.*')
    # >=2.0,<3.0

The main functionality is the combination of version ranges as best as possible, which is needed in case two packages rely on the same third package, but with different version limitations:

.. code-block:: python

    VersionRange('<=2.5,>1') & VersionRange('==2.*')
    #>=2.0,<=2.5
    VersionRange('<4.4') & VersionRange('>0,<=7')
    #>=1.0,<4.4
    VersionRange('<4.4') & VersionRange('>5.3')
    #==5.3 and an optional warning or error (due to the mismatch in range)

It can also choose the most appropriate version among a list of options:

.. code-block:: python

    options = ['0.0.0', '2.8.', '2.1.unordered', '1.0.dev1', '2.2.words', '2.9.9', '999.999.0']
    VersionRange('>=2.2,<2.9').choose(options)
    # 2.8
    VersionRange('>2.2,<2.8').choose(options)
    # 2.8. and an optional warning or error (due to no match in range)
    VersionRange('>2.2').choose(options)
    # 999.999.0

And parse package dependencies:

.. code-block:: python

    parse_dependency('package>=3')
    # ('package', VersionRange(>=3.0))
    parse_dependency('specialname123>2.0,<3')
    # ('specialname123', VersionRange(>=2.1,<3.0))
    parse_dependencies('packA>1.3,<6\n#packskip==*\n\npackB<3.4#,>1.2')
    # OrderedDict([('packa', VersionRange(>=1.4,<6.0)), ('packb', VersionRange(<=3.3))])

For a lot more examples, see the unit tests.

Installation
-------------------------------

Install using:

    pip install package-versions

Import using:

    from package_versions import VersionRange, parse_dependencies

You're ready to go!

Restrictions
-------------------------------

A restriction this package imposes is that it assumed that feature versions are pairs of at most two integers, like `11.7` but not `11.7.3` or `1.7dev`.

Version `11.7.3` is assumed to contain only bug-fixes compared to `11.7`, and as such will always be preferred. Personally I like this unambiguous interpretation, but it's up to you if you accept it.

Due to internal representation, there is a maximum for major and minor versions of 46340.

Package names roughly follow Python module naming guide (start with a letter, lowercase, not too long). Note that some systems treat upper and lower case as the same, so it's probably wise to keep this restriction.

Tests
-------------------------------

There are a lot of py.test unit tests that you can run using:

.. code-block:: bash

    python3 -m pytest

License
-------------------------------

BSD 3-clause “Revised” License. Keep the license file and understand that I'm not to be held liable, and then you're free to do pretty much whatever.


