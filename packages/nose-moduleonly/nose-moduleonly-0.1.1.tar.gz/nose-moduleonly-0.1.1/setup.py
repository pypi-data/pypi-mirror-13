
from setuptools import setup, find_packages

setup(
    name='nose-moduleonly',
    version='0.1.1',
    description="",
    long_description="""""",
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    license="BSD",
    packages=find_packages(exclude=['ez_setup']),
    install_requires=['Nose'],
    url='https://github.com/craigds/nose-moduleonly',
    include_package_data=True,
    entry_points = {
        'nose.plugins.0.10': [
            'moduleonly = moduleonly.plugin:ModuleOnly',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing'
        ],
    )
