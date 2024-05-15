# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ShohanJump
                                 A QGIS plugin
 This plugin show specific Shohan (Areas of segmented forests in Japanese).
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-02-01
        copyright            : (C) 2024 by Takeru Sanda
        email                : takeru_sanda999@maff.go.jp
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ShohanJump class from file ShohanJump.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .shohan_jump import ShohanJump
    return ShohanJump(iface)
