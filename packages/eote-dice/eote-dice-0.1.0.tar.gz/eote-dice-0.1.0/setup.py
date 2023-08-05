from setuptools import setup

import eote_dice


setup(
    name='eote-dice',
    version=eote_dice.__version__,

    description='Utility for analyzing EotE dice rolls.',
    long_description=open('README.rst').read(),
    keywords='star wars EotE dice role-playing',

    author='John Hagen',
    author_email='johnthagen@gmail.com',
    url='https://github.com/johnthagen/eote-dice',
    license='MIT',

    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment :: Role-Playing',
    ],

    scripts=['eote_dice.py'],

    entry_points={
        'console_scripts': [
            'eote_dice = eote_dice:main',
        ],
    }
)
