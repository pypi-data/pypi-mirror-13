===============================
Plumbery
===============================

.. image:: https://img.shields.io/pypi/v/plumbery.svg
        :target: https://pypi.python.org/pypi/plumbery

.. image:: https://img.shields.io/travis/bernard357/plumbery.svg
        :target: https://travis-ci.org/bernard357/plumbery

.. image:: https://readthedocs.org/projects/plumbery/badge/?version=latest
        :target: https://readthedocs.org/projects/plumbery/?badge=latest
        :alt: Documentation Status


Infrastructure as code at Dimension Data with Apache Libcloud

* Documentation: `Plumbery at ReadTheDocs`_
* Python package: `Plumbery at PiPy`_
* Source code: `Plumbery at GitHub`_
* Free software: `Apache License (2.0)`_

Features
--------

* Read fittings plan in YAML
* Use cloud API to create the network infrastructure, and to build nodes
* Bootstrap nodes with cloud-init configuration directives
* Inject actual addresses and on-the-fly secrets to contextualisation
* Preserve random secrets across multiple invocations
* Create network domains and Ethernet networks
* Reserve public IPv4 addresses
* Manage network address translation rules
* Manage firewall rules
* Create load balancers with pools of nodes
* All images in libraries are available to new nodes
* Specify number of CPU, or core per CPU, and CPU speed
* Specify node memory
* Add multiple network interfaces to nodes
* Add public IPv4 addresses to nodes
* Add monitoring to nodes
* Build all blueprints
* Build a blueprint across multiple locations
* Start all nodes
* Start nodes belonging to the same blueprint
* Polish Linux nodes for quick bootstrapping
* Build a full inventory of nodes that have been deployed
* Reflect fittings into a ready-to-use inventory for ansible
* Stop all nodes
* Stop nodes belonging to the same blueprint
* Destroy all nodes
* Destroy nodes belonging to the same blueprint
* Many demonstration scripts are provided
* You can extend plumbery with your own polishers, it has been designed for that
* Run from the command line, or as a python library
* Accept custom polisher from the command line too
* Limit plumbing to some locations if needed

Contributors
------------

* `Bernard Paques`_ [Dimension Data employee] (development lead)
* `Anthony Shaw`_ [Dimension Data employee]
* Olivier Grosjeanne [Dimension Data employee]

Credits
-------

*  `Apache Libcloud`_
*  netifaces_
*  PyYAML_
*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _`Plumbery at ReadTheDocs`: https://plumbery.readthedocs.org
.. _`Plumbery at PiPy`: https://pypi.python.org/pypi/plumbery
.. _`Plumbery at GitHub`: https://github.com/bernard357/plumbery
.. _`Apache License (2.0)`: http://www.apache.org/licenses/LICENSE-2.0
.. _`Bernard Paques`: https://github.com/bernard357
.. _`Anthony Shaw`: https://github.com/tonybaloney
.. _`Apache Libcloud`: https://libcloud.apache.org/
.. _netifaces: https://pypi.python.org/pypi/netifaces
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


