from setuptools import setup, find_packages

setup(
    name='clap-api',
    version='0.10.1',
    author='Marek Marecki',
    author_email='marekjm@ozro.pw',
    url='https://github.com/marekjm/clap',
    license='GNU GPL v3',
    description='Command Line Arguments Parser',
    keywords='commandline arguments parser cli library',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
)
