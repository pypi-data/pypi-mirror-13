from distutils.core import setup
from setuptools import find_packages
from glob import glob
import importlib
import os
import re
from shutil import copy

module_name = 'systemdunitextras'
data_files = [('/etc/systemd/system', glob('data/*'))]


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


setup(
    name=module_name,
    version="0.1.0",
    author="eayin2",
    author_email="eayin2 at gmail dot com",
    packages=find_packages(),
    description="Provides watchdog_ping python module and a systemd unit fail handler, allowing to limit \
                 a notification for an OnFailure event of a specific systemd unit to a specified time span.",
    entry_points={
        'console_scripts': [
            'systemd_fail_handler = systemdunitextras.fail_handler:argparse_entry',
        ],
    },
    install_requires=['gymail', 'sqlalchemy'],
    data_files=data_files
)

module = importlib.import_module(module_name)
print(module)
package_dir = module.__path__[0]
print(package_dir)
site_packages = os.path.dirname(package_dir)
print(site_packages)
#egg_path = [file for file in listdir_fullpath(site_packages) if re.search("{0}\-.*egg.*".format(module_name), file)]
egg_path = [file for file in listdir_fullpath('/usr/lib/python3.5/site-packages') if re.search("{0}\-.*egg.*".format(module_name), file)]
print(egg_path)
[copy(file, '/'.format(file.strip(site_packages))) for file in glob("{0}/*".format(egg_path[0]))]
