from distutils.core import setup
from setuptools import find_packages
from glob import glob, iglob
import importlib
import os
import re
from shutil import copy
import sys
from subprocess import Popen, PIPE
import site

module_name = 'systemdunitextras'
data_dirname = "data"


def rsync(src, dst):
    src = os.path.normpath(src)
    p1 = Popen(["rsync", "-avHAXx", "--ignore-existing", src, dst], stdout=PIPE)
    print(p1.communicate())


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


setup(
    name=module_name,
    version="0.1.7",
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
    include_package_data=True,
)

# (2)
site_packages = site.getsitepackages()[0]

egg_path = None
for file in listdir_fullpath(site_packages):
    if re.search("{0}$".format(module_name), file):
        egg_path = file
        pip = True
        break
    elif re.search("{0}\-.*egg.*".format(module_name), file):  # (1)
        egg_path = file
        pip = False
if egg_path:
    if pip is True:
        data_path = os.path.normpath(os.path.join(egg_path, data_dirname))
        for file in glob("{0}/*".format(data_path)):
            relpath = os.path.relpath(file, data_path)
            print(file)
            print(relpath)
            rsync(file, "/")
    elif pip is False:
        data_path = os.path.normpath(os.path.join(egg_path, module_name, data_dirname))
        for file in glob("{0}/*".format(data_path)):
            relpath = os.path.relpath(file, data_path)
            rsync(file, "/")


# Code notes:
# (1) If package is installed with `python3 setup.py install`, then the package is within
#     site-packages/<package_name><version><egg>/<package_name>. If installed with pip
#     the package is in site-packages/<package_name>. If both directories exist, then latter
#     will be favoured.
# (2) Here we copy files inside <package>/data/* to system dirs, where data/ resemebles the root
# (3) Wrong approach:
#     site_packages = os.path.join("/usr/lib/", "python{0}.{1}".format(sys.version_info.major, sys.version_info.minor), "site-packages")
#     Better: >>> import site; site.getsitepackages()
# Notice:
# - Installation of system files is automatically, but uninstalling is not. You have to manually
#   look in <package>/data/* where files were installed on the system and delete them manually.
