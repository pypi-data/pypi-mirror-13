from setuptools import setup

setup(
    name='convertkit',
    version='0.3',
    description='API Client for ConvertKit v3',
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    license='BSD',
    author='Justin Abrahms',
    author_email='justin@abrah.ms',
    url='https://github.com/justinabrahms/python-convertkit/',
    packages=['convertkit'],
    install_requires=[
        'requests >=1.0.0'
    ]
)
