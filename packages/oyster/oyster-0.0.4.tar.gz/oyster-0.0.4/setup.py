from setuptools import setup

setup(
    name='oyster',
    version='0.0.4',
    author='Florian Brozek',
    author_email='florianbrozek@protonmail.ch',
    description='Nothing to see here. Move along.',
    scripts=['oyster/oyster.py'],
    zip_safe=False,
    install_requires=[
        'click',
        'pycrypto',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.5'
    ],
)
