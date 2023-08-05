#!/usr/bin/env python
"""Generates metapackages for Arch Linux."""
from collections import OrderedDict
from datetime import datetime
from io import StringIO
import os.path
import platform
import re
from shlex import quote as Q
import sys
from urllib.parse import quote as urlquote

import click
import pycman
import requests

_PYCMAN_HANDLE = pycman.config.init_with_config("/etc/pacman.conf")
_PYCMAN_DB = _PYCMAN_HANDLE.get_localdb()

__all__ = [
    'parse_metabuild', 'parse_statements', 'parse_pkglist',
    'generate_pkgbuild', 'quick_metapkg',
    'Statement', 'Package',
    'MetapkgError', 'ParseError', 'InvalidPackageError',
    'METABUILDError', 'PKGBUILDError',
    'main'
]


_TOKEN_CHARS = re.compile(r'[0-9a-zA-Z@_+\-.]')
_TOKEN_BOUNDARIES = re.compile('[#;:=" \t\n\r\f\v]')
_DIRECTIVES = re.compile('desc|ver|rel|(opt)?deps|provides|arch')
_NAME_DIRECTIVES = re.compile('desc|ver|rel')

_DEFAULT_DESC = "Pacmeta metapackage"

_TESTING = False


def _linecol(string, pos):
    """Returns the string "line _, col _" from a given string and index."""
    line, col = 1, 0
    for char in string[:pos]:
        if char == "\n":
            line += 1
            col = 0
        else:
            col += 1
    return "line %d, col %d" % (line, col)


class MetapkgError(Exception):
    """Base class to all metapkg errors."""
    pass


class ParseError(MetapkgError):
    """Thrown from parse_metabuild on parse errors."""
    __slots__ = ('err',)

    def __init__(self, err):
        super(ParseError, self).__init__()
        self.err = err

    def __repr__(self):
        return CLI_STRINGS['parse_err'].format(self.err)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return isinstance(other, ParseError) and self.err == other.err


# pylint: disable=too-few-public-methods
class Statement(object):
    """Used to store statements from METABUILD"""
    __slots__ = ('arch', 'directive', 'names', 'data')

    def __init__(self):
        self.directive = None
        self.arch = []
        self.names = []
        self.data = []

    def empty(self):
        """Whether this statement can be ignored."""
        return self.directive is None and len(self.names) == 0

    def __str__(self):
        arch = '.arch {}: '.format(' '.join(self.arch)) \
            if len(self.arch) > 0 \
            else ''
        directive = '.{} '.format(self.directive) \
            if self.directive and self.directive != 'deps' \
            else ''
        names = ' '.join(self.names)
        data = ' '.join(self.data)
        return '{}{}{} = {}'.format(
            arch, directive, names, data
        )

    def __repr__(self):
        lst = []
        if len(self.arch) > 0:
            lst.append('arch = ' + repr(self.arch))
        if self.directive:
            lst.append('directive = ' + repr(self.directive))
        if self.names:
            lst.append('names = ' + repr(self.names))
        if self.data:
            lst.append('data = ' + repr(self.data))
        return "Statement({})".format(', '.join(lst))


