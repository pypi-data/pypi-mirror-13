from distutils.core import setup
from setuptools import find_packages
from glob import glob, iglob
import importlib
import os
import re
from shutil import copy
import sys
from subprocess import Popen, PIPE

module_name = 'systemdunitextras'
data_dirname = "data"


def rsync(src, dst):
    src = os.path.normpath(src)
    p1 = Popen(["rsync", "-avHAXx", src, dst], stdout=PIPE)
    print(p1.communicate())


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


setup(
    name=module_name,
    version="0.1.3",
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
    include_package_data = True,
)

module = importlib.import_module(module_name)
print(module)
package_dir = module.__path__[0]
print(package_dir)
site_packages = os.path.join("/usr/lib/", "python{0}.{1}".format(sys.version_info.major, sys.version_info.minor), "site-packages")
print(site_packages)
egg_path = [file for file in listdir_fullpath(site_packages) if re.search("{0}|{0}\-.*egg.*".format(module_name), file)]
print(egg_path)
# rsync
if egg_path:
    [rsync(file, '/'.format(file.strip(os.path.join(site_packages, module_name, data_dirname)))) for file in glob("{0}/{1}/{2}/*".format(egg_path[0], module_name, data_dirname))]
