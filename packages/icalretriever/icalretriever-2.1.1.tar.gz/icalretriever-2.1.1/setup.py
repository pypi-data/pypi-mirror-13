from distutils.core import setup
import subprocess

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3 :: Only
Topic :: Office/Business :: Scheduling
Operating System :: Unix
"""

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='icalretriever',
    description='Periodically retrieve ICS files in order to serve them with CalDAV.',
    long_description=long_description,
    version='2.1.1',

    install_requires=('icalendar>=3.6,<4','pyyaml>3,<4'),

    url='https://git.microjoe.org/MicroJoe/icalretriever',

    author='Romain Porte (MicroJoe)',
    author_email='microjoe@mailoo.org',

    packages=('icalretriever',),

    classifiers=list(filter(None, classifiers.split('\n'))),

    scripts=('icalretriever-retrieve.py',)
)
