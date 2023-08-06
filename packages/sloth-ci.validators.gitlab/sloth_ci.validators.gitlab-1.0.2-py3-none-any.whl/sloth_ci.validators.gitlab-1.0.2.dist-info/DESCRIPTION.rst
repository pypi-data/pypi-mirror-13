Sloth CI validator for `GitLab <https://about.gitlab.com/>`_ push events.

Installation
------------

.. code-block:: bash

    $ pip install sloth-ci.validators.gitlab


Usage
-----

.. code-block:: yaml

    provider:
        gitlab:
            # Whitelisted GitLab server IPs.
            # Mandatory parameter.
            trusted_ips:
                - 123.45.67.89
                - 111.22.33.44

            # Repository title as it appears in the URL, i.e. slug.
            # Mandatory parameter.
            repo: sloth-ci

            # Only pushes to these branches will initiate a build.
            # Skip this parameter to allow all branches to fire builds.
            branches:
                - master
                - staging


