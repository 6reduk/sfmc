from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='sfmc',
    version='0.1',
    description='Salesforce Marketing Cloud client for Python',
    long_description=readme,
    author='Dmitriy Shestakov',
    url='https://github.com/6reduk/sfmc',
    license='MIT',

    packages=['sfmc'],
    package_dir={'': 'src'},

    install_requires=[
        'pyjwt>=1.5.3',
        'requests>=2.18.4',
        'lxml==3.7.3',
        'suds-jurko==0.6',
    ],
    classifiers=[
        'Development Status :: Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.6',
    ]
)
