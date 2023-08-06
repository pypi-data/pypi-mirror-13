from setuptools import setup, find_packages
from syscheck import __version__

description = 'Check the status of various systems'
long_description = open('README.rst', 'r').read()

with open('requirements.txt', 'r') as fp:
    requirements = fp.readlines()

setup(
    name='syscheck',
    version=__version__,
    author='Michael V. DePalatis',
    author_email='mike@depalatis.net',
    url='https://bitbucket.org/mivade/syscheck',
    description=description,
    long_description=long_description,
    license='BSD',
    packages=find_packages(),
    package_data={'syscheck': [
        'static/*.png',
        'static/css/*',
        'static/fonts/*',
        'static/js/*.js',
        'templates/*.html'
    ]},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Monitoring"
    ]
)
