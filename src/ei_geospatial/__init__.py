# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name			 	 : IBMPairsConnector
Description          : This plugin allows to perform queries on an IBM PAIRS endpoint.
Date                 : 9/Jan/2024
copyright            : (C) 2024 by International Business Machines
email                : jannis.fleckenstein@ibm.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import os
import platform
import site
#import pkg_resources
import builtins



def classFactory(iface):
    # load GeoCoding class from file GeoCoding
    from .ibmpairsplugin import IBMPairsConnector
    return IBMPairsConnector(iface)
