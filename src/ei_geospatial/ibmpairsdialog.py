# -*- coding: utf-8 -*-
"""
***************************************************************************
Name			 	 : IBM Geospatial APIs QGIS Plugin
Description          : This plugin allows to perform queries on an IBM 
                       Geospatial APIs endpoint.
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
# Import necessary Python and PyQt5 libraries for GUI components and data manipulation
from builtins import str
from qgis.PyQt import QtCore, QtGui, QtWidgets, uic
import pandas as pd
import numpy as np
from qgis.gui import QgsFileWidget
import os
import ibmpairs.catalog as catalog
import datetime
import json
import math
import re
import time

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ibmpairsplugin.ui'))
# Define the IBMPairsDialog class, inheriting from QDialog for modal dialog capabilities
class IBMPairsDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None, iface=None, ibmpairs=None):
        # Initialize the dialog using the QDialog constructor
        # Set up the user interface from Designer by loading the UI file
        super(IBMPairsDialog, self).__init__(parent)

        QtWidgets.QApplication.setStyle("cleanlooks")
        self.ibmpairs = ibmpairs
        self.layers = []
        self.iface = iface
        self.setupUi(self)
        # Reset the input fields of the dialog
        self.wkt.setPlainText("""{
    "layers": [
        {
            "id": "put the data layer id here",
            "type": "raster"
        }
    ],
    "spatial": {
        "coordinates": [
            "put the south coordinate here",
            "put the west coordinate here",
            "put the north coordinate here",
            "put the east coordinate here"
        ],
        "type": "square"
    },
    "temporal": {
        "intervals": [
            {
                "snapshot": "YYYY-MM-DDThh:mm:ssZ"
            }
        ]
    }
}""")
        self.tree = QtWidgets.QTreeView()
        # Erstellen Sie das QgsFileWidget
        self.outputfolder = QgsFileWidget()
        self.outputfolder.setStorageMode(QgsFileWidget.GetDirectory)
        self.outputfolder.setFileWidgetButtonVisible(True)
        self.outputfolder.setDialogTitle("Output folder")
        self.outputfolder.setFilePath(os.path.join(os.path.dirname(__file__), 'download'))
        # Fügen Sie das QgsFileWidget zum Layout hinzu
        self.verticalLayout_2.addWidget(self.outputfolder)
      
        dsets_path = os.path.join(os.path.dirname(__file__),'data_sets.json')
        layer_path = os.path.join(os.path.dirname(__file__),'data_layers.json')
        
        f = open(dsets_path, "r")
        cat_dset = json.loads(f.read())
        f.close()
        
        f = open(layer_path, "r")
        cat_layers = json.loads(f.read())
        f.close()
        
        try:
           dsetl = pd.DataFrame(cat_dset["data_sets"])
           layersl = pd.DataFrame(cat_layers["data_layers"])
           cat = pd.merge(dsetl, layersl, how="left", left_on='id', right_on='dataset_id',suffixes=('_dset', '_layer'))
           cat = cat.sort_values(by=['id_dset','id_layer'])
           self.basecat = cat
           self.dict_cat(cat)
        except:
           print(cat_dset)  # I have seen the catalogue retrieval time off which means you get no output
           print(cat_layers)
           raise Exception("The catalog data failed to load.")


        # Create a new QTreeWidget to display the data
        self.tree.__init__(self)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.model = QtGui.QStandardItemModel(self.tree)
        self.model.setHorizontalHeaderLabels( ['Dataset', 'Layer id', 'Layer name','Resolution','Units'])
        self.tree.setModel(self.model)
        self.tree.setUniformRowHeights(True)
        self.tree.setColumnWidth(0,300)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setSortingEnabled(False)
        self.tree.doubleClicked.connect(self.tree_select)
        #self.tree_mouse_press = self.tree.mousePressEvent
        #self.tree.mousePressEvent = self.tree_select
        self.root = self.tree.rootIndex()
        self.render_tree()

        # Access the layout of the specified tab to add the table and search bar
        tab_layout = self.findChild(QtWidgets.QWidget, "tab_2").layout()

        # Create a search bar (QLineEdit) and add it to the tab's layout
        search_bar = QtWidgets.QLineEdit()
        search_bar.setPlaceholderText("Enter search here then press enter...")
        # Connect the search bar's textChanged signal to a lambda function that filters the table data
        # this did it char by char ..  search_bar.textChanged.connect(lambda: self.search_in_table(search_bar.text()))
        search_bar.returnPressed.connect(lambda: self.search_in_table(search_bar.text()))
        tab_layout.addWidget(search_bar)
        tab_layout.addWidget(self.tree)

    # Take the merged dataframes and produce an array to load UI
    # In reality this might look an unnecessary step as we search from the merged dataframe
    # The problem this solves is handling the oddities for a clean transition to display
    def dict_cat(self,cat):

        levels = {29:"12cm",28:"23cm",27:"45cm",26:"1m",25:"2m",24:"4m",23:"8m",22:"15m",21:"29m",20:"57m",19:"114m",18:"228m",17:"456m",16:"912m",15:"2km",14:"4km",
                       13:"8km",12:"15km",11:"30km",10:"59km",9:"117km",8:"234km",7:"467km",6:"934km",5:"1867km",4:"3733km",3:"7466km",2:"14932km",1:"29864km"}
        self.data = {}
        for row in cat.iterrows():
            layerid = row[1]["id_layer"]
            if type(layerid) is float and math.isnan(float(layerid)):
                   pass # Bad join?
            else:
               dsetname = row[1]["data_source_name_dset"]
               if type(dsetname) is float and math.isnan(float(dsetname)):
                  dsetname = row[1]["name_dset"]
               dsetlong = row[1]["description_long_dset"]
               if type(dsetlong) is float and math.isnan(float(dsetlong)):
                      dsetlong = ""
               layer_name = row[1]["name_layer"]
               layer_desc = row[1]["description_long_layer"]
               if type(layer_desc) is float and math.isnan(float(layer_desc)):
                      layer_desc = ""
               # Special case to jeterson unicode in description field
               layer_desc = layer_desc.encode("ascii", "ignore")
               layer_desc = layer_desc.decode()
               level = row[1]["level_layer"]
               if type(level) is float and math.isnan(level):
                      level = "None"
               else:
                      level = levels[level]
               unit = row[1]["units"]
               if type(unit) is float and math.isnan(unit):
                        unit = 'unknown'

               record = [str(dsetname), str(dsetlong),
                         str(layerid),
                         str(layer_name),
                         level,
                         unit,
                         str(layer_desc)]

               if record[0] in self.data:
                  self.data[record[0]].append(record[1:])
               else:
                  self.data[record[0]] = [record[1:]]

    # Take the record list and render into a tree view
    def render_tree(self):
        for row, (text, values) in enumerate(self.data.items()):
            category = QtGui.QStandardItem(text)
            category.setEditable(False)
            category.setToolTip(values[0][0])
            self.model.appendRow(category)
            self.tree.setFirstColumnSpanned(row, self.root, True)
            for row, value in enumerate(values):
                space = QtGui.QStandardItem()
                space.setEditable(False)
                layerid = QtGui.QStandardItem(str(value[1]))
                layerid.setEditable(False)
                desc = QtGui.QStandardItem(value[2])
                desc.setEditable(False)
                desc.setToolTip(value[5])
                res  = QtGui.QStandardItem(value[3])
                res.setEditable(False)
                unit = QtGui.QStandardItem(value[4])
                unit.setEditable(False)
                category.appendRow([
                        space,
                        layerid ,
                        desc,
                        res,
                        unit
                        ])

    # Handle layer selections and copy them into query
    def tree_select(self,event):
               index = self.tree.selectedIndexes()
               if len(index) > 1:
                   index = index[1]
                   layer = index.model().itemFromIndex(index).text()
                   self.layers.append(layer)
                   self.layers = list(set(self.layers))
                   ql = '"layers" : [' + "\n"
                   comma = "\t"
                   first = True
                   for l in self.layers:
                       name = self.basecat[self.basecat.id_layer.eq(l)]["name_layer"].to_string(header=False, index=False)
                       ql += comma + '{ "id": ' + l + ', "type": "raster" }' + "\n"
                       if first:
                          comma += ','
                          first = False

                   ql += "\t]"
                   input_str = str(self.wkt.toPlainText())
                   # Stitch it in..
                   input_str = re.sub("\"layers\"\s?:\s?\[([^]]+)\]",ql,input_str)
                   self.wkt.setPlainText(input_str)

    # Method to filter the displayed data in the QTableWidget based on user input
    def search_in_table(self, search_text):
        cat = self.basecat  # Restart from the beginning
        # Filter the DataFrame based on the search text in the specified columns
        search_text = str(search_text.strip().lower())
        if len(search_text) > 0:
           mask = np.column_stack([self.basecat[col].astype(str).str.lower().str.contains(search_text, na=False) for col in self.basecat])
           cat = self.basecat[mask.any(axis=1)]

        self.model.clear()
        self.model.setHorizontalHeaderLabels( ['Dataset', 'Layer id', 'Layer name','Resolution','Units'])
        # Rebuild the tree view for just the selected data
        self.dict_cat(cat)
        self.render_tree()

      