def parse_metabuild(mbuild):
    """Parses a metabuild file into a list of statements."""
    defs = [Statement()]

    # current token is mbuild[start : end]
    start, end = 0, 0

    # parser states
    has_arch = False
    has_directive = False  # resets at colon
    has_colon = False
    has_package = False    # has at least one name after recent directive
    has_equals = False

    # force new line at end of file
    mbuild += "\n"

    # the last token ends at the end of the string
    while end < len(mbuild):
        char = mbuild[end]

        # if the first character of a token is a period, we have a directive
        if start == end and char == '.':
            # skip over the period
            end += 1
            start += 1

            # grab the full name without the period
            while end < len(mbuild) and _TOKEN_CHARS.match(mbuild[end]):
                end += 1
            directive = mbuild[start:end].lower()

            # don't allow directives if:
            # * we already have one
            # * we've already grabbed a package name
            if has_directive or has_package:
                raise ParseError(
                    "can't have `{}` here on {}"
                    .format(mbuild[start - 1: end],
                            _linecol(mbuild, start - 1))
                )

            # make sure that the directive is valid
            if not _DIRECTIVES.match(directive):
                raise ParseError(
                    "unknown directive `{}' on {}"
                    .format(mbuild[start - 1: end],
                            _linecol(mbuild, start - 1))
                )

            start = end

            has_directive = True
            if directive == 'arch':
                has_arch = True
            else:
                defs[-1].directive = directive

        # these characters end a token
        elif _TOKEN_BOUNDARIES.match(char):
            # if we have a valid token, add it
            if end > start:
                token = mbuild[start:end]

                # don't allow hyphen at beginning
                if token[0] == '-' and token != '-' and token != '--':
                    raise ParseError(
                        "names can't start with hyphen on {}"
                        .format(_linecol(mbuild, start))
                    )

                # add token to different list depending on position
                if has_arch and not has_colon:
                    if token.lower() != 'any':
                        defs[-1].arch.append(token)
                elif not has_equals:
                    defs[-1].names.append(token)
                else:
                    # make sure that we don't have extraneous input
                    if (defs[-1].directive and
                            _NAME_DIRECTIVES.match(defs[-1].directive) and
                            len(defs[-1].data) > 0):
                        raise ParseError(
                            "extraneous input to `.{}' on {}"
                            .format(defs[-1].directive,
                                    _linecol(mbuild, start))
                        )

                    defs[-1].data.append(token)

                # indicate that we have at least one name
                has_package = True

            if char == "#":
                # skip over comments
                while end < len(mbuild) and mbuild[end] != "\n":
                    end += 1

            elif char == "\"":
                # can't have quote except in certain directives
                if (defs[-1].directive is None or
                        not has_equals and
                        _NAME_DIRECTIVES.match(defs[-1].directive)):
                    raise ParseError(
                        "can't have quoted string here on {}"
                        .format(_linecol(mbuild, end))
                    )

                # can't have extraneous input
                if len(defs[-1].data) > 0:
                    raise ParseError(
                        "extraneous input to `.{}' on {}"
                        .format(defs[-1].directive, _linecol(mbuild, start))
                    )

                # don't include quote character in string
                end += 1
                start = end

                while end < len(mbuild):
                    # if we find an unescaped quote, end the string
                    if mbuild[end] == char and mbuild[end - 1] != '\\':
                        break
                    end += 1
                # if we reach EOF before ending the string, error
                else:
                    raise ParseError(
                        "unended quote in METABULID on {}"
                        .format(_linecol(mbuild, start - 1))
                    )

                # replace escaped quotes with real ones in added token
                defs[-1].data.append(
                    mbuild[start:end].replace('\\"', '"')
                )

            # semicolons end this definition and make a new one
            elif char == ";":
                # if we have a full statement, we're good
                if len(defs[-1].data) > 0:
                    defs.append(Statement())
                    has_arch = False
                    has_directive = False
                    has_package = False
                    has_colon = False
                    has_equals = False
                # if partial data, give error
                elif has_directive or has_package or has_colon or has_equals:
                    raise ParseError(
                        "invalid statement on {}".format(_linecol(mbuild, end))
                    )

            elif char == ':':
                # don't allow colons if:
                # * we already have one
                # * we haven't inputted a package name (architecture) yet
                if has_colon or not has_package:
                    raise ParseError(
                        "dangling colon on {}".format(_linecol(mbuild, end))
                    )

                # don't allow colons without an .arch directive
                if not has_arch:
                    raise ParseError(
                        "colon without `.arch' on {}"
                        .format(_linecol(mbuild, end))
                    )

                # act like we're on a new statement
                has_directive = False
                has_package = False
                has_colon = True

            elif char == '=':
                # don't allow equals if:
                # * we don't have a package name
                # * we already have an equals sign
                # * we're using .arch and don't have a colon
                if ((not has_package or has_equals) or
                        (has_arch and not has_colon)):
                    raise ParseError(
                        "dangling equals on {}; did you forget a semicolon?"
                        .format(_linecol(mbuild, end))
                    )

                has_equals = True

            # skip over the boundary character and start a new token
            end += 1
            start = end

        # invalid character somewhere
        elif not _TOKEN_CHARS.match(char):
            raise ParseError(
                "invalid `{}' in METABUILD on {}"
                .format(char, _linecol(mbuild, end))
            )

        # ordinary name; just increment token end
        else:
            end += 1

    # empty definitions are okay
    if defs[-1].empty():
        defs.pop()

    # empty files aren't okay
    if len(defs) == 0:
        raise ParseError("no package definitions found")

    # if last statement is incomplete but not empty
    if len(defs[-1].data) == 0:
        raise ParseError(
            "last statement is incomplete on {}"
            .format(_linecol(mbuild, len(mbuild) - 1))
        )

    return defs


