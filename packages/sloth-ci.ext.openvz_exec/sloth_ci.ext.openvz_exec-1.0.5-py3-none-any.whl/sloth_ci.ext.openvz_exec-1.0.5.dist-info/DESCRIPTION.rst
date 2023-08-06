Run actions inside an `OpenVZ <http://openvz.org>`__ container.

By default, Sloth CI apps run actions in a subprocess on the same machine they're running on. This extension overrides this and makes the app execute actions inside a given OpenVZ container.


Installation
------------

.. code-block:: bash

    $ pip install sloth-ci.ext.openvz_exec


Usage
-----

.. code-block:: yaml
    :caption: openvz_exec.yml

    extensions:
        run_in_openvz:
            # Use the sloth_ci.ext.openvz_exec module.
            module: openvz_exec

            # Container name.
            container_name: foo

            # Container ID.
            # container_id: 123

If ``container_name`` is provided, ``container_id`` is ignored. If ``container_name`` is *not* provided, ``container_id`` is mandatory.


