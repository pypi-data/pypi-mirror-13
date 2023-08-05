import os.path
from setuptools import setup
from brush import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="brush",
    version=__version__,
    author="Michael V. DePalatis",
    author_email="depalatis@phys.au.dk",
    description="Monitor and log data from Menlo Systems optical frequency combs",
    long_description=read('README.rst'),
    license="MIT",
    keywords="physics science optical data acquisition",
    url="https://bitbucket.org/iontrapgroup/brush",
    packages=['brush'],
    package_data={
        'brush': [
            'static/css/*',
            'static/fonts/*',
            'static/img/*',
            'static/js/brush.js',
            'static/js/react-bundle.js'
        ]
    },
    entry_points={
        'console_scripts': ['brush=brush.cli:main']
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License'
    ]
)
