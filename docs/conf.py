# TODO: replace `(self|cls).x` with `ClassName.x`? Or just `.x`?
# - Have to walk the mro to find the right class?
# - What if it's an instance variable? Always added by __init__?
# TODO: Parameter interpreted text (e.g. `param`) should link to the
#   function. Function parameters are func.__code__.co_varnames.
# - I can get the parameters during the autodoc-process-docstring event,
#   but running regexp replace on each line would be expensive?
# - I can get the module and class names from the missing-reference
#   event node arg, but not the function or method name.

import os
import sys


doxhooks_docs_path = os.path.dirname(__file__)
doxhooks_dist_path = os.path.join(doxhooks_docs_path, os.pardir)
sys.path.insert(0, doxhooks_dist_path)


from doxhooks import __version__


is_rtd_build = os.environ.get("READTHEDOCS", None) == "True"
needs_sphinx = "1.3"

project = "Doxhooks"
copyright = "2015 Nick Evans"
version = release = __version__

master_doc = "index"
source_suffix = ".rst"
nitpicky = False

default_role = "obj"
add_function_parentheses = False  # Erratic when default_role = "obj".
add_module_names = False

if not is_rtd_build:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_use_smartypants = True
html_domain_indices = False  # If True, see modindex_common_prefix.
html_show_sourcelink = False


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "docs.sphinx_ext.init_method_docstrings",  # Before interface_docstrings.
    "docs.sphinx_ext.interface_docstrings",  # After autodoc, before napoleon.
    "sphinx.ext.napoleon",
    "docs.sphinx_ext.first_line_rubric",
    # "docs.sphinx_ext.print_docstrings",  # Debug preprocessed docstrings.
    # "sphinx.ext.viewcode",
]

autoclass_content = "class"  # "class" skips __init__ docstrings.
autodoc_member_order = "alphabetical"  # __all__ orders module members.

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
