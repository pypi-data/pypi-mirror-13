from distutils.core import setup

setup(
    name='SimpG',
    version='0.1.1',
    author='Matthew S. Hamel',
    author_email='imnota9@gmail.com',
    packages=['simpg'],
    scripts=[],
    url='http://pypi.python.org/pypi/SimpG/',
    license='LICENSE.txt',
    description='A simple GUI library for quick GUI prototyping',
    long_description=open('README.txt').read(),
    install_requires="pygame",
)