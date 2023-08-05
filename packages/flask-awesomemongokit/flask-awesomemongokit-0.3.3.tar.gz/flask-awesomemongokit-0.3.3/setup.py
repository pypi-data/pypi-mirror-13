from setuptools import setup

setup(
    name='flask-awesomemongokit',
    version='0.3.3',
    packages=['flask_awesomemongokit'],
    url='https://github.com/angstwad/flask-awesomemongokit',
    license='Apache License v2.0',
    author='Paul Durivage',
    author_email='pauldurivage+github@gmail.com',
    description='Sets up an extremely opinionated MongoKit environment in '
                'Flask, based selfishly on my own needs.',
    install_requires=[
        'mongokit',
        'pymongo<3.0',
        'flask'
    ]
)
