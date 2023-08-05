# This file was auto-generated by zetup
#
# https://bitbucket.org/userzimmermann/zetup.py


from __future__ import absolute_import

import sys
import os
from collections import OrderedDict

from zetup.version import Version
from zetup.dist import Distribution
from zetup.requires import Requirements
from zetup.extras import Extras
from zetup.package import Packages, Package
from zetup.notebook import Notebook



zfg = sys.modules[__name__]

NAME = 'zetup'

LICENSE = 'LGPLv3'

VERSION = Version('0.2.29')

EXTRAS = Extras([
('commands', Requirements("""
path.py >= 8.0 #import path
jinjatools >= 0.1.6

""")),
('notebook', Requirements("""
path.py >= 8.0 #import path
ipython >= 4.0 #import IPython
nbconvert >= 4.0

""")),
('pytest', Requirements("""
pytest

"""))
], zfg=zfg)

SETUP_HOOKS = []

PACKAGES = Packages([

Package('zetup',
  sources=[
    'annotate.py',
    'conda.py',
    'config.py',
    'dist.py',
    'error.py',
    'extras.py',
    'modules.py',
    'object.py',
    'package.py',
    'requires.py',
    'script.py',
    'version.py',
    'zetup.py',
    '__init__.py'
    ],
  subpackages=[
    
Package('zetup.commands',
  sources=[
    'command.py',
    'conda.py',
    'del_.py',
    'dev.py',
    'error.py',
    'pytest.py',
    'run.py',
    'test.py',
    'tox.py',
    '__init__.py'
    ],
  subpackages=[
    
Package('zetup.commands.make',
  sources=[
    '__init__.py'
    ],
  subpackages=[
    
    ],
  )

    ],
  )
,
    
Package('zetup.notebook',
  sources=[
    'jinja.py',
    '__init__.py'
    ],
  subpackages=[
    
    ],
  )
,
    
Package('zetup.process',
  sources=[
    'scons.py',
    '__init__.py'
    ],
  subpackages=[
    
    ],
  )

    ],
  )

  ], root=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

MODULES = []

KEEP_MADE = []

SETUP_REQUIRES = None

CLASSIFIERS = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', 'Operating System :: OS Independent', 'Topic :: Software Development', 'Topic :: Utilities', 'Programming Language :: Python', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5']

FORCE_MAKE = True

SCRIPTS = {'zetup': 'zetup.script:run'}

DESCRIPTION = "Zimmermann's Python package setup"

AUTHOR = 'Stefan Zimmermann'

NO_MAKE = ['setup.py', 'tox.ini']

EMAIL = 'zimmermann.code@gmail.com'

DISTRIBUTION = Distribution(zfg)

PYTHON = ['2.7', '3.3', '3.4', '3.5']

URL = 'https://bitbucket.org/userzimmermann/zetup.py'

SETUP_KEYWORDS = {'use_zetup': 'zetup:setup_entry_point'}

TITLE = 'zetup'

REQUIRES = Requirements("""
setuptools # >= 15.0
setuptools_scm

""", zfg=zfg)

KEYWORDS = ['setup', 'python3']

TEST_COMMANDS = ['py.test -v test']