# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ShohanJump
                                 A QGIS plugin
 This plugin show specific Shohan (Areas of segmented forests in Japanese).
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-02-01
        version              : 20240507
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Takeru Sanda
        email                : takeru_sanda999@maff.go.jp
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QAction
from qgis.utils import iface
from qgis.core import QgsVectorLayer
from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .shohan_jump_dialog import ShohanJumpDialog
import os.path


class ShohanJump:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ShohanJump_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Shohan Jump')
        self.toolbar = self.iface.addToolBar(u'ShohanJump')
        self.toolbar.setObjectName(u'ShohanJump')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ShohanJump', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            #self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Pythonファイルのディレクトリを取得
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # icon.pngのパスを作成
        icon_path = os.path.join(current_directory, "icon.png")
        #icon_path = ':/plugins/shohan_jump/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Shohan Jump'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

        self.dlg = ShohanJumpDialog()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Shohan Jump'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        def deselect_all_features():    #全てのレイヤで選択解除
            layers = QgsProject.instance().mapLayers().values()
            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer:
                    if layer.selectedFeatureCount() > 0:
                        layer.removeSelection()

        def select_features(layer, field_a, value_a, field_b, value_b, field_c, value_c):   #条件に合う地物を選択
            layer.selectByExpression(f"{field_a} = {value_a}")
            if value_b.strip():
                layer.selectByExpression(f"{field_b} LIKE '%{value_b[0]}%'", QgsVectorLayer.IntersectSelection)
                layer.selectByExpression(f"{field_c} = {value_c}", QgsVectorLayer.IntersectSelection)

        def jump_the_shohan():   
            canvas = iface.mapCanvas()
            canvas.zoomToSelected(layer)

        selected_features = 0
        comment =''

        while ( selected_features == 0 ) :
            self.dlg.show()
            result = self.dlg.exec_()
            if result:
                deselect_all_features()

                layer = self.dlg.shohankukaku.currentLayer()
                field_a = '林班主番'
                value_a = self.dlg.rinpan.value()
                field_b = '小班名'
                value_b = self.dlg.shohan.text()
                field_c = '小班枝番'
                value_c = self.dlg.shohan_edaban.value()

                select_features(layer, field_a, value_a, field_b, value_b, field_c, value_c)
                
                selected_features = layer.selectedFeatureCount()

                if selected_features:
                    jump_the_shohan()
                else:
                    comment = '小班が存在しません。'

                self.dlg.label_5.setText(comment)
                self.dlg.label_5.setStyleSheet("QLabel { color : red; }")

            else:
                break

