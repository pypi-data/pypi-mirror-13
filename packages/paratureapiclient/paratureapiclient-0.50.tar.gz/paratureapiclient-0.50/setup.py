from setuptools import setup


setup(
    name='paratureapiclient',
    version='0.50',
    description='Wrapper for working with the Parature RESTful API',
    url='https://github.com/joelcolucci/paratureapiclient',
    author='Joel Colucci',
    author_email='joelcolucci@gmail.com',
    license='MIT',
    packages=['paratureapiclient'],
    install_requires=[
        'requests'
    ],
    zip_safe=False
)
