import os
from distutils.core import setup

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

setup(
    name='pyufc',
    version='0.2.1',
    author='Eric Hamiter',
    author_email='ehamiter@gmail.com',
    description='A Python wrapper for API access to the UFC fighter roster',
    long_description=long_description,
    url='https://github.com/ehamiter/pyufc',
    packages=['pyufc'],
    install_requires=[
        'beautifulsoup4==4.4.0',
        'requests==2.7.0'
    ],
    license='MIT',
    keywords=['ufc', 'mma', 'mixed martial arts', 'fighting', 'fighters'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
