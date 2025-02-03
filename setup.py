from setuptools import setup

setup(
    name='srpskiNLP',
    version='1.01',
    packages=['srpski'],
    install_requires=[
        'spacy',
        'setuptools',
        'requests'
    ],
    package_data={'srpski': ['sr.abbrev']},
    include_package_data=True,
    url='https://github.com/procesaur/srpski',
    license='GPL',
    author='Mihailo Škorić',
    author_email='procesaur@gmail.com',
    description='Serbian language NLP package'
)
