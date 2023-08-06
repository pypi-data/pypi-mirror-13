try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Chainson',
    version='0.1',
    packages=['chainson'],
    url='',
    license='Apache License 2.0',
    author='Shiqiao Du',
    author_email='lucidfrontier.45@gmail.com',
    description='Chainable JSON Encoder',
    install_requires=["six", "future"]
)
