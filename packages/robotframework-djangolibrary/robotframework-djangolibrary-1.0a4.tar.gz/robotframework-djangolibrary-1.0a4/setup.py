from setuptools import setup, find_packages

version = '1.0a4'

setup(
    name='robotframework-djangolibrary',
    version=version,
    description="A robot framework library for Django.",
    long_description="""\
""",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='robotframework django test',
    author='Timo Stollenwerk',
    author_email='stollenwerk@kitconcept.com',
    url='http://kitconcept.com',
    license='',
    packages=find_packages(
        exclude=['ez_setup', 'examples', 'tests']
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django',
        'robotframework',
        'robotframework-selenium2library',
        'robotframework-debuglibrary',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