class Package(object):
    """Used to store parsed packages from statements."""
    __slots__ = ('desc', 'ver', 'rel', 'deps', 'optdeps', 'provides', 'arch')

    def __init__(self):
        self.desc = None
        self.ver = None
        self.rel = None
        self.deps = set()
        self.optdeps = set()
        self.provides = set()
        self.arch = set()

    def run(self, name, directive, data, names):
        """Runs a statement, adding its data to the package."""
        if directive == 'deps' or directive is None:
            self.deps |= parse_pkglist(data, names, name)
        elif directive == 'optdeps':
            self.optdeps |= parse_pkglist(data, names, name)
        elif directive == 'provides':
            self.provides |= set(data)
        elif directive == 'desc':
            self.desc = data[0]
        elif directive == 'ver':
            self.ver = data[0]
        else:  # if directive == 'rel':
            self.rel = data[0]

    def __repr__(self):
        lst = []
        if self.desc:
            lst.append('desc = ' + repr(self.desc))
        if self.ver:
            lst.append('ver = ' + repr(self.ver))
        if self.rel:
            lst.append('rel = ' + repr(self.rel))
        if len(self.deps) > 0:
            lst.append('deps = ' + repr(self.deps))
        if len(self.optdeps) > 0:
            lst.append('optdeps = ' + repr(self.optdeps))
        if len(self.provides) > 0:
            lst.append('provides = ' + repr(self.provides))
        if len(self.arch) > 0:
            lst.append('arch = ' + repr(self.arch))
        return "Package({})".format(', '.join(lst))


def parse_statements(defs):
    """Parses a list of package statements into a list of packages."""
    pkgs = {}
    arch = platform.machine()

    # grab all possible names first
    names = set()
    for defn in defs:
        names |= set(defn.names)
        if defn.directive == 'provides':
            names |= set(defn.data)

    for defn in defs:
        # if architecture is specified, only run if ours is listed
        if len(defn.arch) > 0:
            if arch not in defn.arch and 'any' not in defn.arch:
                continue

        # multiple names is just a shortcut to run multiple times
        for name in defn.names:
            # ensure that package exists
            if name not in pkgs:
                pkgs[name] = Package()

            # fix arch
            if len(pkgs[name].arch) == 0:
                pkgs[name].arch |= set(defn.arch)
            else:
                pkgs[name].arch &= set(defn.arch)

            # run directive
            pkgs[name].run(name, defn.directive, defn.data, names)

    return pkgs


class InvalidPackageError(MetapkgError):
    """Thrown from parse_pkglist when a name is invalid."""
    __slots__ = ('pkg', 'metapkg', 'removed')

    def __init__(self, pkg, metapkg, removed=False):
        super(InvalidPackageError, self).__init__()
        self.pkg = pkg
        self.metapkg = metapkg
        self.removed = removed

    def __repr__(self):
        key = 'package_remove_err' if self.removed else 'package_add_err'
        return CLI_STRINGS[key].format(self.pkg, self.metapkg)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (isinstance(other, InvalidPackageError) and
                self.pkg == other.pkg and
                self.metapkg == other.metapkg and
                self.removed == other.removed)


def parse_pkglist(lst, names, source):
    """Pulls a list of packages from a given package list."""
    pkgs = set()
    state = '+'

    def add_pkg(pkg):
        """Adds a single package to the list."""
        # always called for a valid package; adding is fine
        if state[0] == '+':
            pkgs.add(pkg)

        # if we're removing, we have to check that we've already added it
        elif state[0] == '-':
            if pkg in pkgs or state == '--':
                pkgs.remove(pkg)
            else:
                raise InvalidPackageError(pkg, source, True)

    def add_pkgs(pkg):
        """Adds a set of packages to the list."""
        # always called for a valid package
        if state[0] == '+':
            pkgs.update(pkg)

        # if we're removing, we have to check if we've already added it
        elif state[0] == '-':
            # if there's no failure condition, use the efficent difference
            if state == '--':
                pkgs.difference_update(pkg)

            # otherwise do it manually
            else:
                for name in sorted(pkg):
                    if name in pkgs:
                        pkgs.remove(name)
                    else:
                        raise InvalidPackageError(name, source, True)

    for pkg in lst:
        # modifiers change state
        if pkg in ('+', '-', '++', '--'):
            state = pkg
            continue

        # allow packages that are defined in file
        # allow local packages
        if pkg in names or _PYCMAN_DB.get_pkg(pkg):
            add_pkg(pkg)
            continue

        # try searching synchronised repos
        repos = _PYCMAN_HANDLE.get_syncdbs()
        for repo in repos:
            # valid package name
            if repo.get_pkg(pkg):
                add_pkg(pkg)
                break

            # valid package group
            group = repo.read_grp(pkg)
            if group:
                add_pkgs({p.name for p in group[1]})
                break

        # not in synchronised repos; try AUR
        else:
            pkginfo = requests.get(
                'http://aur.archlinux.org/rpc.php?type=info&arg=' +
                urlquote(pkg),
                headers={'Connection': 'close'}
            ).json()
            if pkginfo['results'] != []:
                add_pkg(pkg)
            # nowhere to be found
            elif len(state) == 1:
                raise InvalidPackageError(pkg, source)

    return pkgs


