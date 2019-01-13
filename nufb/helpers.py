# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains temporary helpers which are installed at the init phase
and removed at the finish phase.
"""
from typing import Optional, List


# pylint: disable=missing-type-doc
class Helper:
    """
    Temporary build helper.

    The command, source paths, install and remove commands, stage and keep
    patterns may contain `@name` which will be replaced by the helper name.

    :param name: The name of the helper.
    :param command: The command to run the helper.
    :param sources: The sources to build the helper.
    :param install: The commands to build/install the helper.
    :param stage: Stage patterns, see :attr:`Module.stage_patterns`.
    :param keep: Keep patterns, see :attr:`Module.keep_patterns`.
    :param remove: The commands to remove/uninstall the helper.
    """
    def __init__(self, name: str, *,
                 command: Optional[str] = None,
                 sources: Optional[List[dict]] = None,
                 install: Optional[List[str]] = None,
                 stage: Optional[List[str]] = None,
                 keep: Optional[List[str]] = None,
                 remove: Optional[List[str]] = None,
                 ):

        def expand(s: str) -> str:
            return s.replace('@name@', name)
        if command:
            command = expand(command)
        for lst in install, stage, keep, remove:
            if lst:
                lst[:] = (expand(s) for s in lst)
        if sources:
            for item in sources:
                try:
                    item['path'] = expand(item['path'])
                except KeyError:
                    pass

        self.name = name
        self.command = command
        self.sources = sources
        self.install = install
        self.stage = stage
        self.keep = keep
        self.remove = remove


NO_RUBBISH_SCRIPT = Helper(
    'no_rubbish.py',
    command='/app/tmp/@name@',
    sources=[{
        'type': 'file',
        'path': '@name@'
    }],
    install=['install -Dt /app/tmp @name@'],
    keep=['/app/tmp/@name@'],
    remove=['rm /app/tmp/@name@']
)
