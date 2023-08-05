"""

Setup script for elsa-client

To install, run:

python setup.py install

"""

from setuptools import setup, find_packages

setup(
        name='elsa-client',
        version='0.1.0',
        description='Service registration client for Cytoscape CI ELSA',
        long_description='Collection of tools for using Cytoscape and ',
        author='Keiichiro Ono',
        author_email='kono@ucsd.edu',
        url='https://github.com/idekerlab/py2cytoscape',
        license='MIT License',
        install_requires=[
            'requests'
        ],
        keywords=['cytoscape', 'bioinformatics', 'graph', 'network', 'microservice'],
        classifiers=[
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'License :: OSI Approved :: MIT License',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Mathematics',
        ],
        test_suite='tests',
        packages=find_packages(),
        include_package_data=True
)
