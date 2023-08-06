#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
from setuptools import setup
import errno
import functools
import glob
import os
import os.path
import platform
import subprocess
import sys

from distutils.command.build_clib import build_clib as _build_clib
from distutils.command.build_ext import build_ext as _build_ext

from setuptools import Distribution


SODIUM_MAJOR = 7
SODIUM_MINOR = 3

requirements = ["six"]
setup_requirements = []

if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (2, 6):
        raise RuntimeError(
            "PyNaCl is not compatible with PyPy < 2.6. Please "
            "upgrade PyPy to use this library."
        )
else:
    requirements.append("cffi>=1.1.0")
    setup_requirements.append("cffi>=1.1.0")


def here(*paths):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *paths))

sodium = functools.partial(here, "src/libsodium/src/libsodium")


sys.path.insert(0, here("src"))


def which(name, flags=os.X_OK):  # Taken from twisted
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result


def use_system():
    install_type = os.environ.get("SODIUM_INSTALL")

    if install_type == "system":
        # If we are forcing system installs, don't compile the bundled one
        return True
    elif install_type == "bundled":
        # If we are forcing bundled installs, compile it
        return False

    # Detect if we have libsodium available
    import cffi

    ffi = cffi.FFI()
    ffi.cdef("""
        int sodium_library_version_major();
        int sodium_library_version_minor();
    """)

    try:
        system = ffi.dlopen("sodium")
    except OSError:
        # We couldn't locate libsodium so we'll use the bundled one
        return False

    if system.sodium_library_version_major() != SODIUM_MAJOR:
        return False

    if system.sodium_library_version_minor() < SODIUM_MINOR:
        return False

    # If we got this far then the system library should be good enough
    return True


class Distribution(Distribution):

    def has_c_libraries(self):
        return not use_system()


class build_clib(_build_clib):

    def get_source_files(self):
        files = glob.glob(here("src/libsodium/*"))
        files += glob.glob(here("src/libsodium/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*/*"))

        return files

    def build_libraries(self, libraries):
        raise Exception("build_libraries")

    def check_library_list(self, libraries):
        raise Exception("check_library_list")

    def get_library_names(self):
        return ["sodium"]

    def run(self):
        if use_system():
            return

        build_temp = os.path.abspath(self.build_temp)

        # Ensure our temporary build directory exists
        try:
            os.makedirs(build_temp)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Ensure all of our executanle files have their permission set
        for filename in [
                "src/libsodium/autogen.sh",
                "src/libsodium/compile",
                "src/libsodium/config.guess",
                "src/libsodium/config.sub",
                "src/libsodium/configure",
                "src/libsodium/depcomp",
                "src/libsodium/install-sh",
                "src/libsodium/missing",
                "src/libsodium/msvc-scripts/process.bat",
                "src/libsodium/test/default/wintest.bat"]:
            os.chmod(here(filename), 0o755)

        # Locate our configure script
        configure = here("src/libsodium/configure")

        # Run ./configure
        subprocess.check_call(
            [
                configure, "--disable-shared", "--enable-static",
                "--disable-debug", "--disable-dependency-tracking",
                "--with-pic", "--prefix", os.path.abspath(self.build_clib),
            ],
            cwd=build_temp,
        )

        # Build the library
        subprocess.check_call(["make"], cwd=build_temp)

        # Check the build library
        subprocess.check_call(["make", "check"], cwd=build_temp)

        # Install the built library
        subprocess.check_call(["make", "install"], cwd=build_temp)


class build_ext(_build_ext):

    def run(self):
        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command("build_clib")
            self.include_dirs.append(
                os.path.join(build_clib.build_clib, "include"),
            )
            self.library_dirs.append(
                os.path.join(build_clib.build_clib, "lib"),
            )

        return _build_ext.run(self)


def here(*paths):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *paths))

sys.path.insert(0, here("src"))

setup(
    name="aes256gcm-nacl",
    version="0.1.6",
    description="aes256gcm support based on pynacl",
    author="XueYu",
    author_email="278006819@qq.com",
    license="AGPLv3",
    setup_requires=setup_requirements,
    install_requires=requirements,
    extras_require={
        "tests": ["pytest"],
    },
    tests_require=["pytest"],
    package_dir={"": "src"},
    packages=[
        "zerodbext",
        "zerodbext.aead",
        "zerodbext.aead.bindings"
    ],
    namespace_packages=["zerodbext"],
    ext_package="zerodbext",
    cffi_modules=[
        "src/bindings/build.py:ffi",
    ],
    cmdclass={
        "build_clib": build_clib,
        "build_ext": build_ext,
    },
    distclass=Distribution,
    zip_safe=False,

    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ]
)
