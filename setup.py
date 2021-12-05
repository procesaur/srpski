from setuptools import setup

setup(
    name='srpskiNLP',
    version='1.00',
    packages=['srpski'],
    install_requires=[
        'spacy~=3.0.6',
        'setuptools~=49.2.1',
        'requests~=2.23.0',
        'nltk~=3.4.5'
    ],
    package_data={'srpski': ['sr.abbrev']},
    include_package_data=True,
    url='https://github.com/procesaur/srpski',
    license='GPL',
    author='Mihailo Škorić',
    author_email='procesaur@gmail.com',
    description='Serbian language NLP package'
)
