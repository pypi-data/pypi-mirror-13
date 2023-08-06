
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
requires = ["dirlistproc", "jsonasobj"]
if sys.version_info < (3, 5):
    requires.append("typing")

setup(
    name='schema_to_context',
    version='0.2.0',
    packages=[''],
    url='http://github.com/crDDI/schema_to_context',
    license='BSD 3-Clause license',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='JSON Schema to JSON LD Extraction Utility',
    long_description='Extract tag names and types from JSON Schema for JSON LD',
    install_requires=requires,
    scripts=['scripts/schema_to_context'],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only']
)
