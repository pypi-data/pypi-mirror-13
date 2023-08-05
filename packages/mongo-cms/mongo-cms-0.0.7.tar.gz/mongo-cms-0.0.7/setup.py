
import os, pip

# from pip.req import parse_requirements

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = pip.req.parse_requirements('requirements.txt', session=pip.download.PipSession())

requirements = [str(ir.req) for ir in install_reqs if ir is not None]

setup(name             = "mongo-cms",
      author           = "Aljosha Friemann",
      author_email     = "aljosha.friemann@gmail.com",
      license          = "",
      version          = "0.0.7",
      description      = "",
      url              = "https://bitbucket.org/afriemann/cdn",
      keywords         = [],
      # download_url     = "",
      install_requires = requirements,
      long_description = read('README.rst'),
      classifiers      = [],
      packages         = find_packages(),
      scripts          = ['scripts/cms']
)
