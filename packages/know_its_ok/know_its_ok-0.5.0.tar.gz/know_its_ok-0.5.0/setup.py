#!/usr/bin/env python

import distutils.core, re

with open('know_its_ok.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

distutils.core.setup(
        name='know_its_ok',
        version=version,
        author='Kale Kundert',
        author_email='kale@thekunderts.net',
        license='GPLv3',
        description="An easy way to debug your code.",
        long_description=readme,
        url='https://github.com/kalekundert/know_its_ok',
        download_url='https://github.com/kalekundert/know_its_ok/tarball/v'+version,
        keywords=[
            '2D',
            'vector',
            'rectangle',
            'library',
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
        py_modules=[
            'know_its_ok',
        ],
        install_requires=[
            'pytest',
            'pytest-cov',
        ],
        entry_points = {
            'console_scripts': ['ok=know_its_ok:main'],
        },

)
