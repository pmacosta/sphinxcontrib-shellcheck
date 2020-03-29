# functions.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0401,E0602,E1111,R0904,R1717,R1718,W0201,W0621,W0702

# Standard library imports
from __future__ import print_function
import glob
import io
import json
import os
import subprocess
import sys


###
# Functions
###
# This function is copied from .compat2 and .compat3
# Repeated here so as make functions in this file self-contained
if sys.hexversion < 0x03000000:

    def _readlines(fname):
        """Read all lines from file."""
        with open(fname, "r") as fobj:
            return fobj.readlines()


else:

    def _readlines(fname, fpointer1=open, fpointer2=open):
        """Read all lines from file."""
        # fpointer1, fpointer2 arguments to ease testing
        try:
            with fpointer1(fname, "r") as fobj:
                return fobj.readlines()
        except UnicodeDecodeError:  # pragma: no cover
            with fpointer2(fname, "r", encoding="utf-8") as fobj:
                return fobj.readlines()


# This function is copied from .compat2 and .compat3
# Repeated here so as make functions in this file self-contained
if sys.hexversion < 0x03000000:
    # Largely from From https://stackoverflow.com/questions/956867/
    # how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
    # with Python 2.6 compatibility changes
    def _unicode_to_ascii(obj):
        if isinstance(obj, dict):
            return dict(
                [
                    (_unicode_to_ascii(key), _unicode_to_ascii(value))
                    for key, value in obj.items()
                ]
            )
        if isinstance(obj, list):
            return [_unicode_to_ascii(element) for element in obj]
        if isinstance(obj, unicode):
            return obj.encode("utf-8")
        return obj


else:

    def _unicode_to_ascii(obj):
        return obj


def dir_tree(root, dir_exclude=None, ext_exclude=None):
    """Return all files at or under root directory."""
    ext_exclude = [] if ext_exclude is None else ext_exclude
    ext_exclude = ["." + item for item in ext_exclude]
    dir_exclude = [] if dir_exclude is None else dir_exclude
    dir_exclude = [os.path.join(root, item) for item in dir_exclude]
    for dname, _, fnames in os.walk(root):
        for fname in fnames:
            _, ext = os.path.splitext(fname)
            if any([dname.startswith(item) for item in dir_exclude]):
                continue
            if ext not in ext_exclude:
                yield os.path.join(dname, fname)


def gen_manifest(make_wheel=False):
    """Generate MANIFEST.in file."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fdata = json_load(os.path.join("data", "data_files.json"))
    ret = [
        "# MANIFEST.in",
        "# Copyright (c) 2013-2020 Pablo Acosta-Serafini",
        "# See LICENSE for details",
    ]
    if not make_wheel:
        for fdict in fdata:
            star = "*" in fdict["file"]
            ret.append(
                "{rec}include{fdir}{pattern}".format(
                    rec="recursive-" if star else "",
                    fdir=(
                        " {fdir}{sep}".format(
                            fdir=fdict["dir"],
                            sep="/" if fdict["dir"] and (not star) else "",
                        )
                        if fdict["dir"]
                        else ""
                    ),
                    pattern=(
                        "{sep}{fname}".format(
                            sep=" " if star or (not fdict["dir"]) else "",
                            fname=fdict["file"],
                        )
                    ),
                )
            )
    with open(os.path.join(pkg_dir, "MANIFEST.in"), "w") as fobj:
        fobj.writelines("\n".join(ret))


def get_coverage_exclude_files():
    """Return package entry points."""
    pkg_name = get_pkg_name()
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return [item.format(PKG_NAME=pkg_name) for item in pkgdata.COV_EXCLUDE_FILES]
    except:
        return []


def get_entry_points():
    """Return package entry points."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.ENTRY_POINTS
    except:
        return None


def get_pkg_copyright_start():
    """Return supported Python interpreter versions."""
    sys.path.append(get_src_dir())
    import pkgdata

    return pkgdata.COPYRIGHT_START


def get_pkg_data_files(share_dir):
    """Create data_files setup.py argument."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fdata = json_load(os.path.join("data", "data_files.json"))
    rdict = {}
    # For each directory a single list with all the file names in that
    # directory has to be provided, otherwise if multiple entries with
    # lists are provided only the last list is installed
    rdict = dict([(fdir, []) for fdir in set([item["dir"] for item in fdata])])
    for fdict in fdata:
        rdict[fdict["dir"]] = rdict[fdict["dir"]] + (
            glob.glob(os.path.join(pkg_dir, fdict["dir"], fdict["file"]))
        )
    return [
        (os.path.join(share_dir, fdir), rdict[fdir]) for fdir in sorted(rdict.keys())
    ]


def get_pkg_desc():
    """Return short package description."""
    sys.path.append(get_src_dir())
    import pkgdata

    return pkgdata.PKG_DESC


def get_pkg_doc_submodules():
    """Return package documentation submodules."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.PKG_DOC_SUBMODULES
    except:
        return []


