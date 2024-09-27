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

extensions.append("sphinx_wagtail_theme")

html_theme = 'sphinx_wagtail_theme'
html_theme_options = {
    'project_name': 'ADV 5.1 Posting Migration',
    'navigation_depth': 2,  # Controls the depth of the TOC in the sidebar
    'collapse_navigation': False,
    'sticky_navigation': True,
    'titles_only': True,  # Only show page titles (not sections)
    'body_max_width': '100%',

}
html_static_path = ['_static']

#7410