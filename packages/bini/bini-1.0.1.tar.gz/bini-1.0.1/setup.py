from setuptools import setup

__version__ = "1.0.1"

setup(
    name='bini',
    version=__version__,
    description='(B)Ini-file manipulation in Python',
    author='Tobias Weise',
    author_email='tobias_weise@gmx.de',
    license = "BSD3",
    keywords= "bini ini configuration freelancer windows",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    py_modules=('bini',)
)

