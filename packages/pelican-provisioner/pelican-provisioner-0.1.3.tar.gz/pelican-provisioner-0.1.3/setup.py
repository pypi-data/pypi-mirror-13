# -*- coding: utf-8 -*-
# pelican-provisioner (c) Ian Dennis Miller

from setuptools import setup
from distutils.dir_util import copy_tree
import os
import re


# from https://github.com/flask-admin/flask-admin/blob/master/setup.py
def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


file_text = read(fpath('pelican_provisioner/__meta__.py'))


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


setup(
    version=grep('__version__'),
    name='pelican-provisioner',
    description="A system for provisioning blogs managed by Pelican.",
    packages=[
        "pelican_provisioner",
    ],
    scripts=[
        "bin/new-blog.sh",
    ],
    long_description=read('Readme.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
    ],
    include_package_data=True,
    keywords='',
    author=grep('__author__'),
    author_email=grep('__email__'),
    url=grep('__url__'),
    install_requires=read('requirements.txt'),
    license='MIT',
    zip_safe=False,
)

venv_path = os.environ.get("VIRTUAL_ENV")
if venv_path:
    copy_tree("skel", os.path.join(venv_path, "share/skel"))
    copy_tree("share/wheelhouse", os.path.join(venv_path, "share/wheelhouse"))
    copy_tree("share/pelican-plugins", os.path.join(venv_path, "share/pelican-plugins"))
else:
    print("This was not installed in a virtual environment")
    print("So, I won't install the skel files.")
