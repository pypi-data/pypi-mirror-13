Changelog
=========

0.4.0 (2016-01-11)
------------------

New
~~~

- Avoid reordering mapping keys in the output. [Valentin Lab]

  Several commands from ``shyaml`` will output YAML themselves. But in the
  process, the whole content is parsed and re-dumped. This can lead to
  differences with the original inputs. The ordering of keys can be
  annoying in some use cases, even if, well mappings should not be
  ordered, these are ordered by the sequential nature of a file, and using
  'omap' is often tedious. ``shyaml`` now keep the original order the keys
  were met.


0.3.4 (2015-03-06)
------------------

New
~~~

- Added a nice ``--help`` doc. [Valentin Lab]

- Added ``key-values{,-0}`` argument to get key and values in one go.
  [Valentin Lab]

- Error is casted if no default specified and the key is not existent.
  [Valentin Lab]

Changes
~~~~~~~

- Be more informative in some key related error message. (fixed #7)
  [Valentin Lab]

0.2.2 (2014-03-19)
------------------

Fix
~~~

- No argument at all was treated as one empty string argument. Thx Yassa
  Bb. (fixes #6) [Valentin Lab]

0.2.1 (2013-11-23)
------------------

New
~~~

- Python3 support. [Valentin Lab]

Fix
~~~

- Keys can now be empty or contains dots ``.`` if they are properly
  escaped (fixes #5, thanks to Daniel Giribet) [Daniel Giribet]

0.2.0 (2013-05-03)
------------------

New
~~~

- Support for iteration in sequence and struct in one go. [Valentin Lab]

Fix
~~~

- Forgot to mention ``./autogen.sh`` execution when getting the code
  from git, and be more clear about other means of installation.
  [Valentin Lab]

0.1.3 (2013-03-29)
------------------

Fix
~~~

- Removed the spurious line feed at the end of any ``shyaml`` output.
  [Valentin Lab]

- Support querying for... nothing. Which now returns the whole input
  YAML. [Valentin Lab]

  Before this fix, you couldn't ask for ``shyaml get-value`` alone, even if it
  makes sense but is completely useless as it returns the whole YAML input.


0.1.2 (2013-03-23)
------------------

New
~~~

- Support for list indexes (see README.rst). [Valentin Lab]

- Catch exceptions when parsing structure and output a clean error
  message. [Valentin Lab]

0.1.1 (2013-02-27)
------------------

Changes
~~~~~~~

- Some minor enhancements, and an "Install" section. [Valentin Lab]

0.1.0 (2013-02-27)
------------------

- First import. [Valentin Lab]


