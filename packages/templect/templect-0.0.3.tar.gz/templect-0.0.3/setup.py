
import os, pip, sys, glob

# from pip.req import parse_requirements

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if os.geteuid() != 0:
    prefix = os.path.expanduser('~/.local')
else:
    prefix = sys.prefix

datadir = os.path.join(prefix, 'share','templect')

def pkg_templates():
    yield datadir, []
    for root,dirs,files in os.walk('templates'):
        # if len(files) > 0:
        yield os.path.join(datadir, root), [ os.path.join(root, f) for f in files ]

datafiles = list(pkg_templates())

install_reqs = pip.req.parse_requirements('requirements.txt', session=pip.download.PipSession())
requirements = [str(ir.req) for ir in install_reqs if ir is not None]

setup(name             = "templect",
      author           = "Aljosha Friemann",
      author_email     = "aljosha.friemann@gmail.com",
      license          = "",
      version          = "0.0.3",
      description      = "",
      url              = "https://bitbucket.org/afriemann/templect",
      keywords         = [],
      # download_url     = "",
      install_requires = requirements,
      long_description = read('README.rst'),
      classifiers      = [],
      packages         = find_packages(),
      data_files       = pkg_templates(),
      scripts          = ['scripts/templect']
)
