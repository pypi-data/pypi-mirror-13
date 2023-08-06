# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

_package_data = dict(
    full_package_name="ruamel.dcw",
    version_info=(0, 1, 1),
    author="Anthon van der Neut",
    author_email="a.van.der.neut@ruamel.eu",
    description="docker-compose wrapper allowing for user data and env. var defaults",
    # keywords="",
    entry_points='dcw=ruamel.dcw.__init__:main',
    # entry_points=None,
    license="MIT",
    since=2016,
    # status: "α|β|stable",  # the package status on PyPI
    # data_files="",
    universal=True,
    install_requires=dict(
        any=["docker-compose>=1.6.0", "ruamel.yaml", "ruamel.std.pathlib",
             "ruamel.showoutput"],
        # py27=["ruamel.ordereddict"],
    ),
)


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

version_info = _package_data['version_info']
__version__ = _convert_version(version_info)

del _convert_version

import sys                                   # NOQA
import os                                    # NOQA
import ruamel.yaml                           # NOQA
from ruamel.std.pathlib import Path          # NOQA
from ruamel.showoutput import show_output    # NOQA


class DockerComposeWrapper(object):
    def __init__(self):
        self._args = None
        self._file_name = None
        self._data = None
        for p in sys.path:
            pp = os.path.join(p, 'docker-compose')
            if os.path.exists(pp):
                self._dc = pp
                break
        else:
            print('docker-compose not found in path')
            sys.exit(1)

    def process_args(self, args):
        if (len(args) > 1) and args[0] in ['-f', '--file']:
            self._file_name = Path(args[1])
            self._args = args[2:]
        elif (len(args) > 0) and (args[0].startswith('--file=') or args[0].startswith('-f=')):
            self._file_name = Path(args[0].split('=', 1)[1])
            self._args = args[1:]
        else:
            self._file_name = Path('docker-compose.yml')
            self._args = args

    def load_yaml(self):
        with self._file_name.open() as fp:
            self._data = ruamel.yaml.load(fp, Loader=ruamel.yaml.RoundTripLoader)

    def set_os_env_defaults(self):
        envs = self._data.get('user-data', {}).get('env-defaults', {})
        for k in envs:
            if k in os.environ:
                continue
            os.environ[k] = str(envs[k])  # str for those pesky port numbers

    def write_temp_file_call_docker_compose(self):
        odata = ruamel.yaml.comments.CommentedMap()
        for k in self._data:
            try:
                if k == 'user-data' or k.startswith('user-data-'):
                    continue
            except TypeError:
                pass
            odata[k] = self._data[k]
        cmd = [self._dc, '--file=-'] + self._args
        print('cmd:', ' '.join(cmd))
        show_output(cmd, input=ruamel.yaml.dump(odata,
                                                Dumper=ruamel.yaml.RoundTripDumper,
                                                allow_unicode=True, encoding='utf-8'),
                    )


def main():
    dcw = DockerComposeWrapper()
    dcw.process_args(sys.argv[1:])
    dcw.load_yaml()
    dcw.set_os_env_defaults()
    dcw.write_temp_file_call_docker_compose()

if __name__ == "__main__":
    main()
