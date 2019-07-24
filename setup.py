try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup


def get_requirements():
    with open('requirements.txt') as fp:
        return [x.strip() for x in fp.read().split('\n')
                if not x.startswith('#')]

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
    'version': '0.0.2',
    'packages': ['tornado_dnslib'],
    'scripts': [],
    'name': 'tornado_dnslib',
    'install_requires': get_requirements(),
}

setup(**config)
