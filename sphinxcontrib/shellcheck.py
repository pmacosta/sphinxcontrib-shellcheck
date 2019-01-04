# shellcheck.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0602,E1129,R0205,R0902,R0903,R0912,R0914,W0107

# Standard library import
from __future__ import print_function
import abc
import codecs
import json
import os
import platform
import re
import sys
import subprocess
import tempfile
import textwrap
import types

# Literal copy from [...]/site-packages/pip/_vendor/compat.py
try:
    from shutil import which
except ImportError:  # pragma: no cover
    # Implementation from Python 3.3
    def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        """Mimic CLI which function, copied from Python 3.3 implementation."""
        # pylint: disable=C0113,W0622
        # Check that a given file can be accessed with the correct mode.
        # Additionally check that `file` is not a directory, as on Windows
        # directories pass the os.access check.
        def _access_check(fn, mode):
            return os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn)

        # If we're given a path with a directory part, look it up directly rather
        # than referring to PATH directories. This includes checking relative to the
        # current directory, e.g. ./script
        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd
            return None

        if path is None:
            path = os.environ.get("PATH", os.defpath)
        if not path:
            return None
        path = path.split(os.pathsep)

        if sys.platform == "win32":
            # The current directory takes precedence on Windows.
            if not os.curdir in path:
                path.insert(0, os.curdir)

            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path extensions.
            # This will allow us to short circuit when given "python.exe".
            # If it does match, only test that one, otherwise we have to try
            # others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]

        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if not normdir in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(dir, thefile)
                    if _access_check(name, mode):
                        return name
        return None


# PyPI imports
import decorator
import docutils.nodes
import six
import sphinx.errors
import sphinx.util.logging
from sphinx.builders import Builder
from sphinx.locale import __


###
# Global variables
###
LOGGER = sphinx.util.logging.getLogger(__name__)
if sys.hexversion > 0x03000000:  # pragma: no cover
    STRING_TYPES = (str,)
    INTEGER_TYPES = (int,)
else:  # pragma: no cover
    STRING_TYPES = (basestring,)
    INTEGER_TYPES = (int, long)


###
# Functions
###
def _errors(stdout):
    for error in json.loads(_tostr(stdout)):
        code = error["code"]
        desc = error["message"]
        line = error["line"]
        col = error["column"]
        yield line, col, code, desc


def _get_indent(line):
    return len(line) - len(line.lstrip())


def _tostr(line):  # pragma: no cover
    if isinstance(line, str):
        return line
    if sys.hexversion > 0x03000000:
        return line.decode()
    return line.encode()


###
# Classes
###
class InvalidShellcheckBuilderConfig(sphinx.errors.SphinxError):  # noqa: D101
    category = __("ShellcheckBuilder failed")


