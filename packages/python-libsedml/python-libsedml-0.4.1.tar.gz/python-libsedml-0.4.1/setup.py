## @file    setup.py
## @brief   Python distutils code for libSEDML Python module (including dependencies)
## @author  Michael Hucka
## @author  Ben Bornstein
## @author  Ben Kovitz
## @author  Frank Bergmann (fbergman@caltech.edu)
## 
##<!---------------------------------------------------------------------------

import glob
import os
import sys
import shutil
import platform
from distutils.sysconfig import get_config_vars

current_dir = os.path.dirname(os.path.realpath(__file__))

# remove -Wstrict-prototypes
(opt,) = get_config_vars('OPT')
if opt != None:
  os.environ['OPT'] = " ".join(
      flag for flag in opt.split() if flag != '-Wstrict-prototypes'
  )

# we need to switch the __init__.py file based on the python version
# as python 3 uses a different syntax for metaclasses
if sys.version_info >= (3,0):
  # this is python 3.x
  if (os.path.exists(current_dir + '/libsedml/__init__.py')):
    os.remove(current_dir + '/libsedml/__init__.py')
  shutil.copyfile(current_dir + '/script/libsedml3.py', current_dir + '/libsedml/__init__.py')
else:
  # this is an older python
  if (os.path.exists(current_dir + '/libsedml/__init__.py')):
    os.remove(current_dir + '/libsedml/__init__.py')
  shutil.copyfile(current_dir + '/script/libsedml2.py', current_dir + '/libsedml/__init__.py')

# figure out the os
#basepath = current_dir + '/base/'
basepath = './base/'
current_os = 'LINUX'
package_name = '"libsedml"'
inc_dirs = []
lib_dirs = []
libs = []
definitions = []
packages = [
  ('USE_COMP', None),
  ('USE_QUAL', None),
  ('USE_FBC', None),
  ('USE_LAYOUT', None)
]
if platform.system() == 'Darwin': 
  current_os = 'DARWIN'
elif platform.system() == 'Windows':
  current_os = 'WIN32'
  package_name = '\\"libsbml\\"'
  definitions = [
    ('LIBSEDML_EXPORTS', None),
    ('LIBNUML_STATIC', None),
    ('LIBSBML_STATIC', None),
    ('LIBLAX_STATIC', None)
  ]

definitions = definitions  + [
  ('BZIP2_STATIC', None),
  ('HAVE_MEMMOVE', None),
  ('_LIB', None)
  ]
  
  
cfiles = [ basepath + 'libsedml_wrap.cpp' ]

# add dependencies
cfiles = cfiles + glob.glob(basepath + "*.c");

for root, dirs, files in os.walk(basepath + 'sbml'):
  for file in files:
    if file.endswith('.c') or file.endswith('.cpp'):
      cfiles.append(os.path.join(root, file))

for root, dirs, files in os.walk(basepath + 'numl'):
  for file in files:
    if file.endswith('.c') or file.endswith('.cpp'):
      cfiles.append(os.path.join(root, file))
for root, dirs, files in os.walk(basepath + 'sedml'):
  for file in files:
    if file.endswith('.c') or file.endswith('.cpp'):
      cfiles.append(os.path.join(root, file))


from distutils.core import setup, Extension

setup(name             = "python-libsedml", 
      version          = "0.4.1",
      description      = "LibSEDML Python API",
      long_description = ("libSEDML is a library for reading, writing and "+
                          "manipulating SEDML.  It is written in ISO C and C++, supports "+
                          "SEDML Levels 1, Version 1-3, and runs on Linux, Microsoft "+
                          "Windows, and Apple MacOS X.  For more information "+
                          "about SEDML, please see http://sed-ml.org/."),
      license          = "LGPL",
      author           = "Frank T. Bergmann",
      author_email     = "fbergman@caltech.edu",
      url              = "https://github.com/fbergmann/libSEDML",
      packages         = ["libsedml"],
      package_dir      = {'libsedml': 'libsedml'},
      #data_files       = [('lib/site-packages', ['libsbml.pth'])],
      ext_package      = "libsedml",
      ext_modules      = [Extension("_libsedml", 
                            sources = cfiles,
                            define_macros =  definitions 
							  +  [(current_os, None), 
                              ('USE_EXPAT', None),
                              ('USE_ZLIB', None),
                              ('USE_BZ2', None)
                              ] 
							  + packages,
                            include_dirs = inc_dirs +
							  [                              
                              basepath + "/", 
                              basepath + "/sbml", 
                              basepath + "/sbml/compress", 
                              basepath + "/sbml/validator/constraints", 
                              basepath + "/sbml/packages/comp/validator", 
                              basepath + "/sbml/packages/comp/validator/constraints", 
                              "."],
                            libraries = libs,
                            library_dirs = lib_dirs
                            )
                         ]
)
