********
PyZureML
********

| Python wrapper for the Microsoft Azure Machine Learning webservice endpoint API.
| Programmatically create, delete, get and update endpoints for any Azure Machine Learning webservice.

Download
--------

Option 1: Download from PyPi
~~~~~~~~~~~~~~~~~~

To install via the Python Package Index (PyPI), type:

.. code-block:: python

    pip install PyZureML

Option 2: Clone via Git
~~~~~~~~~~~~~~~~~~~~~~~~

To get the source code via Git just type:

.. code-block:: python

    git clone git://github.com/marcardioid/PyZureML.git
    cd ./PyZureML
    python setup.py install

Option 3: Source Zip
~~~~~~~~~~~~~~~~~~~~

Download a zip of the code via GitHub or PyPi. Then, type:

.. code-block:: python

    cd ./PyZureML
    python setup.py install

Requirements
--------------------

-  Python 3.x
-  Requests

Usage
-----

.. code-block:: python

    from PyZureML import endpoints
    endpoints.create_endpoint(<locale>, <workspace_id>, <api_token>, <webservice_id>, <endpoint_name>, <description>)
    endpoints.delete_endpoint(<locale>, <workspace_id>, <api_token>, <webservice_id>, <endpoint_name>)


