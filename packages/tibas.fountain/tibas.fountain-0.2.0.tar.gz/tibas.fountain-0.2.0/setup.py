from setuptools import setup, find_packages

long_description = """
Sphinx extension and directive for embeding Fountain marked screenplay fragments.

Works for HTML representations. 
Designed to work with ablog
"""

setup(
    name='tibas.fountain',
    author='gabriel montangé láscaris-comneno',
    author_email='gabriel@tibas.london',
    description='Sphinx extension for embeding Fountain screenplay fragments',
    install_requires = [ 'fountain' ],
    license='MIT',
    long_description=long_description,
    namespace_packages = [ 'tibas' ],
    packages=find_packages(),
    platforms=[ 'any' ],
    url='http://bitbucket.org/gabriel.montagne/tibas.fountain',
    version='0.2.0',
)
