from setuptools import setup, find_packages

version = '1.2'

setup(
    name='collective.maplocbehavior',
    version=version,
    description="Provides map location behavior for Dexterity content types",
    long_description=open("README.rst").read() + "\n" +
                   open("HISTORY.txt").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Framework :: Plone",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='Steve McMahon',
    author_email='steve@dcn.org',
    url='https://github.com/collective/collective.maplocbehavior',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.app.dexterity',
        'Products.Maps',
        'plone.formwidget.geolocation',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
