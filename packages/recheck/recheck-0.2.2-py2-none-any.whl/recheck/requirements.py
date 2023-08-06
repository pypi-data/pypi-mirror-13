import collections
import operator
import os
import re


class OutdatedRequirement(object):
    def __init__(self, name, installed_version, remote_version,
                 requirements_file=None):
        self._name = name
        self._installed_version = installed_version
        self._remote_version = remote_version
        self._requirements_file = requirements_file

    @property
    def name(self):
        return self._name

    @property
    def installed_version(self):
        return self._installed_version

    @property
    def remote_version(self):
        return self._remote_version

    @property
    def requirements_file(self):
        return self._requirements_file

    @requirements_file.setter
    def requirements_file(self, requirements_file):
        self._requirements_file = requirements_file

    @property
    def status(self):
        installed_version = _parse_version(self.installed_version)
        remote_version = _parse_version(self.remote_version)

        if installed_version.major < remote_version.major:
            return 'outdated:major'
        if installed_version.minor < remote_version.minor:
            return 'outdated:minor'
        if installed_version.patch < remote_version.patch:
            return 'outdated:patch'

    def __eq__(self, other):
        return all([
            self.name == other.name,
            self.installed_version == other.installed_version,
            self.remote_version == other.remote_version,
            self.requirements_file == other.requirements_file,
        ])

    def __hash__(self):
        return reduce(operator.xor, map(hash, [self.name,
                                               self.installed_version,
                                               self.remote_version,
                                               self.requirements_file]))


Version = collections.namedtuple('Version', ['major', 'minor', 'patch'])


def _read_lines_from_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()


class RequirementsParser(object):
    def __init__(self, requirements_file):
        self._dirname = os.path.dirname(requirements_file)
        self._requirements_files = collections.deque([requirements_file])
        self._direct_requirements = {}
        self._index_url = None
        self._extra_index_urls = []
        self._parse()

    def _handle_comment(self, line):
        return

    def _handle_pip_directive(self, line):
        directive, value = re.split('\s+|=', line, 1)
        if directive == '-r':
            filepath = value.strip()
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._dirname, filepath)
            self._requirements_files.append(filepath)
        elif directive == '--index-url':
            self._index_url = value.strip()
        elif directive == '--extra-index-url':
            self._extra_index_urls.append(value.strip())

    def _handle_requirement_line(self, requirement_file, line):
        result = re.split('==|>|<|>=|<=', line)
        req = result[0].strip()
        if not req:
            return
        self.direct_requirements[req.strip()] = requirement_file

    def _parse(self):
        try:
            while True:
                requirement_file = self._requirements_files.popleft()
                lines = _read_lines_from_file(requirement_file)
                for line in lines:
                    if line.startswith('#'):
                        self._handle_comment(line)
                    elif line.startswith('-'):
                        self._handle_pip_directive(line)
                    else:
                        self._handle_requirement_line(requirement_file, line)
        except IndexError:
            # No unprocessed requirements file. Parsing complete
            return None

    @property
    def direct_requirements(self):
        return self._direct_requirements

    @property
    def index_url(self):
        return self._index_url

    @property
    def extra_index_urls(self):
        return self._extra_index_urls


def _parse_version(version_str):
    def int_or_str(s):
        try:
            return int(s)
        except ValueError:
            return s

    major, minor, patch = None, None, None
    parts = version_str.split('.', 3)
    if len(parts) > 0:
        major = int_or_str(parts[0])
    if len(parts) > 1:
        minor = int_or_str(parts[1])
    if len(parts) > 2:
        patch = int_or_str(parts[2])

    return Version(major, minor, patch)


def parse_result(line):
    try:
        name, info = line.strip().split(' ', 1)
        _, installed_version, _, remote_version = info[1:-1].split(' ')[:4]
        return OutdatedRequirement(name, installed_version, remote_version)
    except ValueError:
        return None


def get_ignored_requirements(ignore_file):
    if not os.path.exists(ignore_file):
        return set()

    with open(ignore_file) as f:
        return set(map(str.strip, f.readlines()))
