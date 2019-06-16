from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='sfmc',
    version='0.1.10',
    description='Salesforce Marketing Cloud client for Python',
    long_description=readme,
    author='Dmitriy Shestakov',
    author_email='6reduk@gmail.com',
    url='https://github.com/6reduk/sfmc',
    license='MIT',

    packages=find_packages('src', exclude=('tests',)),
    package_dir={'': 'src'},

    install_requires=[
        'pyjwt>=1.5.3',
        'requests>=2.18.4',
        'lxml==4.2.5',
        'suds-jurko==0.6',
    ],
    test_suite="tests",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.6',
    ]
)