def generate_pkgbuild(pkgs, outfile):
    """Generates a PKGBUILD from a dictionary of name: package."""

    def echo(string):
        """Lazy function."""
        click.echo(string, file=outfile)

    def shlist(itr):
        """Converts an iterator into a shell list."""
        return ' '.join(Q(x) for x in sorted(itr))

    # for testing
    now = datetime(1970, 1, 1) if _TESTING else datetime.now()

    # sort packages by name
    ordered_pkgs = OrderedDict(sorted(pkgs.items()))

    # global header
    echo('pkgname=({})'.format(' '.join(ordered_pkgs.keys())))
    echo('pkgver={}'.format(now.strftime("%Y%m%d.%H%M%S")))
    echo('pkgrel=1')
    echo('arch=(any)')
    echo('license=(custom)')
    echo('groups=(\'metapkg\')')

    for name, pkg in ordered_pkgs.items():
        # local header; always include description
        echo('package_{}() {{'.format(Q(name)))
        echo('\tpkgdesc=' + Q(pkg.desc or _DEFAULT_DESC))

        # version and release
        for name, val in (('pkgver', pkg.ver), ('pkgrel', pkg.rel)):
            if val:
                echo('\t{}={}'.format(name, Q(val)))

        # depends, optdepends, and provides
        for name, val in (('depends', pkg.deps),
                          ('optdepends', pkg.optdeps),
                          ('provides', pkg.provides)):
            if len(val) > 0:
                echo('\t{}=({})'.format(name, shlist(val)))

        # override architecture for package
        if len(pkg.arch) > 0:
            echo('\tarch=({})'.format(shlist(pkg.arch)))

        # local footer
        echo('}')


def quick_metapkg(contents):
    """Quickly converts METABUILD string into a PKGBUILD string."""
    out = StringIO()
    defs = parse_metabuild(contents)
    pkgs = parse_statements(defs)
    generate_pkgbuild(pkgs, out)
    return out.getvalue()


def _cli_parse_metapkg(metabuild):
    """
    Parses the metapackage from a given METABUILD file handle, returning
    the value of parse_statements.
    """
    defs = parse_metabuild(metabuild.read())
    pkgs = parse_statements(defs)
    return pkgs


CLI_STRINGS = {
    'force_help':
        'Create PKGBUILD even if one already exists.',
    'metabuild_help':
        'Use the specified METABUILD file',
    'metabuild_err':
        'Error: METABUILD file not found.',
    'pkgbuild_help':
        'Use the specified PKGBUILD file',
    'pkgbuild_err':
        'Error: PKGBUILD exists; specify --force to overwrite old file.',
    'stdin_help':
        'Input from stdin instead of METABUILD (overrides -m).',
    'stdout_help':
        'Output to stdout instead of PKGBUILD (overrides -p).',
    'parse_err':
        'Syntax Error: {}',
    'package_add_err':
        'Package Error: `{}\' for `{}\' could not be found.',
    'package_remove_err':
        'Package Error: `{}\' is not in package list for `{}\'.',
}


class METABUILDError(MetapkgError):
    """Indicates that the METABUILD file was invalid."""
    def __repr__(self):
        return CLI_STRINGS['metabuild_err']

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return isinstance(other, METABUILDError)


class PKGBUILDError(MetapkgError):
    """Indicates that the PKGBUILD file was invalid."""
    def __repr__(self):
        return CLI_STRINGS['pkgbuild_err']

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return isinstance(other, PKGBUILDError)


@click.command()
@click.option('--force', '-f', is_flag=True,
              help=CLI_STRINGS['force_help'])
@click.option('--metabuild', '-m', default='METABUILD',
              help=CLI_STRINGS['metabuild_help'])
@click.option('--pkgbuild', '-p', default='PKGBUILD',
              help=CLI_STRINGS['pkgbuild_help'])
@click.option('--stdin', '-I', is_flag=True,
              help=CLI_STRINGS['stdin_help'])
@click.option('--stdout', '-O', is_flag=True,
              help=CLI_STRINGS['stdout_help'])
def main(force, metabuild, pkgbuild, stdin, stdout):
    """Main function"""
    if not stdin and not os.path.exists(metabuild):
        raise METABUILDError()

    if not stdout and not force and os.path.exists(pkgbuild):
        raise PKGBUILDError()

    if stdin:
        pkgs = _cli_parse_metapkg(sys.stdin)
    else:
        with open(metabuild) as mbf:
            pkgs = _cli_parse_metapkg(mbf)

    if stdout:
        generate_pkgbuild(pkgs, sys.stdout)
    else:
        with open(pkgbuild, 'w') as pbf:
            generate_pkgbuild(pkgs, pbf)
