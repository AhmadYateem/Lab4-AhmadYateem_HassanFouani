# Configuration file for the Sphinx documentation builder.

import os
import sys
from datetime import date

# Add project root to path so autodoc can import modules
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'School Managment Database'
author ='Hassan Ali Fouani'
copyright = f"{date.today().year}, {author}"
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# If your code imports PyQt5 (or other heavy libs), mock them to avoid import errors while building
autodoc_mock_imports = ['PyQt5']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Autodoc defaults: include __init__ doc, and private members if you want
autoclass_content = 'both'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
