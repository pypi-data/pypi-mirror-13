import os
import sys
from setuptools import setup, find_packages
from pkg_resources import require, DistributionNotFound


def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

readme_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              'README.rst'))

try:
    long_description = open(readme_file).read()
except IOError as err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
                     "long_description (%s)\n" % readme_file)
    sys.exit(1)

extra_kwargs = {}
# extra_kwargs = {'tests_require': ['mock>1.0']}
# if sys.version_info < (2, 7):
#    extra_kwargs['tests_require'].append('unittest2')

contactbox = __import__('contactbox')

requirements = local_open('requirements.txt')
required_to_install = []
for dist in requirements.readlines():
    dist = dist.strip()
    try:
        require(dist)
    except DistributionNotFound:
        required_to_install.append(dist)

setup(
    name='contactbox',
    version=contactbox.get_version(),
    url='https://github.com/YD-Technology/contactbox',
    author='YD Technology',
    author_email='team@ydtechnology.com',
    description=contactbox.__doc__,
    long_description=long_description,
    zip_safe=False,
    install_requires=required_to_install,
    packages=find_packages(),
    license='MIT',
    scripts=[],
    test_suite='contactbox.test_runner.build_suite',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    **extra_kwargs
)
