try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup

from pip.req import parse_requirements
import pip.download

config = {
    'description': 'Tornado-based Asynchronous DNS client',

    'url': 'https://github.com/ContextLogic/tornado_dnslib',
    'author': 'Thomas Jackson',
    'author_email': 'tjackson@contextlogic.com',
    'license': 'MIT',
     'classifiers': [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    'version': '0.0.1',
    'packages': ['tornado_dnslib'],
    'scripts': [],
    'name': 'tornado_dnslib',
    # TODO: unify with requirements.txt
    'install_requires': [str(ir.req) for ir in parse_requirements('requirements.txt', session=pip.download.PipSession())],
}

setup(**config)
