Nuvola Flatpak Packaging
========================

[![Install Nuvola Apps](https://img.shields.io/badge/Install-Nuvola_Apps-blue)](https://nuvola.tiliado.eu/index/)
[![Install Nuvola CDK](https://img.shields.io/badge/Install-Nuvola_CDK-yellow)](https://github.com/tiliado/nuvolaruntime/wiki/Nuvola-Core-Developer-Kit)
[![Install Nuvola ADK](https://img.shields.io/badge/Install-Nuvola_ADK-yellow)](https://github.com/tiliado/nuvolaruntime/wiki/Nuvola-App-Developer-Kit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CircleCI](https://circleci.com/gh/tiliado/nuvola-flatpaks.svg?style=shield)](https://circleci.com/gh/tiliado/nuvola-flatpaks)


Hierarchy
---------

There are several dependent layers of flatpaks:

* [eu.tiliado.NuvolaCdk.yml](./manifests/stable/eu.tiliado.NuvolaCdk.yml):
  [Nuvola Core Developer Kit](https://github.com/tiliado/nuvolaruntime/wiki/Nuvola-Core-Developer-Kit)
  contains all dependencies to build and run Nuvola. 
  * [eu.tiliado.NuvolaAdk.yml](./manifests/stable/eu.tiliado.NuvolaAdk.yml):
    [Nuvola App Developer Kit](https://github.com/tiliado/nuvolaruntime/wiki/Nuvola-App-Developer-Kit)
    contains prebuilt Nuvola and all tools needed to develop web app scripts for Nuvola.
  * [eu.tiliado.NuvolaBase.yml](./manifests/stable/eu.tiliado.NuvolaBase.yml):
    Base image with prebuilt Nuvola to build Nuvola Service and individual Nuvola apps.
    * [eu.tiliado.Nuvola.yml](./manifests/stable/eu.tiliado.Nuvola.yml):
      Nuvola Apps Service is an optional background service that provides individual Nuvola apps
      with global shared resources such as a global configuration storage, global keyboard
      shortcuts, a HTTP remote control server, and a command-line controller.
    * [eu.tiliado.NuvolaApp.yml](./manifests/stable/eu.tiliado.NuvolaApp.yml):
      Individual Nuvola apps.


Usage
-----

* Install:
```
python3 -m venv ~/.virtualenvs/flatpaks
~/.virtualenvs/flatpaks/bin/pip install -r requirements.txt
```

* Run:
```
. ~/.virtualenvs/flatpaks/bin/activate
./nufbctl --help
./nufbctl buildall --help
./nufbctl buildall experimental
./nufbctl buildall experimental,master,stable
```

Copyright
---------

Copyright 2018-2020 Jiří Janoušek <janousek.jiri@gmail.com>

Unless noted otherwise, the content of this repository is licensed under
[BSD-2-Clause](./LICENSE).
