
from setuptools import setup

version = open('config/VERSION').read().strip()
requirements = open('config/requirements.txt').read().split("\n")

setup(
    name='twentyc.database',
    version=version,
    author='Twentieth Century',
    author_email='code@20c.com',
    description='database abstractions',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
      'twentyc.database',
      'twentyc.database.couchdb',
      'twentyc.database.dummydb',
      'twentyc.database.couchbase'
    ],
    url = 'https://github.com/20c/twentyc.database',
    download_url = 'https://github.com/20c/twentyc.database/tarball/%s'%version,
    install_requires=requirements,
    namespace_packages=['twentyc'],
    zip_safe=False
)