@six.add_metaclass(abc.ABCMeta)
class LintShellBuilder(Builder):
    """Validate shell code in documents."""

    name = ""
    epilog = __(
        "Look for any errors in the above output or in " "%(outdir)s/output.txt"
    )

    def __init__(self, app):  # noqa
        super(LintShellBuilder, self).__init__(app)
        self._debug = False
        self._col_offset = 0
        self._header = None
        self._line_offset = 0
        self._nodes = []
        self._output = []
        self._srclines = None
        self._tabwidth = None
        self.dialect = ""
        self.docname = ""
        self.fname = os.path.join(self.outdir, "output.txt")
        self.source = None
        open(self.fname, "w").close()

    def _get_block_indent(self, node):
        return _get_indent(self._srclines[node.line + 1])

    def _is_shell_node(self, node):
        return (
            node.source
            and (node.tagname == "literal_block")
            and (node.attributes.get("language").lower() in self.dialects)
        )

    def _get_linter_stdout(self, lines):
        if self._debug:  # pragma: no cover
            LOGGER.info("<<< lines (_get_linter_stdout)")
            LOGGER.info(lines)
            LOGGER.info(">>>")
        with TmpFile(fpointer=lambda x: x.write(lines.encode("ascii"))) as fname:
            if self._debug:  # pragma: no cover
                with open(fname, "r") as fhandle:
                    check_lines = fhandle.readlines()
                LOGGER.info("Auto-generated shell file")
                LOGGER.info("".join(check_lines))
            obj = subprocess.Popen(
                self.cmd(fname), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = obj.communicate()
            if self._debug:  # pragma: no cover
                LOGGER.info("STDOUT")
                LOGGER.info(_tostr(stdout))
        return stdout

    def _lint_block(self, node, indent):
        # Create a shell script with all output lines commented out to be able
        # to report file line numbers correctly
        lines = ""
        cont_line, cmd_line = False, False
        value = node.astext()
        code_lines = _tostr(value).split("\n")
        lmin = max(len(code_line) for code_line in code_lines)
        if self._debug:  # pragma: no cover
            LOGGER.info("<<< Node code (_lint_block)")
            LOGGER.info(code_lines)
            LOGGER.info(">>>")
        for code_line in code_lines:
            cmd_line = code_line.strip().startswith(self.prompt)
            if cmd_line or cont_line:
                lines += code_line[1:] + "\n"
                lmin = min(lmin, _get_indent(code_line[1:]))
                cont_line = code_line.strip().endswith("\\")
            else:
                cont_line, cmd_line = False, False
                lines += (" " * lmin) + "# Output line\n"
        shebang = "#!/bin/bash\n"
        self._line_offset = node.line
        self._col_offset = _get_indent(lines.split("\n")[0]) + indent + 1
        lines = shebang + textwrap.dedent(lines)
        if self._debug:  # pragma: no cover
            LOGGER.info("<<< lines (_lint_block)")
            LOGGER.info(lines)
            LOGGER.info(">>>")
        self._output = []
        self.parse_linter_output(self._get_linter_stdout(lines))
        return self._output

    def _shell_nodes(self, doctree):
        regexp = re.compile("(.*):docstring of (.*)")
        for node in doctree.traverse():
            if self._is_shell_node(node):
                self.dialect = node.attributes.get("language").lower()
                self.source, func_abs_name = (
                    regexp.match(node.source).groups()
                    if ":docstring of " in node.source
                    else (node.source, None)
                )
                self.source = os.path.abspath(self.source.strip())
                if self._debug:  # pragma: no cover
                    LOGGER.info("Analyzing file " + self.source)
                    LOGGER.info("<<< Node code")
                    LOGGER.info(_tostr(node.astext()))
                    LOGGER.info(">>>")
                if func_abs_name:
                    tokens = func_abs_name.split(".")
                    func_path, func_name = ".".join(tokens[:-1]), tokens[-1]
                    func_obj = __import__(func_path).__dict__[func_name]
                    node.line = func_obj.__code__.co_firstlineno + node.line + 1
                self._read_source_file()
                indent = self._get_block_indent(node)
                if self._debug:  # pragma: no cover
                    LOGGER.info("Indent: " + str(indent))
                yield node, indent

    def _read_source_file(self):
        self._srclines = []
        node = docutils.nodes.Node()
        with open(self.source, "r") as obj:
            for line in obj.readlines():
                node.rawsource = line
                self._srclines.append(_tostr(node.rawsource.expandtabs(self._tabwidth)))

    def add_error(self, line, col, code, desc):
        """Add shell error to list of errors."""
        info = [
            self.source,
            line + self._line_offset,
            col + self._col_offset,
            code,
            desc,
        ]
        if self._debug:  # pragma: no cover
            LOGGER.info("info: " + str(info))
        if info not in self._nodes:
            if self._debug:  # pragma: no cover
                LOGGER.info("Adding info")
            self._nodes.append(info)
            self._output.append("Line {0}, column {1} [{2}]: {3}".format(*info[1:]))

    @abc.abstractmethod
    def cmd(self, fname):  # pragma: no cover
        """Return shell linter command."""
        return []

    @property
    @abc.abstractmethod
    def dialects(self):  # pragma: no cover
        """Return shell dialects supported."""
        pass

    def get_target_uri(self, docname, typ=None):  # pragma: no cover
        """Abstract method of base class, not germane to current builder."""
        return ""

    def get_outdated_docs(self):  # pragma: no cover
        """Abstract method of base class, not germane to current builder."""
        return self.env.found_docs

    @abc.abstractmethod
    def parse_linter_output(self, stdout):  # pragma: no cover
        """Extract linter error information from STDOUT."""
        return []

    def prepare_writing(self, docnames):  # pragma: no cover
        """Abstract method of base class, not germane to current builder."""
        return

    @property
    @abc.abstractmethod
    def prompt(self):  # pragma: no cover
        """Return prompt used to denote command line start."""
        pass

    def write_doc(self, docname, doctree):
        """Check shell nodes."""
        self.docname = docname
        self._tabwidth = doctree.settings.tab_width
        for node, indent in self._shell_nodes(doctree):
            errors = self._lint_block(node, indent)
            if errors:
                LOGGER.info(self.source)
                self.write_entry(self.source)
                for error in errors:
                    LOGGER.info(error)
                    self.write_entry(error)
        self.app.statuscode = 0

    def write_entry(self, error):
        """Write error to file."""
        with codecs.open(self.fname, "a", "utf-8") as output:
            output.write(
                "{0}: {1}{2}".format(
                    self.env.doc2path(self.docname, None), error, os.linesep
                )
            )


class ShellcheckBuilder(LintShellBuilder):
    """Validate shell code in documents using shellcheck."""

    name = "shellcheck"

    def __init__(self, app):  # noqa
        super(ShellcheckBuilder, self).__init__(app)
        self._debug = app.config.shellcheck_debug
        self._dialects = app.config.shellcheck_dialects
        self._exe = app.config.shellcheck_executable
        self._prompt = app.config.shellcheck_prompt
        # Validate configuration options. Data type validation done by Sphinx
        try:
            self._dialects = set(_tostr(item) for item in self._dialects)
            assert all(item in ["sh", "bash", "dash", "ksh"] for item in self._dialects)
        except:
            raise InvalidShellcheckBuilderConfig(__("Invalid dialect"))
        if not which(self._exe):
            raise InvalidShellcheckBuilderConfig(__("Shellcheck executable not found"))
        if len(self._prompt) != 1:
            raise InvalidShellcheckBuilderConfig(__("Invalid shellcheck prompt"))
        if self._debug not in (0, 1):
            raise InvalidShellcheckBuilderConfig(__("Invalid shellcheck debug flag"))
        self._debug = self._debug == 1

    @property
    def dialects(self):
        """Return shell dialects supported by linter."""
        return self._dialects

    @property
    def prompt(self):
        """Return character used to denote shell command prompt."""
        return self._prompt

    def cmd(self, fname):
        """Return command that runs the linter."""
        return [
            self._exe,
            "--shell=" + self.dialect,
            "--color=never",
            "--format=json",
            fname,
        ]

    def parse_linter_output(self, stdout):
        """Extract shellcheck error information from STDOUT."""
        for line, col, code, desc in _errors(stdout):
            if self._debug:  # pragma: no cover
                LOGGER.info("<<< Error")
                LOGGER.info("Line: " + str(line))
                LOGGER.info("Column: " + str(col))
                LOGGER.info("Code: " + str(code))
                LOGGER.info("Description: " + desc)
                LOGGER.info("<<<")
            self.add_error(line, col, code, desc)


class TmpFile(object):  # pragma: no cover
    """Create and manage temporary file."""

    def __init__(self, *args, **kwargs):  # noqa
        fpointer = kwargs.get("fpointer", None)
        if fpointer:
            del kwargs["fpointer"]
        if (
            fpointer
            and (not isinstance(fpointer, types.FunctionType))
            and (not isinstance(fpointer, types.LambdaType))
        ):
            raise RuntimeError(__("Argument `fpointer` is not valid"))
        self._fname = None
        self._fpointer = fpointer
        self._args = args
        self._kwargs = kwargs

    def __enter__(self):  # noqa
        fdesc, fname = tempfile.mkstemp()
        # fdesc is an OS-level file descriptor, see problems if this
        # is not properly closed in this post:
        # https://www.logilab.org/blogentry/17873
        os.close(fdesc)
        if platform.system().lower() == "windows":  # pragma: no cover
            fname = fname.replace(os.sep, "/")
        self._fname = fname
        if self._fpointer:
            with open(self._fname, "wb") as fobj:
                self._fpointer(fobj, *self._args, **self._kwargs)
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa
        with ignored(OSError):
            os.remove(self._fname)
        return not exc_type is not None


@decorator.contextmanager
def ignored(*exceptions):  # pragma: no cover
    """Ignore given exceptions."""
    try:
        yield
    except exceptions:
        pass


###
# Registration
###
def setup(app):
    """Register custom builder."""
    app.add_builder(ShellcheckBuilder)
    app.add_config_value("shellcheck_dialects", ["sh", "bash", "dash", "ksh"], "env")
    app.add_config_value("shellcheck_executable", "shellcheck", "env")
    app.add_config_value("shellcheck_prompt", "$", "env")
    app.add_config_value("shellcheck_debug", int(0), "env")