def get_pkg_long_desc():
    """Return long package description."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.PKG_LONG_DESC
    except:
        return ""


def get_pkg_name():
    """Return package name."""
    stem = "pkgdata"
    start_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for (dirpath, _, fnames) in os.walk(start_dir):
        # Ignore .tox, .git and other directories
        if dirpath[len(start_dir) + 1 :].startswith("."):
            continue
        #
        for fname in fnames:
            if os.path.splitext(os.path.basename(fname))[0] == stem:
                return os.path.basename(dirpath)
    pkg_name = os.path.basename(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return pkg_name.split("-")[1] if pkg_name.startswith("sphinxcontrib-") else pkg_name


def get_pkg_pipeline_id():
    """Return Microsoft Azure Pipelines ID."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.PKG_PIPELINE_ID
    except:
        return 0


def get_pkg_submodules():
    """Return package submodules."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.PKG_SUBMODULES
    except:
        return []


def get_pkg_version():
    """Return supported Python interpreter versions."""
    sys.path.append(get_src_dir())
    import pkgdata

    return pkgdata.__version__


def get_sphinx_extensions():
    """Return Sphinx extensions used by package."""
    sys.path.append(get_src_dir())
    import pkgdata

    try:
        return pkgdata.SPHINX_EXTENSIONS
    except:
        return []


def get_src_dir():
    """Return package name."""
    # When requesting package directory for utility tasks, or when installing the
    # package, the source file is the parent directory of the directory where the
    # package management framework is located. However, when testing the package
    # the package management framework is installed in a completely directory tree,
    # thus its location has to be inferred by importing the package
    pkg_name = get_pkg_name()
    tdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(tdir, pkg_name)
    if os.path.exists(os.path.join(src_dir, "pkgdata.py")):
        return src_dir
    backend = "Agg"
    try:
        import matplotlib

        matplotlib.rcParams["backend"] = backend
        import matplotlib as mpl

        mpl.rcParams["backend"] = backend
    except ImportError:
        pass
    __import__(pkg_name)
    src_dir = os.path.dirname(os.path.abspath(sys.modules[pkg_name].__file__))
    if os.path.exists(src_dir):
        return src_dir
    raise RuntimeError("Could not find package source directory")


def get_supported_interps():
    """Return supported Python interpreter versions."""
    # pylint: disable=W0122
    sys.path.append(get_src_dir())
    import pkgdata

    return pkgdata.SUPPORTED_INTERPS


def json_load(fname):
    """Load JSON file."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_file = os.path.join(pkg_dir, fname)
    with io.open(conf_file, "r") as fobj:
        fdata = json.load(fobj)
    if sys.hexversion < 0x03000000:
        fdata = _unicode_to_ascii(fdata)
    return fdata


def load_requirements(pkg_dir, pyver, cat="source"):
    """Get package names from requirements files."""
    rtd = os.environ.get("READTHEDOCS", "")
    pyver = pyver.replace(".", "")
    reqs_dir = os.path.join(pkg_dir, "requirements")
    if cat.lower() == "source":
        reqs_files = ["rtd.pip"] if rtd else ["main_py{0}.pip".format(pyver)]
    elif cat.lower() == "testing":
        reqs_files = ["tests_py{0}.pip".format(pyver), "docs_py{0}.pip".format(pyver)]
    else:
        raise RuntimeError("Unknown requirements category: {0}".format(cat))
    ret = []
    for fname in [os.path.join(reqs_dir, item) for item in reqs_files]:
        with open(os.path.join(reqs_dir, fname), "r") as fobj:
            lines = [item.strip() for item in fobj.readlines() if item.strip()]
        ret.extend(lines)
    return ret


def pcolor(text, color, indent=0):
    """Return a string that once printed is colorized (copied from .strings)."""
    esc_dict = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "none": -1,
    }
    if not isinstance(text, str):
        raise RuntimeError("Argument `text` is not valid")
    if not isinstance(color, str):
        raise RuntimeError("Argument `color` is not valid")
    if not isinstance(indent, int):
        raise RuntimeError("Argument `indent` is not valid")
    color = color.lower()
    if color not in esc_dict:
        raise ValueError("Unknown color {color}".format(color=color))
    if esc_dict[color] != -1:
        return "\033[{color_code}m{indent}{text}\033[0m".format(
            color_code=esc_dict[color], indent=" " * indent, text=text
        )
    return "{indent}{text}".format(indent=" " * indent, text=text)


def python_version(hver):
    """Return Python version."""
    return "{major}.{minor}".format(major=int(hver[:-2]), minor=int(hver[-2:]))


def shcmd(cmd_list, exmsg, async_stdout=False):
    """Execute command piping STDERR to STDOUT."""
    try:
        proc = subprocess.Popen(
            cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    except:
        print("COMMAND: {0}".format(" ".join(cmd_list)))
        raise
    while async_stdout:
        if sys.hexversion < 0x03000000:
            line = proc.stdout.readline()
        else:
            line = proc.stdout.readline().decode("utf-8")
        if (line == "") and (proc.poll() is not None):
            break
        sys.stdout.write(line)
        sys.stdout.flush()
    stdout, stderr = proc.communicate()
    retcode = proc.returncode
    if sys.hexversion >= 0x03000000:
        stdout = stdout.decode("utf-8") if stdout is not None else stdout
        stderr = stderr.decode("utf-8") if stderr is not None else stderr
    if retcode:
        print("COMMAND: {0}".format(" ".join(cmd_list)))
        print("STDOUT:")
        print(stdout)
        print("STDERR:")
        print(stdout)
        raise RuntimeError(exmsg)
    return stdout
