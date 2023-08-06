from setuptools import setup

__version__ = "0.0.1"

setup(
    name = 'pylude',
    version = __version__,
    description = "A library trying to clone the Haskell-Prelude for python3",
    long_description = "A library trying to clone the Haskell-Prelude for python3",
    author = 'Tobias Weise',
    author_email = 'tobias_weise@gmx.de',
    license = "BSD3",
    keywords = "prelude haskell function functional lambda list tuple higherorder",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ],
    py_modules=('pylude','pylude.data')
)

