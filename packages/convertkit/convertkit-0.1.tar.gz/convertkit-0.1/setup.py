from setuptools import setup

setup(
    name='convertkit',
    version='0.1',
    description='API Client for ConvertKit v3',
    author='Justin Abrahms',
    author_email='justin@abrah.ms',
    url='https://github.com/justinabrahms/python-convertkit/',
    packages=['convertkit'],
    install_requires=[
        'requests >=1.0.0'
    ]
)
