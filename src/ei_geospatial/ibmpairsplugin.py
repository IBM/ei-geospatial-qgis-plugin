# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : IBM Geospatial APIs QGIS Plugin
Description          : This plugin allows to perform queries on an Geospatial 
                       APIs endpoint.
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
"""

# Import necessary libraries and modules
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
try:
    from qgis.PyQt.QtWidgets import *  # Compatibility with different PyQt versions
except:
    pass
from qgis.core import *
import json
import inspect
import os
import ibmpairs.query as query
import ibmpairs.catalog as catalog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from osgeo import gdal
from pathlib import Path

# Import the code for the dialog windows
from .ibmpairsdialog import IBMPairsDialog
from .login_dialog import LoginDialog

MESSAGE_CATEGORY = 'ei-geospatial-apis'

class IBMPairsConnector(object):
    def __init__(self, iface):
        """Constructor of the class. Initializes the plugin with the QGIS interface."""
        self.iface = iface  # Reference to the QGIS interface
        self.canvas = iface.mapCanvas()
        self.first_start = None  # Helper variable to check if the plugin is being started for the first time

    def initGui(self):
        """Initializes the GUI elements of the plugin."""
        # Path to the plugin's icon
        current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # Create an action that will open the main window of the plugin when triggered
        self.action = QAction(QIcon(os.path.join(current_directory, "icons", "ibm.png")),
                              "IBM Environmental Intelligence: Geospatial APIs", self.iface.mainWindow())
        self.action.triggered.connect(self.ibmpairs)
        # Add the action to the toolbar and menu
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("IBM Environmental Intelligence: Geospatial APIs", self.action)
        self.first_start = True

    def unload(self):
        """Removes the plugin from QGIS (cleanup function)."""
        self.iface.removePluginMenu("IBM Environmental Intelligence: Geospatial APIs", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Main method of the plugin. Gets called when the plugin is executed."""
        # Check if the plugin is being started for the first time and initialize the dialog window
        if self.first_start:
            self.first_start = False
            self.dlg = LoginDialog(iface=self.iface, ibmpairs=self)
            # Set the logo in the login dialog
            self.dlg.logo.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), 'icons/icon.png')))
            self.dlg.logo.setFixedSize(80,80)
            self.pw_hidden = True
            self.dlg.eyeball.clicked.connect(self.handlepwButton)
            self.dlg.eyeball.setIcon(QIcon(os.path.join(os.path.dirname(__file__),'icons/hide.png')))
            self.dlg.eyeball.setIconSize(QSize(20,20))
        # Display the login dialog
        self.dlg.show()
        # Process the result of the dialog
        result = self.dlg.exec_()
        if result:
            # Process the input if the dialog was closed successfully
            self.processInput()
    
    def download_task(self, task, ibmpairs_query):
        
        QgsMessageLog.logMessage('{} started task query.check_status_and_download()'.format(str(ibmpairs_query.id)), MESSAGE_CATEGORY, Qgis.Info)
        
        incomplete = True
        
        while incomplete:
            
            if task.isCanceled():
                stopped(task)
                return None
            
            ibmpairs_query.status()
            
            QgsMessageLog.logMessage('{} status is {}'.format(str(ibmpairs_query.id), str(ibmpairs_query.status_response.status_code)), MESSAGE_CATEGORY, Qgis.Info)
            
            if ibmpairs_query.status_response.status_code == 20:
                ibmpairs_query.download()
                QgsMessageLog.logMessage('{} successfully completed download'.format(str(ibmpairs_query.id)), MESSAGE_CATEGORY, Qgis.Info)
                incomplete = False
            elif ibmpairs_query.status_response.status_code in [0, 1, 10, 11, 12]:
                incomplete = True
                QgsMessageLog.logMessage('{} query is still running'.format(str(ibmpairs_query.id)), MESSAGE_CATEGORY, Qgis.Info)
            else:
                incomplete = False
                raise Exception('{} failed'.format(str(ibmpairs_query.id)))
                
        return ibmpairs_query
    
    def download_completed(self, exception, result=None):

        if exception is None:
            if result is None:
                QgsMessageLog.logMessage(
                    'Completed with no exception and no result (probably manually canceled by the user)', MESSAGE_CATEGORY, Qgis.Warning)
            else:
                files = result.list_files()
                result_files = []
                if True:
                    for f in files:
                        if f.endswith('.tiff') and not f.endswith('.tiff.json'):
                            result_files.append(f)
                print(result_files)
                for file in result_files:
                    self.import_file(file)
                    
                self.canvas.refresh()

                QgsMessageLog.logMessage('Successfully refreshed QGIS canvas', MESSAGE_CATEGORY, Qgis.Info)
        else:
            QgsMessageLog.logMessage("Exception: {}, {}".format(exception, result), MESSAGE_CATEGORY, Qgis.Critical)
            raise exception

    def processInput(self):
        """Processes the user input from the main dialog of the plugin."""
        input_str = str(self.dlg.wkt.toPlainText())
        start_index = input_str.find('{')

        if start_index != -1:  # Ensure start_index is found
            json_text = input_str[start_index:]

            try:
                raster_query = json.loads(json_text.replace("False", "false").replace("True", "true"))
                print("JSON:", raster_query)
            except json.JSONDecodeError as e:
                message = self.constraintMessage(str(e))
                QMessageBox.information(self.iface.mainWindow(), \
                QCoreApplication.translate('IBMPairsConnector', "IBM Geospatial APIs plugin error"), \
                QCoreApplication.translate('IBMPairsConnector', "There was an error while loading the JSON:<br /><strong>{0}</strong>").format(message))

        else:
            QMessageBox.information(self.iface.mainWindow(), \
            QCoreApplication.translate('IBMPairsConnector', "IBM Geospatial APIs plugin error"), \
            QCoreApplication.translate('IBMPairsConnector', "Error: JSON data not found in the input string."))

        #download and save the query, if its available
        DOWNLOAD_FOLDER = self.dlg.outputfolder.filePath()
        my_query = query.Query.from_json(raster_query)
        
        if ((my_query.spatial is not None) and (my_query.spatial.type is not None)):
            if my_query.spatial.type.lower() in ['point']:
                msg = "In the alpha version of the plugin point queries are not executable; please refactor the query as a raster query."
                QgsMessageLog.logMessage(msg, MESSAGE_CATEGORY, Qgis.Critical)
                QCoreApplication.translate('IBMPairsConnector', msg)
                
                return
        
        my_query.set_download_folder(DOWNLOAD_FOLDER)
        
        my_query.submit()
        
        QgsMessageLog.logMessage('{} Query Submitted'.format(my_query.id), MESSAGE_CATEGORY, Qgis.Info)
            
        QgsMessageLog.logMessage('{} Query Checking Status and Downloading'.format(my_query.id), MESSAGE_CATEGORY, Qgis.Info)
        
        globals()[my_query.id] = QgsTask.fromFunction('ei geospatial apis: {}'.format(my_query.id), self.download_task, on_finished=self.download_completed, ibmpairs_query=my_query)

        QgsApplication.taskManager().addTask(globals()[my_query.id])
        
        QgsMessageLog.logMessage('{} QgsTask Started'.format(my_query.id), MESSAGE_CATEGORY, Qgis.Info)

        return

    def login(self):
        """
        Logs the user into the backend and starts the main IBM Geospatial APIs dialog, also closes the login dialog.
        Attempts to authenticate the user with the provided credentials. If successful, the main plugin dialog is displayed.
        """
        authentication = self.dlg.connect()  # Attempt to authenticate with the backend

        if not authentication:
            # Authentication failed; return without opening the main dialog
            return
        
        self.dlg.catalog()

        # Close the login dialog and open the main plugin dialog
        self.dlg.close()
        self.dlg = IBMPairsDialog()
        # Setup actions for dialog buttons
        self.dlg.clearButton.clicked.connect(self.clearButtonClicked)
        # Display the main dialog
        self.dlg.show()
        result = self.dlg.exec_()
        # Process the input if the dialog was closed with the OK action
        if result:
            self.processInput()

    # Toggle Key fields to be visible
    def handlepwButton(self):
        if self.pw_hidden:
            self.pw_hidden = False
            self.dlg.eyeball.setIcon(QIcon(os.path.join(os.path.dirname(__file__),'icons/show.png')))
            self.dlg.eyeball.setIconSize(QSize(20,20))
            self.dlg.apiEdit.setEchoMode(QLineEdit.Normal)
            self.dlg.tenantEdit.setEchoMode(QLineEdit.Normal)
            self.dlg.orgEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_hidden = True
            self.dlg.eyeball.setIcon(QIcon(os.path.join(os.path.dirname(__file__),'icons/hide.png')))
            self.dlg.eyeball.setIconSize(QSize(20,20))
            self.dlg.apiEdit.setEchoMode(QLineEdit.Password)
            self.dlg.tenantEdit.setEchoMode(QLineEdit.Password)
            self.dlg.orgEdit.setEchoMode(QLineEdit.Password)

    def clearButtonClicked(self):
        """
        Clears the input field in the main dialog when the clear button is clicked.
        """
        self.dlg.wkt.setPlainText('')


    def ibmpairs(self):
        """
        Entry point for the plugin action. It displays the dialog to the user.
        """
        self.run()

    def import_file(self, file):
        """
        Imports a raster file into the QGIS project.

        Args:
            file (str): The file path of the raster file to be imported.
        """
        # Create a QgsRasterLayer from the provided file path
        layer = QgsRasterLayer(file, os.path.basename(file)[:-5])
        if not layer.isValid():
            QgsMessageLog.logMessage('{} layer failed to load'.format(file), MESSAGE_CATEGORY, Qgis.Error)
            return

        # Add the layer to the QGIS project
        QgsProject.instance().addMapLayer(layer)
        
        # Optionally, apply styling and rendering settings to the layer

        file_no_ext = Path(file).stem
        output_info = Path('{}/output.info'.format(Path(file).parent))
        
        dl_id = None

        # Determine data layer id of the file
        if output_info.is_file():
            with open(output_info) as f:
                try:
                    output_info_json = json.load(f)
                    for tiff in output_info_json['files']:
                        if tiff['name'] == file_no_ext:
                            dl_id = tiff['datalayerId']
                except:
                    QgsMessageLog.logMessage('{} the data layer id could not be found'.format(file), MESSAGE_CATEGORY, Qgis.Error)

        spectrum = None
        
        if dl_id is not None:
            try:
                dl = catalog.get_data_layer(dl_id)
                if dl.color_table != None:
                    if dl.color_table.colors != None:
                        spectrum = dl.color_table.colors.split(',')
                        spectrum = ['#'+item for item in spectrum]
            except:
                QgsMessageLog.logMessage('{} the spectrum could not be found for the layer {}'.format(file, dl_id), MESSAGE_CATEGORY, Qgis.Warn)

        if spectrum is not None:
            QgsMessageLog.logMessage('{} the spectrum {} will be applied'.format(file, str(spectrum)), MESSAGE_CATEGORY, Qgis.Info)
            self.applyStylingToLayer(layer = layer, spectrum = spectrum)
        else:
            self.applyStylingToLayer(layer)

        '''
        self.applyStylingToLayer(layer)
        '''

        QgsMessageLog.logMessage('{} layer loaded'.format(file), MESSAGE_CATEGORY, Qgis.Info)

    def applyStylingToLayer(self, 
                            layer, 
                            band=1,
                            #spectrum=['Cyan', 'Green', 'Yellow', 'Orange', 'Red']):
                            spectrum=['#153A91','#84F588','#FFF787','#FF7C3B','#FF1921'],
                            opacity = 0.6):
        """
        Applies styling to the raster layer based on the specified band and color spectrum.

        Args:
            layer (QgsRasterLayer): The raster layer to style.
            band (int): The band of the raster to use for styling.
            spectrum (list): A list of colors to use for the styling.
        """
        # Obtain the data provider and GDAL dataset for the layer
        prov = layer.dataProvider()
        src_ds = gdal.Open(layer.source())
        src_band = src_ds.GetRasterBand(band)

        # Compute statistics if not already present
        if src_band.GetMinimum() is None or src_band.GetMaximum() is None:
            src_band.ComputeStatistics(0)
        band_min, band_max = src_band.GetMinimum(), src_band.GetMaximum()

        # Prepare the color ramp shader
        band_range = band_max - band_min
        class_range = band_range / len(spectrum)
        fcn = QgsColorRampShader()
        fcn.setColorRampType(QgsColorRampShader.Interpolated)
        item_list = []

        # Create color ramp items based on the spectrum
        for n in range(len(spectrum)):
            band_min += class_range
            list_item = QgsColorRampShader.ColorRampItem(band_min, QColor(spectrum[n]), lbl='{0:.2f}-{1:.2f}'.format(band_min-class_range, band_min))
            item_list.append(list_item)
        fcn.setColorRampItemList(item_list)

        # Apply the color ramp to the layer
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fcn)
        renderer = QgsSingleBandPseudoColorRenderer(prov, band, shader)
        layer.setRenderer(renderer)
        layer.setOpacity(opacity)  # Set layer opacity
        layer.triggerRepaint()

    def constraintMessage(self, message):
        """
        Returns a shortened version of a message if it exceeds a certain length.

        Args:
            message (str): The message to possibly shorten.

        Returns:
            str: The original or shortened message.
        """
        if len(message) > 128:
            return message[:64] + ' [ .... ] ' + message[-64:]
        return message


if __name__ == "__main__":
    pass
    