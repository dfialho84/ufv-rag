# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'UFV-RAG'
copyright = '2025, Diego Fialho Rodrigues'
author = 'Diego Fialho Rodrigues'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',   # Extrai docstrings
    'sphinx.ext.viewcode',  # Adiciona links para o código-fonte
    'sphinx.ext.napoleon',  # Suporte a Google/NumPy docstrings
]


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Caminho para o projeto (ajuste conforme necessário)
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # Ajuste para o caminho do seu projet
