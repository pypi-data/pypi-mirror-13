from setuptools import setup, find_packages

setup(
    name='datastore.cloudfiles',
    version='0.0.1',
    packages=[p for p in find_packages() if p.startswith('datastore')],
    namespace_packages=['datastore'],
    install_requires=['datastore>=0.3', 'pyrax>=1.9'],
    test_suite='datastore.cloudfiles.test',
    keywords=[
          'datastore',
          'rackspace',
          'cloud files',
          'cloudfiles'
          'pyrax'
          'storage',
    ],
    classifiers=[
        'Environment :: OpenStack',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    description='Rackspace Cloud Files implementation of Datastore.',
    author='Ben Jeffrey',
    author_email='ben.jeffrey@boilerroom.tv',
    license='MPL 2.0',
    url='https://github.com/boilerroomtv/datastore.cloudfiles',
)
