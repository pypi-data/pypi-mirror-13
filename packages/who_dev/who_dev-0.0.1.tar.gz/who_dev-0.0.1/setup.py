import os
from setuptools import setup, find_packages
from subprocess import Popen, PIPE
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGELOG = open(os.path.join(HERE, 'CHANGES.rst')).read()


REQUIRES = [
    'repoze.who>=2.0',
]


EXTRAS = {
    'test': ['pytest', 'pytest-cov']
}


def get_version():
    version_file = os.path.join(HERE, 'VERSION')

    # read fallback file
    try:
        with open(version_file, 'r+') as fp:
            version_txt = fp.read().strip()
    except:
        version_txt = None

    # read git version (if available)
    try:
        version_git = (
            Popen(['git', 'describe'], stdout=PIPE, stderr=PIPE, cwd=HERE)
            .communicate()[0]
            .strip()
            .decode(sys.getdefaultencoding()))
    except:
        version_git = None

    version = version_git or version_txt or '0.0.0'

    # update fallback file if necessary
    if version != version_txt:
        with open(version_file, 'w') as fp:
            fp.write(version)

    return version


setup(
    name='who_dev',
    version=get_version(),
    description='A developer-mode plugin for repoze.who',
    long_description='\n\n'.join([README, CHANGELOG]),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
    keywords='web application server wsgi repoze repoze.who',
    url='https://github.com/m-martinez/who_dev',
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    tests_require=EXTRAS['test'],
)
