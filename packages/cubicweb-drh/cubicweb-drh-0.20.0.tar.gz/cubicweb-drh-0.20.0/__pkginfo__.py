# pylint: disable-msg=W0622
"""cubicweb-drh packaging information"""

modname = 'drh'
distname = "cubicweb-drh"

numversion = (0, 20, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = "Logilab"
author_email = "contact@logilab.fr"
description = "recruitment application based on the CubicWeb framework"
web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'cubicweb': '>= 3.21.0',
               'cubicweb-addressbook': None,
               'cubicweb-comment': None,
               'cubicweb-email': '>= 1.12.0',
               'cubicweb-event': None,
               'cubicweb-file': None,
               'cubicweb-folder': None,
               'cubicweb-geocoding': None,
               'cubicweb-jsonld': None,
               'cubicweb-person': None,
               'cubicweb-rqlcontroller': None,
               'cubicweb-signedrequest': None,
               'cubicweb-squareui': None,
               'cubicweb-tag': None,
               'cubicweb-task': None,
               }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration', 'wdoc'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
