#!/usr/bin/env python

# Copyright (C) 2013 PolyBeacon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.

import os
import sys


sys.path.insert(0, os.path.abspath('../..'))

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'ripcord'
copyright = u'2013, Paul Belanger'
pygments_style = 'sphinx'
html_theme = 'default'
htmlhelp_basename = 'ripcordedoc'

latex_elements = {
}

latex_documents = [
    ('index', 'ripcord.tex', u'Ripcord Documentation',
     u'Paul Belanger', 'manual'),
]

man_pages = [
    ('man/ripcord-api', 'ripcord-api', u'Ripcord Documentation',
     [u'Paul Belanger'], 1),
    ('man/ripcord-manage', 'ripcord-manage', u'Ripcord Documentation',
     [u'Paul Belanger'], 1),
]

texinfo_documents = [
    ('index', 'ripcord', u'Ripcord Documentation',
     u'Paul Belanger', 'ripcord', 'One line description of project.',
     'Miscellaneous'),
]
