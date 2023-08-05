cctm
========================================

CCTM = cookie cutter template manager

project templates manager for `cookiecutter <https://github.com/audreyr/cookiecutter>`_

(python3 only)


quick examples
----------------------------------------

.. code-block:: bash

 $ cctm init
 $ cctm selfupdate
 $ cctm install audreyr/cookiecutter-pypackage
 $ cctm use audreyr/cookiecutter-pypackage

 # alias
 $ cctm management alias audreyr/cookiecutter-pypackage pypackage
 $ cctm use pypackage

 # extra_context configuration
 $ cctm config --name=full_name --value=podhmo.podhmo
 $ cctm use pypackage

setup
----------------------------------------

.. code-block:: bash

  $ pip install cctm

cctm uses individual configuration file(cctm.json).

searching cctm.json
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

searching method is here.

first, from current working directory, searching "cctm.json" file, recuresively.

e.g. if cwd is `~/foo/bar/boo`. searching below paths.

#. ~/foo/bar/boo/cctm.json
#. ~/foo/bar/cctm.json
#. ~/foo/cctm.json
#. ~/cctm.json

second, if cctm.json is not found on first process, then, using `~/.cctm/cctm.json` (default path)

generating configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

generating configuration file via `cctm init`.

.. code-block:: bash

  $ cctm init

  # if generating configuration file as current working directory
  $ cctm init --project=.

package information
----------------------------------------

listing package information via `cctm list`

.. code-block:: bash

  $ cctm list | grep pypackage
  kragniz/cookiecutter-pypackage-minimal(12) -- A minimal template for python packages
  audreyr/cookiecutter-pypackage(555) -- Cookiecutter template for a Python package.
  pypackage -> audreyr/cookiecutter-pypackage  # this is alias

show detail via `cctm show`

.. code-block:: bash

  $ cctm show audreyr/cookiecutter-pypackage
  {
    "updated_at": "2016-01-08T22:53:23Z",
    "url": "https://github.com/audreyr/cookiecutter-pypackage",
    "name": "audreyr/cookiecutter-pypackage",
    "description": "Cookiecutter template for a Python package.",
    "star": 555,
    "created_at": "2013-07-14T18:52:05Z"
  }

using cookiecutter
----------------------------------------

installing cookiecutter template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

installing the template via `cctm install`

.. code-block:: bash

  $ cctm install chrisdev/wagtail-cookiecutter-foundation

  # wagtail-cookiecutter-foundation is installed
  $ cctm list --installed
  audreyr/cookiecutter-pypackage
  chrisdev/wagtail-cookiecutter-foundation

using cookiecutter template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

using installed template via `cctm use`

.. code-block:: bash

  $ cctm use chrisdev/wagtail-cookiecutter-foundation

if you are irritated by long-long-name, `cctm management alias` is helpful, maybe.

.. code-block:: bash

  $ cctm management alias chrisdev/wagtail-cookiecutter-foundation mywagtail
  $ cctm list --alias | grep wagtail
  mywagtail -> chrisdev/wagtail-cookiecutter-foundation
  $ cctm use mywagtail  # it's is also ok.

default configuration settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

if you want to set a default context, using `cctm config`

.. code-block:: bash

  # show configuration
  $ cctm config | jq .extra_context
  {
    "name": "podhmo",
  }
  # edit configuration
  $ cctm config --name=project_name --value=hello
  # delete configuration
  $ cctm config --name=project_name

extra_context attribute in config file is using as cookiecutter's extra context, so.

.. code-block:: bash

  $ cctm use mywagtail
  project_name [Wagtail Project]:  # cancel

  $ cctm config --name=project_name --value=hello
  $ cctm use mywagtail
  project_name [hello]:

your custom repositories
----------------------------------------

if you store url in `repositories` of configration file, cctm recognizes as package repositoriy.

default reposotiries are here. ::

  "repositories": [
    "https://raw.githubusercontent.com/podhmo/cctm/master/data/cookiecutter.index.json"
  ]

package format example ::

  {
    "name": "chrisdev/wagtail-cookiecutter-foundation",
    "url": "https://github.com/chrisdev/wagtail-cookiecutter-foundation",
    "description": "Cookiecutter template for Wagtail CMS using Zurb Foundation 5",
    "created_at": "2015-04-13T13:36:50Z",
    "updated_at": "2016-01-04T14:53:04Z",
    "star": 23
  }

if you know, github url, be able to fetch information via `cctm management fetch`

.. code-block:: bash

  $ cctm management fetch chrisdev/wagtail-cookiecutter-foundation
  {
    "name": "chrisdev/wagtail-cookiecutter-foundation",
    "url": "https://github.com/chrisdev/wagtail-cookiecutter-foundation",
    "description": "Cookiecutter template for Wagtail CMS using Zurb Foundation 5",
    "created_at": "2015-04-13T13:36:50Z",
    "updated_at": "2016-01-04T14:53:04Z",
    "star": 23
  }

  # store data at local.json
  $ cctm management fetch chrisdev/wagtail-cookiecutter-foundation --save --store=./local.json

please, don't forget to call `cctm selfupdate`. this command synchnonizes at local data and repositoriies data.

.. code-block:: bash

  $ cctm selfupdate
