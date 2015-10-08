Change Log
##########

Release updates are available via `Atom feed <https://github.com/nre/doxhooks/releases.atom>`_ and `Twitter <https://twitter.com/doxhooks>`_.


0.5.0
*****

*2015-10-08*

Breaking changes:

* `ResourceFactory` has been rewritten to be easier to extend.
* `FileTree` arguments are renamed:

  * `leaf` -> `filename`.
  * `branch` -> `dir_path`.
  * `branches` -> `roots`.

* `FileTree.path` returns an absolute path or an *explicitly* relative path.
* `ResourceAddress` is superseded by `ServerConfiguration`.
* `urls` are superseded by `DataStore` and `UrlMapping`.
* `Preprocessor` constructor argument `root_input_file` and `Preprocessor.start` are eliminated.
* `Preprocessor.input_files` are renamed as `Preprocessor.input_paths`.
* `context_vars` is a keyword argument of `PreprocessorFactory.make`.


New features:

* `DataStore`.
* Python 3.5 compatibility.


Bug fixes:

* The `Preprocessor` indentation level leaked into subsequent preprocessor stacks.


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
