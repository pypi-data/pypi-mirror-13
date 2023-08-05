import os
import sys
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

if 'publish' in sys.argv:
    if 'test' in sys.argv:
        os.system('python setup.py sdist bdist_wheel upload -rtest')
    else:
        os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = ''


with open('LICENSE') as f:
    license = f.read()

setup(
    name='bench-it',
    version='0.2.4',
    description='Quick and easy python benchmarking.',
    url='http://github.com/scuml/benchit',
    packages=find_packages(where="src"),
    license=license,
    long_description=description,
    author='Stephen Mitchell',
    author_email='stephen@echodot.com',
    package_dir={"": "src"},
    package_data={'': ['LICENSE']},
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),
)
