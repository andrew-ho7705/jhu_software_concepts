import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("../../"))


MOCK_MODULES = [
    "psycopg",       
    "psycopg2",      
    "requests"       
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

# -- Project information -----------------------------------------------------
project = 'Module 4 Docs'
copyright = '2025, Andrew Ho'
author = 'Andrew Ho'

# -- General configuration ---------------------------------------------------
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
