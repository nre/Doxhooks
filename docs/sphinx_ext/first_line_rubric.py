def first_line_rubric(app, what, name, obj, options, lines):
    if what == "module":
        lines.insert(0, ".. rubric::")
        lines[1] = "   " + lines[1]

def setup(app):
    app.connect("autodoc-process-docstring", first_line_rubric)
