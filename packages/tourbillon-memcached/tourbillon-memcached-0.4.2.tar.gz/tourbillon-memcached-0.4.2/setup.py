import sys
from setuptools import setup, find_packages


PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

exclude = ['tourbillon.memcached.memcached2'
           if PY34_PLUS else 'tourbillon.memcached.memcached']

setup(
    name='tourbillon-memcached',
    description='A tourbillon plugin for collecting metrics from memcached.',
    version='0.4.2',
    packages=find_packages(exclude=exclude),
    zip_safe=False,
    namespace_packages=['tourbillon'],
    author='The Tourbillon Team',
    author_email='tourbillonpy@gmail.com',
    url='https://github.com/tourbillonpy/tourbillon-memcached',
    license='ASF',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Monitoring',
    ],
    keywords='monitoring metrics agent influxdb memcached',
)
