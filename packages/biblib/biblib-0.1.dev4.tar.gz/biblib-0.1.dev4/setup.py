import os
from setuptools import setup
from biblib import __version__


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'biblib',
    version = __version__,
    author = 'Frank Roemer',
    author_email = 'froemer76@googlemail.com',
    description = ("A library to handle BibTeX bibliographic data."),
    license = "MIT",
    keywords = "BibTeX ISBN DOI citation",
    url = "http://pythonhosted.org/biblib",
    packages=['biblib',
              'biblib/dev'
              ],
    package_data={'': ['README', 'LICENSE']},
    include_package_data=True,
    long_description=read('README'),
    install_requires=["isbnlib>=3.5.6",
                      "python-magic>=0.4.10"],
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only'
    ]
)
