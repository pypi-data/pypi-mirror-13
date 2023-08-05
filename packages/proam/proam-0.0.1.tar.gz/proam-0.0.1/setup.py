import distribute_setup
distribute_setup.use_setuptools()
from distutils.core import setup

setup(
    name='proam',
    version='0.0.1',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    package_data={'':['*']},

    scripts=[
        'bin/proam',
    ],
    url='http://pypi.python.org/pypi/proam/',
    license='LICENSE.txt',
    description='Process photos to send to ProAm (http://proamimaging.com).',
    install_requires=[
        "Pillow>=2.6.1",
        "click>=6.2",
    ],

)
