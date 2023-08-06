from setuptools import setup, find_packages


setup(
    name='gocept.month',
    version='1.4',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/gocept.month',
    description="A datatype which stores a year and a month.",
    long_description=(
        open('COPYRIGHT.txt').read()
        + '\n\n'
        + open('README.rst').read()
        + '\n\n'
        + open('CHANGES.rst').read()),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages = ['gocept'],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
    ],
    extras_require=dict(
        form=[
            'z3c.form >= 2.6',
            'zope.formlib >= 4.0',
        ],
        test=[
            'zope.testing',
        ]),
)
