from distutils.core import setup
import sys

requires = ["jsonasobj"]
if sys.version_info < (3, 5):
    requires.append("typing")

setup(
    name='PyShExJ',
    version='0.0.1',
    packages=[''],
    package_dir={'': 'src'},
    url='https://github.com/hsolbrig/PyShExJ',
    license='Apache License 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    install_requires = requires,
    test_requires = ["dirlistproc"],
    description='python bindings and parser for ShExJ'
)
