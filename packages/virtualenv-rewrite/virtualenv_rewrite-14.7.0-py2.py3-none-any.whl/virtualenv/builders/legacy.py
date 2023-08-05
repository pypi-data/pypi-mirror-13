from __future__ import absolute_import, division, print_function

import io
import logging
import os.path
import sys
import pprint

from virtualenv.builders.base import BaseBuilder
from virtualenv._utils import copyfile
from virtualenv._utils import ensure_directory

SITE = b"""# -*- encoding: utf-8 -*-
import os
import os.path
import sys
try:
    # Workaround for pypy losing it's builtin _struct module. The bundled
    # _struct.py is horribly broken, see:
    # https://bitbucket.org/pypy/pypy/issue/1959/zipimport-issue-unorderable-types-str-int
    import _struct
except ImportError:
    pass
try:
    # Workaround for pypy having a `builtin` symbol module. Don't laugh, it's not funny!
    import symbol
except ImportError:
    pass

# We want to stash the global site-packages here, this will be None if we're
# not adding them.
global_site_packages = __GLOBAL_SITE_PACKAGES__

# We want to make sure that our sys.prefix and sys.exec_prefix match the
# locations in our virtual enviornment.
# Note that case normalization is done here instead of the host interpreter
# to avoid differences - if any.
sys.prefix = os.path.normcase(__PREFIX__)
sys.exec_prefix = os.path.normcase(__EXEC_PREFIX__)

# We want to record what the "real/base" prefix is of the virtual environment.
# We store the variants `real_` prefix for compatibility with code that detects
# virtualenvs that way. Eg: Debian patches, pip, wheel etc ...
sys.real_prefix = sys.base_prefix = os.path.normcase(__BASE_PREFIX__)
sys.real_exec_prefix = sys.base_exec_prefix = os.path.normcase(__BASE_EXEC_PREFIX__)

# This is used in the creation phase when pip is installed in the virtualenv.
# We don't want those damn egg tripping up our PYTHONPATH whl loading, so we
# instruct setuptools to add the eggs at the end of sys.path (or whatever position
# VIRTUALENV_BOOTSTRAP_ADJUST_EGGINSERT specifies)
if "VIRTUALENV_BOOTSTRAP_ADJUST_EGGINSERT" in os.environ:
    sys.__egginsert = int(os.environ["VIRTUALENV_BOOTSTRAP_ADJUST_EGGINSERT"])

# At the point this code is running, the only paths on the sys.path are the
# paths that the interpreter adds itself. These are essentially the locations
# it looks for the various stdlib modules. Since we are inside of a virtual
# environment these will all be relative to the sys.prefix and sys.exec_prefix,
# however we want to change these to be relative to sys.base_prefix and
# sys.base_exec_prefix instead.
new_sys_path = []
for path in sys.path:
    # TODO: Is there a better way to determine this?
    path = os.path.normcase(os.path.realpath(os.path.abspath(path)))
    if path.startswith(sys.prefix):
        path = os.path.join(
            sys.base_prefix,
            path[len(sys.prefix):].lstrip(os.path.sep),
        )
    elif path.startswith(sys.exec_prefix):
        path = os.path.join(
            sys.base_exec_prefix,
            path[len(sys.exec_prefix):].lstrip(os.path.sep),
        )

    new_sys_path.append(path)
sys.path = new_sys_path

# We want to empty everything that has already been imported from the
# sys.modules so that any additional imports of these modules will import them
# from the base Python and not from the copies inside of the virtual
# environment. This will ensure that our copies will only be used for
# bootstrapping the virtual environment.
# TODO: is this really necessary? They would be the same modules as the global ones after all ///
dirty_modules = [
    # TODO: there might be less packages required but we
    # need to extend the integration tests to see exactly what
    "__builtin__",
    "__main__",
    "_frozen_importlib",
    "_frozen_importlib_external",
    "builtins",
    "codecs",
    "encodings",
    "site",
    "sitecustomize",
    "symbol",
]
dirty_modules.extend(sys.builtin_module_names)
for key in list(sys.modules):
    # We don't want to purge these modules because if we do, then things break
    # very badly.
    parts = key.split('.')
    if parts[0] in dirty_modules:
        continue
    else:
        del sys.modules[key]

# We want to trick the interpreter into thinking that the user specific
# site-packages has been requested to be disabled. We'll do this by mimicing
# that sys.flags.no_user_site has been set to False, however sys.flags is a
# read-only structure so we'll temporarily replace it with one that has the
# same values except for sys.flags.no_user_site which will be set to True.
_real_sys_flags = sys.flags
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
    def __getattr__(self, name):
        return self[name]
sys.flags = AttrDict((k, getattr(sys.flags, k)) for k in dir(sys.flags))
sys.flags["no_user_site"] = True

# We want to import the *real* site module from the base Python. Actually
# attempting to do an import here will just import this module again, so we'll
# just read the real site module and exec it.
with open(__SITE__) as fp:
    exec(fp.read())

# Restore the real sys.flags
sys.flags = _real_sys_flags

# On Debian-enized platforms the site.py won't add site-packages on sys.path
# (it will add dist-packages and other crazy stuff).
# Therefore we need to match pip's install location (site-packages)
from distutils import sysconfig
python_lib = sysconfig.get_python_lib()
if python_lib not in sys.path:
    addsitedir(python_lib)

# If we're running with the global site-packages enabled, then we'll want to
# go ahead and enable it here so that it comes after the virtual environment's
# site-package.
if global_site_packages is not None:
    # Force a re-check of ENABLE_USER_SITE so that we get the "real" value
    # instead of our forced off value.
    ENABLE_USER_SITE = check_enableusersite()

    # Add the actual user site-packages if we're supposed to.
    addusersitepackages(None)

    # Add the actual global site-packages.
    for path in global_site_packages:
        addsitedir(path)

# Apply distutils patches. Originally from virtualenv_embedded/distutils-init.py
# Support for per virtualenv distutils.cfg is missing.
def patch(module, name):
    original = getattr(module, name)

    def decorator(replacement):
        def wrapper(*args, **kwargs):
            return replacement(original, *args, **kwargs)
        wrapper.__doc__ = original.__doc__
        setattr(module, name, wrapper)
    return decorator

try:
    basestring
except NameError:
    basestring = str

# Patch build_ext (distutils doesn't know how to get the libs directory
# path on windows - it hardcodes the paths around the patched sys.prefix)
if sys.platform == 'win32':
    from distutils.command.build_ext import build_ext

    @patch(build_ext, 'finalize_options')
    def finalize_options(original, self):
        if self.library_dirs is None:
            self.library_dirs = []
        elif isinstance(self.library_dirs, basestring):
            self.library_dirs = self.library_dirs.split(os.pathsep)

        self.library_dirs.insert(0, os.path.join(sys.real_prefix, "Libs"))
        original(self)

## distutils.sysconfig patches:
from distutils import sysconfig

@patch(sysconfig, 'get_python_inc')
def sysconfig_get_python_inc(original, plat_specific=0, prefix=None):
    if prefix is None:
        prefix = sys.real_prefix
    return original(plat_specific, prefix)

@patch(sysconfig, 'get_python_lib')
def sysconfig_get_python_lib(original, plat_specific=0, standard_lib=0, prefix=None):
    if standard_lib and prefix is None:
        prefix = sys.real_prefix
    return original(plat_specific, standard_lib, prefix)

@patch(sysconfig, 'get_config_vars')
def sysconfig_get_config_vars(original, *args):
    real_vars = original(*args)
    if sys.platform == 'win32':
        lib_dir = os.path.join(sys.real_prefix, "libs")
        if isinstance(real_vars, dict) and 'LIBDIR' not in real_vars:
            real_vars['LIBDIR'] = lib_dir # asked for all
        elif isinstance(real_vars, list) and 'LIBDIR' in args:
            real_vars = real_vars + [lib_dir] # asked for list
    return real_vars
"""

