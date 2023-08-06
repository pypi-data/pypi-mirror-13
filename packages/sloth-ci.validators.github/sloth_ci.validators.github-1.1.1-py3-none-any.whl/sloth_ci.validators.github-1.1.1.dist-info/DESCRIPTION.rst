Sloth CI validator for `GitHub <https://github.com/>`_ push events.

Installation
------------

.. code-block:: bash

    $ pip install sloth-ci.validators.github


Usage
-----

.. code-block:: yaml

    provider:
        github:
            # Repository owner. Mandatory parameter.
            owner: moigagoo

            # Repository title as it appears in the URL, i.e. slug.
            # Mandatory parameter.
            repo: sloth-ci

            # Only pushes to these branches will initiate a build.
            # Skip this parameter to allow all branches to fire builds.
            branches:
                - master
                - staging


