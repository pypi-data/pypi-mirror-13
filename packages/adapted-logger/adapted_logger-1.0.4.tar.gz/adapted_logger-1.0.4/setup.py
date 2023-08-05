__author__ = 'ismailkaboubi'
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
    import os
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

requires = [
        ]

scripts = [
    'logger/adapted_logger.py',
    'logger/custom_adapter.py',
    'logger/config/config.yml'
]

setup(
    name='adapted_logger',
    version='1.0.4',
    description='adapted_logger is a lib based on Python logging module, permetting injection of new data on logs'
                'and redirection to different target',

    author='ismailkaboubi',
    author_email='ikaboubi@gmail.com',
    url='',
    install_requires=requires,
    dependency_links=[
    ],
    #setup_requires=["PasteScript>=1.7.5"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    classifiers=[
                    # How mature is this project? Common values are
                    #   3 - Alpha
                    #   4 - Beta
                    #   5 - Production/Stable
                    'Development Status :: 3 - Alpha',

                    # Indicate who your project is intended for
                    'Intended Audience :: Developers',
                    'Topic :: Software Development :: Build Tools',

                    # Pick your license as you wish (should match "license" above)
                     'License :: OSI Approved :: MIT License',

                    # Specify the Python versions you support here. In particular, ensure
                    # that you indicate whether you support Python 2, Python 3 or both.
                    'Programming Language :: Python :: 2',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
                ],
    keywords='logging python filters python',
    package_data={'': ['*.xml', '*.sh', '*.yml']},
    scripts=scripts,
    entry_points="""
    """,
    zip_safe=False,
    message_extractors={},



)
