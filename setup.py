#!/usr/bin/env python3
import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
import os
import urllib
import shutil


JDK_dst = './up_enhsp/openjdk'
JDK_FOLDER = './jdk-17.0.1'
OPENJDK_TAR_GZ = './openjdk.tar.gz'
ENHSP_dst = './up_enhsp/ENHSP'
ENHSP_PUBLIC = 'ENHSP-Public'
COMPILE_CMD = './compile'
ENHSP_TAG = 'enhsp20-0.9.2'
ENHSP_REPO = 'https://gitlab.com/enricos83/ENHSP-Public'
OPENJDK_URL = 'https://download.java.net/java/GA/jdk17.0.1/2a2082e5a09d4267845be086888add4f/12/GPL/openjdk-17.0.1_linux-x64_bin.tar.gz'

long_description = \
    """============================================================
    UP_ENHSP
 ============================================================
"""


def install_ENHSP():
    with urllib.request.urlopen(OPENJDK_URL) as response, open(OPENJDK_TAR_GZ, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    shutil.unpack_archive(OPENJDK_TAR_GZ, format='gztar')
    shutil.move(JDK_FOLDER, JDK_dst)
    os.remove(OPENJDK_TAR_GZ)
    subprocess.run(['git', 'clone', '-b', ENHSP_TAG, ENHSP_REPO])
    shutil.move(ENHSP_PUBLIC, ENHSP_dst)
    curr_dir = os.getcwd()
    os.chdir(ENHSP_dst)
    compile_cmd = open('./compile', 'r').read().replace('javac -d', '../openjdk/bin/javac -d').replace('jar --create', '../openjdk/bin/jar --create')
    open('./compile', 'w').write(compile_cmd)
    subprocess.run(COMPILE_CMD)
    os.chdir(curr_dir)


class InstallENHSP(build_py):
    """Custom install command."""

    def run(self):
        install_ENHSP()
        build_py.run(self)


class InstallENHSPdevelop(develop):
    """Custom install command."""

    def run(self):
        install_ENHSP()
        develop.run(self)


setup(name='up_enhsp',
      version='0.0.1',
      description='up_enhsp',
      author='Luigi Bonassi',
      author_email='l.bonassi005@unibs.it',
      packages=['up_enhsp'],
      package_data={
          "": ["ENHSP/enhsp-dist/*", "ENHSP/enhsp-dist/libs/*", "openjdk/*", "openjdk/*/*", "openjdk/*/*/*", "openjdk/*/*/*/*", "openjdk/*/*/*/*", "openjdk/*/*/*/*/*"],
      },
      cmdclass={
          'build_py': InstallENHSP,
          'develop': InstallENHSPdevelop,
      },
      license='APACHE')
