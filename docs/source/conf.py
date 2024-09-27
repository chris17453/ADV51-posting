# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TAS Posting'
copyright = '2024, Chris Watkins'
author = 'Chris Watkins'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

extensions = ['myst_parser']
source_suffix = ['.rst', '.md']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'navigation_depth': 1,  # Controls the depth of the TOC in the sidebar
    'collapse_navigation': False,
    'sticky_navigation': True,
    'titles_only': True,  # Only show page titles (not sections)
}
html_static_path = ['_static']

#7410