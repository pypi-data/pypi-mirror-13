yamlfred
========

|version| |license|_ |pypi_version| |python_versions| |circle-ci|_ |codeclimate|_

The `Alfred Workflows`_ management tool with a *divide and rule* manner.

Alfred Workflows contains README and scripts in single ``info.plist``,
and it's hard to maintain by common development methods,
edit script with your favorite editor or track script changes with VCS.

``yamlfred`` translate ``info.plist`` and generates files,
simplified configuration, called ``workflow.yml``, scripts and README.

This enable us to edit each script files or track changes with VCS.

In addition, yamlfred has abilities to extract or create Alfred workflow,
translate a ``workflow.yml`` into an ``info.plist`` and vice a versa.

Installation
------------

To install yamlfred, use pip install::

  $ pip install yamlfred

For the case of uninstall, use pip uninstall yamlfred::

  $ pip uninstall yamlfred

Usage
-----

- Extract existing Alfred workflow::

     $ yamlfred extract {{workflow}}.alfredworkflow

  Creates following ``{{workflow}}`` directory::

     {{workflow}}
     |-- ...
     |-- info.plist
     |-- ...

- convert ``info.plist`` (in current directory)
  into yaml template (``workflow.yml``) and scripts and README::

    $ yamlfred to_yaml

- convert yaml template (``workflow.yml``) into ``info.plist``::

    $ yamlfred to_plist

- create Alfred workflow (`{{workflow}}.alfredworkflow``)
  from ``workflow.yml``, scripts and README::

    $ yamlfred create {{workflow}}

Examples
--------

These Alfred workflows uses yamlfred:

- `alfred-switch-vpn <https://github.com/uchida/alfred-switch-vpn>`_
- `alfred-switch-bluetooth <https://github.com/uchida/alfred-switch-bluetooth>`_
- `alfred-switch-audio <https://github.com/uchida/alfred-switch-audio>`_

On can upload github release page via CI services, such as `Circle CI <https://circleci.com/>`_
with `hub <https://github.com/github/hub/>`_ command and `GITHUB_TOKEN`
consult `circle.yml` in these repositories for detailed information.

License
-------

CC0_ dedeicated to |CC0_publicdomain|, no rights reserved.

.. |version| image:: https://img.shields.io/github/tag/uchida/yamlfred.svg
.. |license| image:: https://img.shields.io/github/license/uchida/yamlfred.svg
.. |circle-ci| image:: https://img.shields.io/circleci/project/uchida/yamlfred.svg
.. |CC0_publicdomain| image:: http://i.creativecommons.org/p/zero/1.0/80x15.png
.. |pypi_version| image:: https://img.shields.io/pypi/v/yamlfred.svg
.. |python_versions| image:: https://img.shields.io/pypi/pyversions/yamlfred.svg
.. |codeclimate| image:: https://img.shields.io/codeclimate/github/uchida/yamlfred.svg

.. _Alfred Workflows: http://support.alfredapp.com/workflows
.. _license: https://tldrlegal.com/license/creative-commons-cc0-1.0-universal
.. _CC0: http://creativecommons.org/publicdomain/zero/1.0/
.. _circle-ci: https://circleci.com/gh/uchida/yamlfred
.. _codeclimate: https://codeclimate.com/github/uchida/yamlfred

