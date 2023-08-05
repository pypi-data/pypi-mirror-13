from setuptools import setup, find_packages
import os

package_root = os.path.dirname(__file__)

about = {}
with open("valigator/__about__.py") as fp:
    exec(fp.read(), about)

# Error-handling here is to allow package to be built w/o README.rst included
try:
    long_description = open(os.path.join(package_root, 'README.rst')).read()
except IOError:
    long_description = ''

setup(
    name=about["__title__"],
    version=about["__version__"],

    description=about["__summary__"],
    long_description=long_description,

    url=about["__uri__"],

    author=about["__author__"],
    author_email=about["__email__"],

    license=about["__license__"],

    classifiers=[
        'Intended Audience :: System Administrators',
        'Topic :: System :: Archiving :: Backup',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='database backup docker',

    packages=find_packages(exclude=['contrib', 'docs']),

    install_requires=['bottle', 'PyYAML', 'docker-py', 'click'],

    data_files=[('/etc/valigator', ['valigator.yml'])],

    entry_points={
        'console_scripts': [
            'valigator=valigator.valigator:main'
        ],
    },
)
