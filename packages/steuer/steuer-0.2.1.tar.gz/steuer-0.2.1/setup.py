import os
import shutil
from distutils.core import setup
from os.path import expanduser

setup(
        name='steuer',
        version='0.2.1',
        license="GNU LGPLv3",
        description='A python module that do a mapping from pygame controller events to actions. Actions are also combined to Directions.',
        long_description=open("README.txt").read(),
        author='Thorsten Butschke',
        author_email='thorsten.butschke@googlemail.com',
        url='https://thornpw@bitbucket.org/thornpw/steuer',
        packages=['steuer'],
        package_dir={'steuer': 'src/steuer'},
        package_data={
            'steuer': [
                'data/*.json',
                'examples/*.*',
                'examples/moveblock_event/*.*',
                'examples/moveblock_poll/*.*',
                'examples/simple/*.*'
            ]
        },
        classifiers=[
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
        ]
)

_steuer_directory = os.path.join(expanduser("~"), ".steuer")
if not os.path.exists(_steuer_directory):
    os.mkdir(_steuer_directory)
    shutil.copy(os.path.join(os.getcwd(), "src","steuer","data", "steuer.json"), _steuer_directory)
