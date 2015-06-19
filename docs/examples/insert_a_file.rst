Insert a File
#############

How to:

* Insert the contents of an input file into another input file.
* Reference a preprocessor variable in an ``insert`` directive.


File tree
*********

* :ref:`insert_a_file_example_py`
* src

  * :ref:`insert_a_file_html_html`
  * :ref:`insert_a_file_head_html`
  * :ref:`insert_a_file_body_html`
  * content

    * :ref:`content_celinejulie_html`
    * :ref:`content_daywrath_html`

* www

  * :ref:`celinejulie_html`
  * :ref:`daywrath_html`


Files
*****

.. _insert_a_file_example_py:

example.py
==========

.. literalinclude:: /../examples/basics/insert_a_file/example.py
    :emphasize-lines: 15-25, 40-42


.. _insert_a_file_html_html:

_html.html
==========

.. literalinclude:: /../examples/basics/insert_a_file/src/_html.html
    :language: html
    :emphasize-lines: 6, 10-11


.. _insert_a_file_head_html:

_head.html
==========

.. literalinclude:: /../examples/basics/insert_a_file/src/_head.html
    :language: html


.. _insert_a_file_body_html:

_body.html
==========

.. literalinclude:: /../examples/basics/insert_a_file/src/_body.html
    :language: html
    :emphasize-lines: 2


.. _content_celinejulie_html:

_celinejulie.html
=================

.. literalinclude:: /../examples/basics/insert_a_file/src/content/_celinejulie.html
    :language: html


.. _content_daywrath_html:

_daywrath.html
==============

.. literalinclude:: /../examples/basics/insert_a_file/src/content/_daywrath.html
    :language: html


.. _celinejulie_html:

celinejulie.html
================

.. literalinclude:: /../examples/basics/insert_a_file/www/celinejulie.html
    :language: html


.. _daywrath_html:

daywrath.html
=============

.. literalinclude:: /../examples/basics/insert_a_file/www/daywrath.html
    :language: html
