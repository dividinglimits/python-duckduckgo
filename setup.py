from setuptools import setup
from duckduckgo import __version__

with open('README.rst') as f:
    long_description = f.read()

setup(name='duckduckgo-async',
      version=__version__,
      py_modules=['duckduckgo'],
      description='Library for querying the DuckDuckGo API',
      author='Ammon Smith',
      author_email='ammon.i.smith@gmail.com',
      license='BSD',
      url='http://github.com/strinking/python-duckduckgo/',
      long_description=long_description,
      platforms=['any'],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
                   ],
      entry_points={'console_scripts': ['ddg = duckduckgo:main']},
      install_requires=['aiohttp', 'ratelimit']
)
