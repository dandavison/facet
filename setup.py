import os

from setuptools import find_packages
from setuptools import setup


setup(
    name='facet',
    version=(open(os.path.join(os.path.dirname(__file__),
                               'facet',
                               'version.txt'))
             .read().strip()),
    author='Dan Davison',
    author_email='dandavison7@gmail.com',
    description="A context switcher",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'facet = facet.cli:main',
        ],
    },
)
