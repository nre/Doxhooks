Glossary
########

.. glossary::
    :sorted:

    address
        See `information resource`:term:.

    branch
        See `file tree`:term:.

    directive
        See `preprocessor directive`:term:.

    Doxhooks
        This Python package that you are reading about.

        Doxhooks lets you abstract away the content and maintenance of files in your project.

    file tree
        Directories and files that are organised into a structure.

        A *branch* is a path within that file tree.

        `Doxhooks`:term: file trees are instances of `~doxhooks.filetrees.FileTree`.

    fingerprint
        A common dilemma in Web development is deciding how long to cache resources that are indirectly requested by the client. These resources are typically images, fonts, scripts and stylesheets. A solution is that the cache lifetime can be arbitrarily long if the URL of the resource changes whenever the content of the resource changes. One way to change the URL is to mangle the resource filename with a fingerprint of the file contents, e.g. ``myfile.css`` becomes ``myfile-c1285a47.css``.

        `Doxhooks`:term: has a `~doxhooks.fingerprint` module that performs this task.

    ID
    identity
        See `information resource`:term:.

    information resource
        An information resource is information that has an *identity*. A request for the resource is sent to the *address* of the resource. The response is a *representation* of the information. The representation can depend on who requested the resource, and when, why and how it was requested.

        `Doxhooks`:term: information resources are instances of `~doxhooks.resources.Resource`.

    mangle
        See `fingerprint`:term:.

    mini-language
        A small domain-specific language.

        `Doxhooks`:term: `preprocessor`:term: mini-languages are subclasses of `~doxhooks.preprocessor_contexts.BasePreprocessorContext`.

    preprocessed resource
        See `information resource`:term:.

    preprocessor
        A program that modifies a source text before the text is processed by another program. The second program can be a browser, compiler, interpreter, server, etc.

        `Doxhooks`:term: preprocessors are instances of `~doxhooks.preprocessors.Preprocessor`.

    preprocessor directive
        An instruction embedded in a source text that controls how the source text is `preprocessed <preprocessor>`:term:.

        These instructions are written in a preprocessor `mini-language`:term:.

    preprocessor node
        A name that more accurately describes the behaviour of a *preprocessor variable* in `Doxhooks`:term:.

        Doxhooks `preprocesses <preprocessor>`:term: the value of a variable in the same way that it preprocesses input files (except that any `preprocessor directives <preprocessor directive>`:term: in the value are ignored).

        In other words, a Doxhooks preprocessor variable can store an 'expression', and these expressions are evaluated recursively and late.

        This is like evaluating a syntax tree, or flattening a tree of strings. So a Doxhooks preprocessor variable is more like a *node* in a tree.

        `Doxhooks`:term: preprocessor nodes are implemented by variables in a preprocessor `mini-language`:term:.

    preprocessor variable
        See `preprocessor node`:term:.

    representation
        See `information resource`:term:.

    resource
        See `information resource`:term:.

    root
        See `file tree`:term:.
