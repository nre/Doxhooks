interface_titles = {
    "Exports",
    "Class Interface",
    "Subclass Interface",
    "Magic Methods",
}


def interface_preprocessor(app, what, name, obj, options, lines):
    # Extend NumPy style docstrings with Interface sections.
    new_lines = None
    numbered_lines = enumerate(lines)

    for line_no, line in numbered_lines:
        if line in interface_titles:
            __, next_line = next(numbered_lines)

            underline = "-" * len(line)
            if next_line != underline:
                # Don't worry about next_line being an interface title.
                if new_lines is not None:
                    new_lines.extend((line, next_line))
                continue

            if new_lines is None:
                new_lines = lines[:line_no]
            # Section break for Napoleon:
            new_lines.append("")
            # Field list:
            field_name = line.capitalize()
            new_lines.append(":{}:".format(field_name))

            list_item_count = 0
            while line:
                __, line = next(numbered_lines)
                if line and not line.startswith(" "):
                    list_item_count += 1
                    list_item_index = len(new_lines)

                    # Bullet list + interpreted text + em dash:
                    new_lines.append("  * `{}` --".format(line))
                else:
                    new_lines.append(line)

            if list_item_count == 1:
                item_line = new_lines[list_item_index]

                # Remove bullet if list is only one item:
                new_lines[list_item_index] = item_line.replace("*", " ", 1)

        elif new_lines is not None:
            new_lines.append(line)

    if new_lines is not None:
        lines[:] = new_lines


def setup(app):
    app.connect("autodoc-process-docstring", interface_preprocessor)
