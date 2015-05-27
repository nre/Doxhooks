def print_lines(app, what, name, obj, options, lines):
    # Hint: Add a condition like 'if name ==', etc.
    for line in lines:
        print(line)


def setup(app):
    app.connect("autodoc-process-docstring", print_lines)