logger = logging.getLogger(__name__)


class LegacyBuilder(BaseBuilder):

    @classmethod
    def check_available(cls, python):
        # TODO: Do we ever want to make this builder *not* available?
        return True

    def _locate_module(self, mod, search_paths):
        for search_path in search_paths:
            pymod = os.path.join(search_path, mod + ".py")
            if os.path.exists(pymod):
                return pymod
            path = os.path.join(search_path, mod)
            if os.path.exists(path):
                return path

    def _path_repr(self, string):
        return (
            b"'" +
            string.encode(sys.getfilesystemencoding())
                  .replace(b"'", b"\\'")
                  .replace(b"\\", b"\\\\") +
            b"'"
        )

    def create_virtual_environment(self, destination):
        logger.debug("Getting python info: \n%s", pprint.pformat(self._python_info))

        # Create our binaries that we'll use to create the virtual environment
        bin_dir = os.path.join(destination, self.flavor.bin_dir(self._python_info))
        ensure_directory(bin_dir)
        for python_bin in self.flavor.python_bins(self._python_info):
            copyfile(
                self._python_info["sys.executable"],
                os.path.join(bin_dir, python_bin),
            )

        # Copy extra bins, like some DLLs PyPy likes to have in it's bin dir ...
        for extra_bin in self.flavor.extra_bins(self._python_info):
            for bin_src in set([
                os.path.join(self._python_info["sys.prefix"], extra_bin),
                os.path.join(os.path.dirname(self._python_info["sys.executable"]), extra_bin),
            ]):
                if os.path.exists(bin_src):
                    copyfile(
                        bin_src,
                        os.path.join(bin_dir, extra_bin),
                    )

        # Create our lib directory, this is going to hold all of the parts of
        # the standard library that we need in order to ensure that we can
        # successfully bootstrap a Python interpreter.
        lib_dir = os.path.join(
            destination,
            self.flavor.lib_dir(self._python_info)
        )
        ensure_directory(lib_dir)

        # Create our site-packages directory, this is the thing that end users
        # really want control over.
        site_packages_dir = os.path.join(lib_dir, "site-packages")
        ensure_directory(site_packages_dir)

        # The site module has a number of required modules that it needs in
        # order to be successfully imported, so we'll copy each of those module
        # into our virtual environment's lib directory as well. Note that this
        # list also includes the os module, but since we've already copied
        # that we'll go ahead and omit it.
        sys_prefix = self._python_info["sys.prefix"]
        lib_dirs = [
            path for path in self._python_info["sys.path"]
            if path.startswith(sys_prefix)
            # TODO: this has an unhandled edgecase, it handle case with
            # partial match (should only match full components)

        ]

        for module in self.flavor.bootstrap_modules(self._python_info):
            modulepath = self._locate_module(module, lib_dirs)
            if modulepath:
                copyfile(
                    modulepath,
                    os.path.join(
                        destination,
                        os.path.relpath(modulepath, sys_prefix)
                    ),
                )

        osmodulepath = self._locate_module("os", lib_dirs)
        if not osmodulepath:
            raise RuntimeError("Can't locate os module in any of %s." % lib_dirs)
        osmoduledestination = os.path.join(
            destination,
            os.path.relpath(osmodulepath, sys_prefix)
        )
        copyfile(osmodulepath, osmoduledestination)

        include_dir = self.flavor.include_dir(self._python_info)
        src_include_dir = os.path.join(self._python_info["sys.prefix"], include_dir)
        if os.path.exists(src_include_dir):
            copyfile(src_include_dir, os.path.join(destination, include_dir))
            copyfile(src_include_dir, os.path.join(destination, "local", include_dir))
        else:
            logger.critical("You're missing %r. You many need to install the development packages for this intepreter.",
                            src_include_dir)

        dst = os.path.join(os.path.dirname(osmoduledestination), "site.py")
        logger.debug("Writing %s", dst)
        with io.open(dst, "wb") as dst_fp:
            # Get the data from our source file, and replace our special
            # variables with the computed data.
            data = SITE
            data = data.replace(b"__PREFIX__", self._path_repr(destination))
            data = data.replace(b"__EXEC_PREFIX__", self._path_repr(destination))
            data = data.replace(
                b"__BASE_PREFIX__",
                self._path_repr(self._python_info["sys.prefix"]),
            )
            data = data.replace(
                b"__BASE_EXEC_PREFIX__", self._path_repr(self._python_info["sys.exec_prefix"]),
            )
            data = data.replace(b"__SITE__", self._path_repr(self._python_info["site.py"]))
            data = data.replace(
                b"__GLOBAL_SITE_PACKAGES__",
                (
                    b"[" +
                    b", ".join(
                        self._path_repr(path) for path in self._python_info["site.getsitepackages"]
                    ) +
                    b"]"
                ) if self.system_site_packages else b"None",
            )

            if self.verbose:
                dst_fp.write(b"""# -*- encoding: utf-8 -*-
import sys
print("DEBUG: sys.modules:")
for m in sorted(sys.modules):
    print("DEBUG:   %s - %s" % (m, sys.modules[m]))
print("DEBUG: sys.path:")
for p in sys.path:
    print("DEBUG:   %s" % p)
""")

            # Write the final site.py file to our lib directory
            dst_fp.write(data)

            if self.verbose:
                dst_fp.write(b"""
print("DEBUG: sys.path after site.py run:")
for p in sys.path:
    print("DEBUG:   %s" % p)
""")
