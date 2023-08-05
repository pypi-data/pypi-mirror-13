from transmission.__version__ import SEMANTIC_VERSION as __version__
from setuptools import setup, find_packages


setup(
    author="hangarunderground",
    author_email="transmission@reelio.com",
    name="transmission",
    packages=find_packages(exclude=['transmission/tests/*']),
    version=__version__,
    url="https://github.com/hangarunderground/transmission",
    download_url=(
        "https://github.com/hangarunderground/transmission/"
        "tarball/" + __version__
    ),
    description=(
        "Transmission is a utility package that houses decorators and "
        "signals pertaining to state transitions and generalized events"
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=["django", "finite state machine", "rest", "signals"],
    install_requires=['django', 'djangorestframework'],
    extras_require={
        'dev': ['ipdb', 'mock', 'funcsigs', 'pylint', 'Fabric', 'tox'],
    }
)
