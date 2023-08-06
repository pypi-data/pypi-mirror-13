from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='sqlalchemy_teradata',
    version='0.0.2',
    description="Teradata dialect for SQLAlchemy",
    classifiers=[
                      'Development Status :: 3 - Alpha',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'Programming Language :: Python',
                      'Programming Language :: Python :: 3',
                      'Programming Language :: Python :: Implementation :: CPython',
                      'Topic :: Database :: Front-Ends',
                ],
    keywords='Teradata SQLAlchemy',
    author='Mark Sandan',
    author_email='mark.sandan@teradata.com',
    license='Commercial/Private',
    packages=['sqlalchemy_teradata'],
    include_package_data=True,
    tests_require=['pytest >= 2.5.2'],
    install_requires=['teradata'],
    entry_points={
                'sqlalchemy.dialects': [
                           'teradata = sqlalchemy_teradata.dialect:TeradataDialect',
                                           ]
                }
)
