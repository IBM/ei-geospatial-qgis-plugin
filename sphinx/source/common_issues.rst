.. _common_issues:

Common Issues
=============

Mac (OSX)
---------

Keychain
********

If you encounter the following error messages:

.. error::
    2024-07-22T13:47:05     CRITICAL    Authentication Manager : Retrieving password from your Keychain failed: OS X Keychain error (OSStatus -25293).
    2024-07-22T13:47:11     CRITICAL    Authentication Manager : Storing password in your Keychain failed: OS X Keychain
    2024-07-22T13:47:11     WARNING    Authentication Manager : Master password could not be written to your Keychain

This is a general QGIS issue, please follow the guidance in `issue 46175 <https://github.com/qgis/QGIS/issues/46175#issuecomment-1144289096>`_. 

bottleneck
**********

A pre-requisite package of this Plugin ``ibmpairs`` has a transitive dependency chain: ``ibmpairs`` -> ``jsonschema`` -> ``bottleneck``. As of bottleneck 1.4.0 the wheel builds for [arm64](https://github.com/pydata/bottleneck/pull/427) systems (e.g. M1, M2, M3 chipsets) are broken. For this reason the version of bottleneck is pinned to 1.3.8 to prevent the error when attempting to ``make install``:

.. error::
    Could not build wheels for bottleneck which use PEP 517 and cannot be installed directly

numpy
*****

A pre-requisite package of this Plugin ``ibmpairs`` has a non-version pinned transitive dependency on ``numpy``, by default this will install 2.x (as of 2024-06-16). "A module that was compiled using NumPy 1.x cannot be run in NumPy 2.0.0 as it may crash. To support both 1.x and 2.x versions of NumPy, modules must be compiled with NumPy 2.0."; as there are prerequisites of QGIS compiled with numpy 1.x the version is pinned to 1.26.4 to avoid the following error when opening QGIS:

.. error::
    AttributeError: _ARRAY_API not found 
    
Windows
-------

aiohttp
*******

A pre-requisite package of this Plugin ``ibmpairs`` has a non-version pinned transitive dependency on ``aiohttp``, by default this will install 3.10.x (as of 2024-06-16). The recommended version for Windows under later versions of Python is 3.9.5 for this reason the version is pinned in the requirements.txt. 3.10.x versions cause the following error at present:

.. error::
    aiodns needs a SelectorEventLoop on Windows. See more: https://github.com/saghul/aiodns/issues/86
