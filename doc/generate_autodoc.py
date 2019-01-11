#!/usr/bin/env python3

"""
This script generates simple Sphinx autodoc directives for given modules.
"""

import os
from os.path import join
from typing import List, Iterable

AUTO_MODULE_TEMPLATE = '''

.. automodule:: {module}
    :members:
    :undoc-members:
    :show-inheritance:
'''


def list_modules(root_dir: str, packages: Iterable[str]) -> List[str]:
    """
    Create a sorted list of modules and submodules.

    :param root_dir: The root directory where to look for packages.
    :param packages: The packages to look for.
    :return: Sorted list of packages and their submodules.
    """
    modules = []
    for package in packages:
        for root, _dirs, files in os.walk(join(root_dir, package)):
            for file in files:
                if file == '__init__.py':
                    path = root
                elif file.endswith('.py'):
                    path = join(root, file[:-3])
                else:
                    continue
                modules.append(path[len(root_dir) + 1:].replace('/', '.'))
    modules.sort()
    return modules


def generate_auto_doc(modules: List[str]) -> str:
    """
    Generate simple Sphinx autodoc directives for given modules.

    Tests submodules are ignored.

    :param modules: The modules to document.
    :return: The autodoc Sphinx directives.
    """
    output = []
    prev_module = None
    for module in reversed(modules):
        if module.endswith('.tests') or '.tests.' in module:
            continue
        if prev_module and prev_module.startswith(module + '.'):
            heading = f'\n{module} package\n'
        else:
            heading = f'\n{module} module\n'
        output.append(AUTO_MODULE_TEMPLATE.format(module=module))
        output.append(('-' if '.' in module else '=') * (len(heading) - 2))
        output.append(heading)
        prev_module = module
    output.reverse()
    return ''.join(output)


def main(root: str, packages: List[str]) -> None:
    """
    Generate simple Sphinx autodoc directives for given modules and print them
    to the standard output.

    :param root: The root directory where to look for packages.
    :param packages: The packages to look for.
    """

    modules = list_modules(root, packages)
    output = generate_auto_doc(modules)
    print(output)


if __name__ == '__main__':
    import clizy
    clizy.run(main)
