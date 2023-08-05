from setuptools import setup, find_packages

long_description = """
This package contains a Sphinx / ablog theme, that inherits and works off alabaster
"""

setup(
    name='tibas.tt',
    author='gabriel montangé láscaris-comneno',
    author_email='gabriel@tibas.london',
    include_package_data = True,
    install_requires=[ 'ablog', 'sphinxcontrib-blockdiag' ],
    license='MIT',
    long_description=long_description,
    namespace_packages = [ 'tibas' ],
    packages=find_packages(),
    platforms=['any'],
    description='A Sphinx/ablog theme that inherits and works off alabaster',
    url='http://bitbucket.org/gabriel.montagne/tibas.tt',
    version='0.3.1',
)
