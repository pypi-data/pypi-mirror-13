import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='netdrive-connector',
    version='1.3.2',
    license='BSD License',
    description='GUI tool to setup mountable SFTP and WebDAV connections on Linux/UNIX systems.',
    long_description=README,
    url='http://github.com/ethoms/netdrive-connector/',
    author='Euan Thoms',
    author_email='euan@potensol.com',
    classifiers=[
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
    ],
    keywords='connect remote network filesystem mount davfs webdav fuse sshfs sftp',
    packages=['netdriveconnector'],
    package_data={'netdriveconnector': ['*.ui']},
    include_package_data=True,
    data_files=[
        ('share/pixmaps',['data/netdrive-connector.png']),
        ('share/applications',['data/netdrive-connector.desktop']),
    ],
    scripts=['bin/netdrive-connector_run-as-root', 'bin/netdrive-connector_automountd', 'bin/add-sftp-connector', 'bin/add-webdav-connector', 'bin/remove-sftp-connector', 'bin/remove-webdav-connector'],
    entry_points={
        'console_scripts': [ 'netdrive-connector = netdriveconnector.main:main',],
    },
    options = {
        'build_scripts': {
            'executable': '/usr/bin/python2.7',
        },
    }, 
)
