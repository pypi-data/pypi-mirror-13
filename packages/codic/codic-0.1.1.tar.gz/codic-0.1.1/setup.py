import setuptools

setuptools.setup(
    name='codic',
    version='0.1.1',
    description='Codic CLI',
    url='https://github.com/tuvistavie/codic-cli',

    author='Daniel Perez',
    author_email='tuvistavie@gmail.com',

    install_requires=[
        'requests'
    ],
    packages=['codic'],
    scripts=['bin/codic']
)
