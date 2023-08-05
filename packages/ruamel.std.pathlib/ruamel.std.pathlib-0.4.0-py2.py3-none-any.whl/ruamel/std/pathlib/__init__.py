# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

_package_data = dict(
    full_package_name="ruamel.std.pathlib",
    version_info=(0, 4, 0),
    author="Anthon van der Neut",
    author_email="a.van.der.neut@ruamel.eu",
    since="2013",
    description="improvements over the standard pathlib module and pathlib2 package",
    entry_points=None,
    install_requires=dict(
        any=[],
        py26=["pathlib2"],
        py27=["pathlib2"],
        py33=["pathlib2"],
        py34=["pathlib2"],  # expanduser added
    ),
    license="MIT License",
    # status= "α",
    # data_files= "",
    universal=True,
)


# < from ruamel.util.new import _convert_version
def _convert_version(tup):
    """Create a PEP 386 pseudo-format conformant string from tuple tup."""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    for x in tup[1:]:
        if isinstance(x, int):
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            ret_val += '.post' if first_letter == 'p' else '.dev'
    return ret_val
# <

version_info = _package_data['version_info']
__version__ = _convert_version(version_info)

del _convert_version

###########

import os       # NOQA
import sys      # NOQA
import inspect  # NOQA

if sys.version_info < (3, 5):
    # 3.4 e.g has no expanduser()
    from pathlib2 import *  # NOQA
else:
    from pathlib import *   # NOQA


class DirStack(object):
    def __init__(self):
        self._dir_stack = []

    def pushd(self, d):
        self._dir_stack.insert(0, os.getcwd())
        os.chdir(str(d))

    def popd(self):
        os.chdir(self._dir_stack.pop())

# global stack, always there
_dir_stack = DirStack()


def pushd(d):
    _dir_stack.pushd(d)


def popd():
    _dir_stack.popd()

# pathlib 0.8 was not compatible with pathlib in python 3.4,
# but 0.97 is
# should check here but there is no version number in pathlib ...
# switched to pathlib2 which aims at compatibility
#
#     @property
#     def root_stem(self):
#         """The final path component, minus suffices."""
#         return self.name.split('.', 1)[0]


# just for some sanity
Path.remove = Path.unlink


def _rmtree(self):
    import shutil
    assert self.is_dir()
    shutil.rmtree(str(self))

Path.rmtree = _rmtree


def _chdir(self):
    assert self.is_dir()
    os.chdir(str(self))

Path.chdir = _chdir

# #
# # - If the check level is set at 1, any calls that are issued with strings that
# #     could be changed are logged (to the console), those are the positions where
# #     arguments should still be converted from string to Path.
# # - If check level is set at 2, all call to pl methods are logged, those
# #     are the areas where the calls can be replaced by methods on the Path instance,
# #     check level 3 is the same as level 1, but any remaining string isntances throw
# #         an error.


class PathLibConversionHelper(object):
    """
    if you are changing to use the standard pathlib library, it is cumbersome
    to change everything at once, and also to change all the arguments to calls to
    os.path.join, os.rename, os.path.dirname to be made encapsulated in str()

    by making an instance of PathLibConversionHelper named pl you can change
    os.path.join() to pl.path.join(), etc., and then start passing in Path instances
    instead of strings.

    if the check level is set at 1 any calls that are issued with strings that
    could be changed are logged (to the console), those are the positions where
    arguments should still be converted from string to Path
    if check level is set at 2, all call to pl methods are logged, those
    are the areas where the calls can be replaced by methods on the Path instance,
    check level 3 is the same as level 1, but any remaining string isntances throw
    an error.

    maybe look at https://github.com/mikeorr/Unipath#comparision-with-osospathshutil-and-pathpy
    and incorporate
    """
    def __init__(self, check=0):
        class Container(object):
            pass
        self._check = check
        self._usage = {}
        path = self.path = Container()
        path.join = self._path_join
        path.dirname = self._path_dirname
        path.exists = self._path_exists

    def add_usage(self, vars, comment):
        if isinstance(vars, (list, tuple)):
            vt = tuple([isinstance(x, Path) for x in vars])
        else:
            vt = tuple([isinstance(vars, Path)])
        if self._check < 1:
            return
        caller = inspect.stack()[2]
        t = caller[1], caller[2], comment, vt
        count = self._usage.setdefault(t, [0, ])
        count[0] += 1
        if self._check > 1 and count[0] == 1:
            print('{2} [{0}:{1} / Path {3}]'.format(*t))

    def dump(self, stream=None, show_all=False):
        """dump unique invocations of methods

        unless show_all is True, invocations that uniquely use Path arguments
        are not shown
        """
        if stream is None:
            stream = sys.stdout
        for t in self._usage:
            if show_all or not all(t[3]):
                print('{t[2]} [{t[0]}:{t[1]} / {count} / Path {t[3]}]'.format(
                    count=self._usage[t][0], t=t))

    def rename(self, old_name, new_name):
        """os.rename replacement that can handle Path argument"""
        self.add_usage([old_name, new_name], 'update .rename')
        if isinstance(old_name, Path):
            old_name.rename(new_name)  # rename works with strings and Path
        else:
            os.rename(old_name, str(new_name))
    # os.rename
    # os.getcwd
    # os.path.expanduser

    def _path_join(self, base, *args):
        self.add_usage([base] + list(args), 'update .path.join to use "/"')
        # os.path.join
        if isinstance(base, Path):
            return base.joinpath(*args)
        else:
            return os.path.join(base, *args)

    def _path_exists(self, path):
        # os.path.join
        self.add_usage(path, 'update .exists to use Path.exists()')
        if isinstance(path, Path):
            return path.exists()
        else:
            return os.path.exists(path)

    def _path_dirname(self, file_name):
        self.add_usage(file_name, 'update .path.dirname to use Path.parent')
        if isinstance(file_name, Path):
            return file_name.parent
        else:
            return os.path.dirname(file_name)

    # os.chdir
    def chdir(self, path):
        self.add_usage(
            path,
            'update .chdir to use Path.chdir() or os.chdir(str(Path))')
        if isinstance(path, Path):
            return path.chdir()
        else:
            return os.chdir(path)

    # os.mkdir
    # os.makedirs

    def glob(self, pattern):
        """replaces: glob.glob()"""
        import glob
        self.add_usage(path, 'update .glob to use Path.glob()')
        if isinstance(pattern, Path):
            return [Path(fn) for fn in glob.glob(str(pattern))]
        else:
            return glob.glob(pattern)

    # shutil.rmtree
    def rmtree(self, path):
        """replaces: shutil.rmtree()"""
        import shutil
        self.add_usage(
            path, 'update .rmtree to use Path.rmtree() or shutil.rmtree(str(Path))')
        if isinstance(path, Path):
            return path.rmtree()
        else:
            return shutil.rmtree(path)

    # built-in open
    def open(self, path, mode='r', buffering=1):
        """replaces: built-in open()"""
        self.add_usage(path, 'update .open to use Path.open()')
        if isinstance(path, Path):
            return path.open(mode, buffering)
        else:
            return open(path, mode, buffering)

    def mkstemp(self, suffix="", prefix=None, dir=None, text=False):
        """replaces: tempfile.mkstemp()"""
        import tempfile
        if prefix is None:
            prefix = tempfile.template
        self.add_usage(dir, 'update .mkstemp to use Path.mkstemp()')
        if isinstance(dir, Path):
            dir = str(dir)
        return tempfile.mkstemp(suffix, prefix, dir, text)
