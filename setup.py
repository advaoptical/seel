import os

from setuptools import find_packages, setup


setup(
    name='seel',
    description="the Send-Expect-Extract-Loop",

    author="ADVA Optical Networking :: Stefan Zimmermann",
    author_email="szimmermann@advaoptical.com",

    setup_requires=['setuptools_scm'],
    version_from_scm={
        'local_scheme': lambda _: '',
        'write_to': os.path.join('seel', '__version__.py'),
    },

    packages=find_packages('.', include=['seel', 'seel.*']),
)
