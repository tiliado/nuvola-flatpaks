"""
This module contains various constants, mainly those from flatpak-builder's
manifest files (see `man flatpak-manifest` for more information).
"""

#: The branch of the application, defaults to master.
MANIFEST_BRANCH = 'branch'

#: The default value of :data:`MANIFEST_BRANCH`.
MANIFEST_BRANCH_DEFAULT = 'master'

#: A string defining the application id.
MANIFEST_ID = 'id'

#: A string defining the application id.
MANIFEST_APP_ID = 'app-id'

#: An array of objects specifying the modules to be built in order.
MANIFEST_MODULES = 'modules'

#: The name of the module, used in e.g. build logs.
MODULE_NAME = 'name'
