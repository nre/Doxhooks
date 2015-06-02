Doxhooks
########

.. image:: https://travis-ci.org/nre/Doxhooks.svg?branch=master
    :target: https://travis-ci.org/nre/Doxhooks

Doxhooks helps you to write and maintain the files in your project by letting you write abstractions for your content and tasks. You can abstract away your duplicate content, boilerplate code, debug code, modules, templates, data, cross-references, file paths, URLs, build tasks, etc. You can even abstract away the preprocessor logic by defining your own preprocessor mini-languages.

Beginners can start using Doxhooks by customising the example scripts. Users with knowledge of the Python programming language can extend Doxhooks with their own code.

Doxhooks is open-source software distributed under an MIT license. The latest versions of the Doxhooks `distribution package <https://pypi.python.org/pypi/doxhooks>`_, `documentation <http://doxhooks.readthedocs.org/>`_ and `source code <https://github.com/nre/doxhooks>`_ are available online.


Features
********

Doxhooks has three main classes of abstractions: Resources (files), preprocessors and preprocessor mini-languages.


Resources
=========

* Refer to files and directories by names, instead of hard-coding the paths.
* Refer to a resource URL by the name of the resource, instead of hard-coding the URL.
* Give a resource a default URL (based on its output path) or override the default.
* Mangle a URL and output filename with a custom fingerprint of the resource content.
* Update one resource, or all the resources, or all the resources that depend on a given input file.
* Specify the order in which resources are updated.
* Mix and match resources with preprocessors and preprocessor mini-languages.


Preprocessors
=============

* Create customised preprocessors by extending and overriding other preprocessors, including the built-in general-purpose lexical preprocessor.
* Use different types of preprocessors for different types of resources in the same project.
* Customise the delimiters of the preprocessor directives and variables.
* Apply character encodings and newline conventions to the output files.
* Replace HTML character references with Unicode characters, other character references, etc.
* See a preprocessor 'stack trace' when an error occurs in a preprocessor directive or variable.
* Evaluate preprocessor variables recursively and late.
* Mix and match preprocessors with preprocessor mini-languages.


Preprocessor mini-languages
===========================

* Create customised preprocessor mini-languages by extending and overriding other preprocessor mini-languages, including the built-in preprocessor mini-language.
* Use different types of preprocessor mini-languages for different types of resources in the same project.
* Share data that is common to different resources by using preprocessor variables and the inheritance hierarchy of your preprocessor mini-languages.
* Create your own domain-specific keywords in addition to the built-in keywords: ``insert`` or ``include`` a file, ``write`` a line, ``set`` a variable, raise an ``error`` or print a ``warning``, ``if`` a condition is true.
* Represent boolean output values in lowercase (``true``) or start-case (``True``), or exclude boolean as a valid output type.
