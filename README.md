# ei-geospatial-qgis-plugin
IBM Environmental Intelligence: Geospatial Analytics- QGIS Plugin

## Scope

The repository contains the IBM Environmental Intelligence: Geospatial Analytics- QGIS Plugin.

## Install

Please see the [Plugin documentation](https://ibm.github.io/ei-geospatial-qgis-plugin/).

## Use 

Please see the [Plugin documentation](https://ibm.github.io/ei-geospatial-qgis-plugin/).

## Common Issues 

Please see the [Plugin documentation](https://ibm.github.io/ei-geospatial-qgis-plugin/).

## Build

The project contains a [Makefile](Makefile) with the following targets:

`develop`: Installs development pre-requisites

`clean`: Cleans the repository of build artefacts

`doc`: Generates the Sphinx documentation

`pages`: Copies Sphinx docs to the docs repository to show as a set of GitHub pages (inc. doc)

`metadata`: Generates the src/ei_geospatial/metadata.txt file for the QGIS Plugin

`compile`: Compiles the resources.py from resources.qrc using pyrcc5

`package`: Packages a release zip (inc. clean doc metadata compile)

`prerequisites`: Installs zip package to environment

`install`: Installs zip package to environment (inc. prerequisites package)

The make targets execute the [packaging_cli.py](packaging_cli.py) Python script, this CLI script contains a number of methods in the `Packaging` class with equivalent names to those in the Makefile, e.g. `clean` -> `do_clean()`.
