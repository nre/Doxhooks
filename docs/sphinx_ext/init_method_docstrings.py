import textwrap

from .interface_docstrings import interface_titles


def insert_init_method_docstring(app, what, name, obj, options, lines):
    """Insert __init__ method docstring in class docstring."""
    if what != "class" and what != "exception":
        return

    # Do not insert the __init__ docstring if it is inherited.
    if "__init__" not in obj.__dict__:
        return

    init_method_doc = obj.__init__.__doc__
    # Silently ignore missing __init__ docstring.
    if not init_method_doc:
        return

    init_method_docstring = textwrap.dedent(init_method_doc)
    init_method_doc_lines = init_method_docstring.splitlines()[2:]
    # Have two blank lines between __init__ method docstring
    # and the class docstring line that it is inserted before.
    init_method_doc_lines.extend(("", ""))

    numbered_lines = enumerate(lines)

    # Insert __init__ method docstring before Interface section.
    for line_no, line in numbered_lines:
        if line in interface_titles:
            __, next_line = next(numbered_lines)

            underline = "-" * len(line)
            if next_line != underline:
                # Don't worry about next_line being an interface title.
                continue

            lines[line_no:line_no] = init_method_doc_lines
            return

    # Append __init__ method docstring at the end of the class docstring
    # if the class docstring doesn't have any Interface sections.
    lines.extend(init_method_doc_lines)


def make_ref_node(app, env, node, contnode, modified_reftarget):
        # See sphinx.environment.BuildEnvironment.resolve_references():
        typ = node["reftype"]
        refdoc = node["refdoc"]
        domain = env.domains[node["refdomain"]]
        return domain.resolve_xref(
            env, refdoc, app.builder, typ, modified_reftarget, node, contnode)


def modify_init_method_reference(app, env, node, contnode):
    reftarget = node["reftarget"]

    if reftarget == "__init__":
        # Modify a reference from "__init__" to "ClassName".
        modified_reftarget = node["py:class"]
    elif reftarget.endswith(".__init__"):
        # Modify a reference from "ClassName.__init__" to "ClassName".
        modified_reftarget, __, __ = reftarget.rpartition(".__init__")
    else:
        return

    return make_ref_node(app, env, node, contnode, modified_reftarget)


def setup(app):
    app.connect("autodoc-process-docstring", insert_init_method_docstring)
    app.connect("missing-reference", modify_init_method_reference)
