# coding: utf-8

from setuptools import setup, find_packages


try:
    readme_text = open('README.rst', 'r').read()
except IOError as e:
    readme_text = ''


setup(
    name='gsconfig-py3',
    version='1.0.1',
    description = "GeoServer REST Configuration",
    long_description = readme_text,
    url='https://github.com/dimitri-justeau/gsconfig-py3',
    author='Dimitri Justeau (IAC/AMAP)',
    author_email='dimitri.justeau@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['requests >= 2.4.3', ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS',
    ]
)
