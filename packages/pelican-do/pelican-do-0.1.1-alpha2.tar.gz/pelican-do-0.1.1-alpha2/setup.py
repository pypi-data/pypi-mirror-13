try:
  from setuptools import setup, find_packages
except ImportError:
  from distutils.core import setup, find_packages


config = {
  'name': 'pelican-do',
  'version': '0.1.1-alpha2',
  'description': 'Commands to automate common pelican tasks',
  'long_description': open('README.rst').read(),
  'license': 'MIT',
  'author': 'Gustavo Ajzenman',
  'author_email': 'gustavoajz@gmail.com',
  'url': 'https://github.com/gusajz/pelican-do',
  'keywords': ['blog', 'pelican'],
  'install_requires': [
    'click==6.2',
    'Jinja2==2.8',
    'awesome-slugify==1.6.5',
  ],
  'extras_require': {
    'development': [
    ],
  },
  'setup_requires': [
    'pytest-runner',
  ],
  'tests_require': [
    'pytest>=2.6.4',
    'pytest-cov==2.2.0'
  ],
  'classifiers': [
    'Development Status :: 1 - Planning',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Utilities',
    'Programming Language :: Python :: 2.7',
  ],
  'packages': find_packages(),
  'scripts': [],
  'entry_points': {
    'console_scripts': ['pelican-do=pelican_do.main:main']
  }
}

setup(**config)
