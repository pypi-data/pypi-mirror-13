from setuptools import setup

__version__ = "0.0.3"

setup(
    name = 'pylude',
    version = __version__,
    description = "A library trying to clone the Haskell-Prelude for python3",
    long_description = "A library trying to clone the Haskell-Prelude for python3",
    author = 'Tobias Weise',
    author_email = 'tobias_weise@gmx.de',
    license = "BSD3",
    keywords = "prelude haskell function functional lambda list tuple either maybe functor monad monoid higherorder",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.0',
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ],
    py_modules=('pylude', 'pylude.data', 'pylude.system', 'pylude.control', 'pylude.text')
)








