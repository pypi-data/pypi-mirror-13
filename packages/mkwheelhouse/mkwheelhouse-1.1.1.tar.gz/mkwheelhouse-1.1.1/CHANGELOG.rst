Changelog
=========

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

`1.1.1` - 2016 January 23
-----------------------------

Fixed
~~~~~

- mkwheelhouse can actually build wheelhouses in S3 subdirectories
  `#8`_. Thanks, `@rajiteh`_!


`1.1.0`_ - 2015 April 24
-----------------------------

Added
~~~~~

- mkwheelhouse learned to build wheelhouses in S3 subdirectories (key
  prefixes) `#2`_. Thanks, `@j-martin`_!


`1.0.0`_ - 2015 April 23
------------------------

Changed
~~~~~~~

- Boto replaced Botocore. Boto is a higher-level AWS API that provides
  better error messages. mkwheelhouse's documented functionality should
  remain unchanged, but if you were relying on error messages, you may
  be impacted. **[BREAKING]**
- Documentation converted to reStructuredText.


`0.3.1`_ - 2015 April 23
------------------------

Added
~~~~~

-  This CHANGELOG.
-  Unofficial Python 2.6 support [`#6`_\ ]. Thanks, `@prologic`_!


.. _1.1.1: https://github.com/WhoopInc/mkwheelhouse/compare/1.1.0...1.1.1
.. _1.1.0: https://github.com/WhoopInc/mkwheelhouse/compare/1.0.0...1.1.0
.. _1.0.0: https://github.com/WhoopInc/mkwheelhouse/compare/0.3.1...1.0.0
.. _0.3.1: https://github.com/WhoopInc/mkwheelhouse/compare/0.3.0...0.3.1

.. _#2: https://github.com/WhoopInc/mkwheelhouse/pull/2
.. _#6: https://github.com/WhoopInc/mkwheelhouse/pull/6
.. _#8: https://github.com/WhoopInc/mkwheelhouse/pull/8

.. _@j-martin: https://github.com/j-martin
.. _@prologic: https://github.com/prologic
.. _@rajiteh: https://github.com/rajiteh
