.. _installation:

Installation
============

Python
------

You must have Python installed to your machine in order to execute the ``packaging_cli.py`` script.

You must also install the development requirements to build the plugin:

``python -m pip install -r requirements-development.txt``

QGIS
----

In order to use the IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin you must already have QGIS installed on your machine. Please see the QGIS `Getting Started <https://docs.qgis.org/3.34/en/docs/user_manual/introduction/getting_started.html>`_ documentation.

If you already have QGIS installed to your machine please skip this step.

Plugin
------

Mac (OSX) or Linux
******************

To package and install the plugin from the repo:-

1. Checkout the project:
``git clone git@github.com:IBM/ei-geospatial-qgis-plugin.git``

2. To install:

``make install``

3. Open QGIS and go to: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``Installed``

4. Select the checkbox next to ``IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin`` to enable the plugin.

Windows
*******

1. Checkout the project:
``git clone git@github.com:IBM/ei-geospatial-qgis-plugin.git``

2. Execute the Windows batch install file:

``install.bat``

3. Open QGIS and go to: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``Installed``

4. Select the checkbox next to ``IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin`` to enable the plugin.
