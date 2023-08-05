import os.path

from setuptools import setup, find_packages


setup(
    name = 'gocept.form',
    version='0.8.0',
    author = "Christian Zagrodnick",
    author_email = "cz@gocept.com",
    description = "Extensions for zope.formlib",
    long_description = '\n\n'.join(
        open(os.path.join(os.path.dirname(__file__), name)).read()
        for name in ['README.txt', 'CHANGES.txt']),
    license = "ZPL 2.1",
    url='http://pypi.python.org/pypi/gocept.form',

    packages = find_packages('src'),
    package_dir = {'': 'src'},

    include_package_data = True,
    zip_safe = False,

    namespace_packages = ['gocept'],
    install_requires = [
        'setuptools',
        'gocept.mochikit>=1.3.1',
        'zope.interface',
        'zope.component',
        'zope.contentprovider',
        'zope.viewlet',
        'zc.resourcelibrary',
    ],
    extras_require = dict(
        test=[
              'zope.testbrowser',
              'zope.app.testing',
              'zope.app.zcmlfiles',
              'zope.viewlet!=3.4.1',
               'z3c.pagelet',
             ],
        formlib=[
            'zope.browserpage',
            'zope.formlib',
        ],
        z3cform=['z3c.form',
                 'z3c.pagelet'
                ])
    )
