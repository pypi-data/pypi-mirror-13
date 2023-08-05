#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil 
import os
from setuptools import setup, find_packages

import FSDNOEL
 
setup(
    name='FSDNOEL',
    version=FSDNOEL.__version__,
    packages=find_packages(),
    author="FredThx",
    author_email="FredThx@gmail.com",
    description="Un sapin de noel qui clignotte",
    long_description=open('README.md').read(),
    install_requires=[], #TODO
    include_package_data=True,
    url='',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
    ],
    # entry_points = {
        # 'console_scripts': [
            # 'proclame-sm = sm_lib.core:proclamer',
        # ],
    # },
    license="WTFPL",
)
try:
	os.mkdir('/opt/FSDNOEL')
except OSError:
	pass
shutil.copy('monbosapin.py', '/opt/FSDNOEL')

shutil.copy('monbosapin', '/etc/init.d')
shutil.copy('monbosapin.sh', '/usr/bin')
os.system('sudo chmod +x /etc/init.d/monbosapin')
os.system('sudo chmod +x /usr/bin/monbosapin.sh')
os.system('sudo update-rc.d monbosapin defaults 99')
