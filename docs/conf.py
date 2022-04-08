# -*- coding: utf-8 -*-
import derex.runner
import os
import sys


# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))


# -- General configuration ---------------------------------------------


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.viewcode", "autoapi.extension"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["html_templates"]
autoapi_type = "python"
autoapi_dirs = ["../derex/runner"]
autoapi_ignore = ["*settings/derex/*", "*compose_files/*"]
autoapi_python_class_content = "both"
autoapi_root = "derex_runner"


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "derex.runner"
copyright = "2020, Abstract-Technology GmbH"
author = "Abstract-Technology GmbH"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = derex.runner.__version__
# The full version, including alpha/beta/rc tags.
release = derex.runner.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "press"

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "external_links": [("Github", "https://github.com/Abstract-Tech/derex.runner")]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "assets/logo.svg"

html_css_files = [
    "css/custom.css",
]


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "derex.runnerdoc"


# -- Options for LaTeX output ------------------------------------------

# latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#
# 'papersize': 'letterpaper',
# The font size ('10pt', '11pt' or '12pt').
#
# 'pointsize': '10pt',
# Additional stuff for the LaTeX preamble.
#
# 'preamble': '',
# Latex figure (float) alignment
#
# 'figure_align': 'htbp',
# }

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "derex.runner.tex",
        "derex.runner Documentation",
        "Abstract-Technology GmbH",
        "manual",
    )
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "derex.runner", "derex.runner Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "derex.runner",
        "derex.runner Documentation",
        author,
        "derex.runner",
        "One line description of project.",
        "Miscellaneous",
    )
]

# Enable nitpicking
nitpicky = True
# Solve `class reference target not found: object`
# as advised on https://stackoverflow.com/a/30624034
nitpick_ignore = [
    ("py:class", "type"),
    ("py:class", "object"),
    # The following are needed to prevent errors like
    # WARNING: py:class reference target not found: Path
    # from showing up.
    # We don't fully understand how this works, but we'd like to keep
    # the warning-as-failures behaviour, so we "fix" them here.
    ("py:class", "RuntimeError"),
    ("py:class", "ValueError"),
    ("py:class", "enum.Enum"),
    ("py:class", "enum.IntEnum"),
    ("py:class", "logging.Formatter"),
    ("py:class", "Project"),
    ("py:class", "ProjectRunMode"),
    ("py:class", "click.core.Context"),
    ("py:class", "DerexSecrets"),
    ("py:class", "derex.runner.project.Project"),
    ("py:class", "derex.runner.constants.ProjectBuildTargets"),
    ("py:class", "Optional['derex.runner.project.Project']"),
    ("py:class", "Path"),
    ("py:class", "pathlib.Path"),
    ("py:class", "ProjectRunMode"),
    ("py:class", "pymysql.cursors.Cursor"),
    ("py:class", "string.Template"),
    ("py:meth", "str.format"),
    ("py:obj", "object"),
    ("py:obj", "enum.Enum"),
    ("py:obj", "enum.IntEnum"),
    ("py:obj", "RuntimeError"),
    ("py:obj", "ValueError"),
]
