from setuptools import setup, find_packages

setup(
    name='oyster',
    version='0.0.5',
    author='Florian Brozek',
    author_email='florianbrozek@protonmail.ch',
    description='Nothing to see here. Move along.',
    scripts=['oyster/oyster.py'],
    zip_safe=False,
	packages=find_packages(),
    install_requires=[
        'click',
        'pycrypto',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.5'
    ],
)
