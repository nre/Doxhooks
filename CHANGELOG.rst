Change Log
##########

Release updates are available via `Atom feed <https://github.com/nre/doxhooks/releases.atom>`_ and `Twitter <https://twitter.com/doxhooks>`_.


0.4.0
*****

*2015-06-23*

Breaking changes:

* Optional whitespace between the opening delimiter and the keyword of a preprocessor directive is no longer the default. This behaviour can be restored, e.g.::

    @directive_delimiter("##[ \t]*")
    class MyPreprocessor(Preprocessor):
        pass


0.3.0
*****

*2015-06-16*

Breaking changes:

* Changes to the public APIs of `FileTree`, `InputFileDomain` and `OutputFileDomain`.
* `InputFileTree` and `OutputFileTree` are eliminated.


Bug fixes:

* `output_branches` had priority over `url_branches` in the URL file tree.


0.2.0
*****

*2015-06-04*

New features:

* Python 3.3 compatibility.


Bug fixes:

* System and example tests failed on \*nix.
* `importattr` caught secondhand import errors.
