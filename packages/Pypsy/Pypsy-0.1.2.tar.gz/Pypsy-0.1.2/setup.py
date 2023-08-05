from setuptools import setup, find_packages

setup(
    name='Pypsy',
    version='0.1.2',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'numpy',
        'scipy'
    ],
    url='http://www.musicsensorsemotion.com',
    license='MIT',
    author='Brennon Bortz',
    author_email='brennon@vt.edu',
    description='Electrodermal activity processing and analysis'
)
