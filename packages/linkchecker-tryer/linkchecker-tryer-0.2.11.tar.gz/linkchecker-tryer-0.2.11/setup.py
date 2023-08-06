
'''
Setup script.
To install lizard:
[sudo] python setup.py install
'''

from setuptools import setup, find_packages
import os

def install(appname):

    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fobj:
            readme = fobj.read()
    except IOError:
        readme = "helper for linkchecker"

    setup(
          name = appname,
          version = "0.2.11",
          description = '''A tool for retrying linkchecker''',
          long_description =  readme,
          url = 'https://github.com/terryyin/linkchecker-tryer',
          download_url='https://pypi.python.org/linkcheck-retryer/',
          license='MIT',
          platforms='any',
          classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'Intended Audience :: End Users/Desktop',
                     'License :: Freeware',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Quality Assurance',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.2',
                     'Programming Language :: Python :: 3.3'],
          py_modules = ['linkchecker_tryer'],
          author = 'Terry Yin',
          author_email = 'terry@odd-e.com',
          scripts = ['linkchecker-tryer']
          )

if __name__ == "__main__":
    import sys
    install('linkchecker-tryer')
