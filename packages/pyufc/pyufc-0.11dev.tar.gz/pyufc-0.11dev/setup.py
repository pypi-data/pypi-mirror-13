from distutils.core import setup

setup(
    name='pyufc',
    version='0.11dev',
    author='Eric Hamiter',
    author_email='ehamiter@gmail.com',
    description='A Python wrapper for API access to the UFC fighter roster',
    url='https://github.com/ehamiter/pyufc',
    packages=['pyufc'],
    install_requires=[
        'beautifulsoup4==4.4.0',
        'requests==2.7.0'
    ],
    license='MIT',
    keywords=['ufc', 'mma', 'mixed martial arts', 'fighting', 'fighters'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'pyufc': 'pyufc'}
)
