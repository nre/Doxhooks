Features
########

Doxhooks lets you abstract away the content and maintenance of files in your project. Doxhooks has three main classes of abstractions: `Resources <resource>`:term: (files), `preprocessors <preprocessor>`:term: and preprocessor `mini-languages <mini-language>`:term:.


Resources
*********

* Refer to files and directories by names, instead of hard-coding the paths.
* Refer to a `resource`:term: URL by the name of the resource, instead of hard-coding the URL.
* Give a resource a default URL (based on its output path) or override the default.
* `Mangle <fingerprint>`:term: a URL and output filename with a custom `fingerprint`:term: of the resource content.
* Update one resource, or all the resources, or all the resources that depend on a given input file.
* Specify the order in which resources are updated.
* Mix and match resources with preprocessors and preprocessor mini-languages.


Preprocessors
*************

* Create customised `preprocessors <preprocessor>`:term: by extending and overriding other preprocessors, including the built-in general-purpose lexical preprocessor.
* Use different types of preprocessors for different types of resources in the same project.
* Customise the delimiters of the `preprocessor directives <preprocessor directive>`:term: and `variables <preprocessor node>`:term:.
* Apply character encodings and newline conventions to the output files.
* Replace HTML character references with Unicode characters, other character references, etc.
* See a preprocessor 'stack trace' when an error occurs in a preprocessor directive or variable.
* Evaluate preprocessor variables `recursively and late <preprocessor node>`:term:.
* Mix and match preprocessors with preprocessor mini-languages.


Preprocessor Mini-Languages
***************************

* Create customised preprocessor `mini-languages <mini-language>`:term: by extending and overriding other preprocessor mini-languages, including the built-in preprocessor mini-language.
* Use different types of preprocessor mini-languages for different types of resources in the same project.
* Share data that is common to different resources by using preprocessor variables and the inheritance hierarchy of your preprocessor mini-languages.
* Create your own domain-specific keywords in addition to the built-in keywords: ``insert`` or ``include`` a file, ``write`` a line, ``set`` a variable, raise an ``error`` or print a ``warning``, ``if`` a condition is true.
* Represent boolean output values in lowercase (``true``) or start-case (``True``), or exclude boolean as a valid output type.