# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import sys

from ruamel.std.pathlib import Path
from ruamel.yaml.compat import ordereddict


class VirtualEnvUtils(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config

    def alias(self):
        aliases = ordereddict()
        venv_dirs = []
        for d in self._args.dir:
            d = Path(d).expanduser()
            for sub_dir in d.glob('*'):
                if not sub_dir.is_dir():
                    continue
                for x in ('bin', 'lib', 'include'):
                    sub_sub_dir = sub_dir / x
                    if not sub_sub_dir.exists():
                        break
                    if not sub_sub_dir.is_dir():
                        break
                else:
                    activate = sub_dir / 'bin' / 'activate'
                    if activate.exists() and activate.is_file():
                        venv_dirs.append(sub_dir)
        for d in venv_dirs[:]:
            # check for configuration file
            conf = d / 'virtualenvutils.conf'
            if not conf.exists():
                continue
            venv_dirs.remove(d)
            # print('conf file', d, file=sys.stderr)
            for line in conf.read_text().splitlines():
                # print('line', line, file=sys.stderr)
                if u':' in line:
                    util, full = line.strip().split(u":", 1)
                    full = d / 'bin' / full
                else:
                    util = line.strip()
                    full = d / 'bin' / util
                if not full.exists():
                    print('cannot find {}\n  from line {}\  in {}'.format(
                        full, line, conf), file=sys.stderr)
                if util in aliases:
                    print('virtualenvutils name clashes {}\n  {}\n  {}'.format(
                        util,
                        util,
                        aliases[util],
                        ), file=sys.stderr)
                else:
                    aliases[util] = full
        for d in venv_dirs[:]:
            util = d / 'bin' / (d.stem)
            if not util.exists():
                continue
            venv_dirs.remove(d)
            # print('matching virtualenv name', d, file=sys.stderr)
            if util.name in aliases:
                print('virtualenvutils name clashes {}\n  {}\n  {}'.format(
                    util.name,
                    util,
                    aliases[util.name],
                    ), file=sys.stderr)
            else:
                aliases[util.stem] = util
        for d in venv_dirs[:]:
            for util in (d / 'bin').glob('*'):
                if not util.is_file():
                    continue
                for skip in ['activate', 'easy_install', 'python', 'pip', 'wheel']:
                    if util.stem.startswith(skip):
                        break
                else:
                    if d in venv_dirs:  # only first time
                        venv_dirs.remove(d)
                    if util.name.endswith('.so'):
                        continue
                    if util.name.endswith('.pyc'):
                        continue
                    if util.name.endswith('.py'):
                        # can make xyz.py into util xyz, or skip. Yeah, skip
                        continue
                    if util.name in aliases:
                        if self._args.verbose > 0:
                            print('skipping name clashes {}\n  {}\nin favor of\n  {}'.format(
                                util.name,
                                util,
                                aliases[util.name],
                                ), file=sys.stderr)
                    else:
                        aliases[util.name] = util
        assert not venv_dirs
        for k in aliases:
            print("alias {}='{}'".format(k, aliases[k]))
