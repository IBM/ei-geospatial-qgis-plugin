# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoginDialog

 This class is responsible for showing the login window and to let the user 
     log in to an IBM Geospatial APIs backend.

        author            : 2024 by Jannis Fleckenstein
        email             : jannis.fleckenstein@ibm.com
 ***************************************************************************/
"""
import os

from qgis.PyQt import uic
from qgis.core import QgsApplication, Qgis
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings

from qgis.PyQt.QtGui import QIcon
from .ibmpairsdialog import IBMPairsDialog
import ibmpairs.client as client
import ibmpairs.catalog as catalog
import datetime
import json
import os

SETTINGS_NAMESPACE="ibm_pairs"
SAVE_CREDS_KEY="save_credentials"
AUTH_CREDS_KEY = "ibmpairs_plugin_auth"
AUTH_SEP = "|||"
AUTH_STRING = "{EIS_API_KEY}{sep}{EIS_TENANT_ID}{sep}{EIS_ORG_ID}"

########################################################################################################################
########################################################################################################################

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'login_dialog.ui'))


class LoginDialog(QtWidgets.QDialog, FORM_CLASS):
    """
    This class is responsible for showing the login window and to let the user log in to an IBM Geospatial APIs backend.
    """
    def __init__(self, parent=None, iface=None, ibmpairs=None):
        """
        Constructor method: Initializes the dialog UI and loads credentials if they exist.
        :param parent: The parent dialog or widget.
        :param iface: Interface to display the dialog.
        :param ibmpairs: Reference to the main IBM Pairs plugin instance.
        """
        super(LoginDialog, self).__init__(parent)

        QApplication.setStyle("cleanlooks")

        self.ibmpairs = ibmpairs
        self.iface = iface
        self.setupUi(self)
        
        self.auth_man = QgsApplication.authManager()
        
        credentials = self.load_credentials()
        
        if credentials:
            self.apiEdit.setText(credentials["EIS_API_KEY"])
            self.tenantEdit.setText(credentials["EIS_TENANT_ID"])
            self.orgEdit.setText(credentials["EIS_ORG_ID"])
            self.cbx_save_credentials.setChecked(True)
            self.save_creds = bool(QSettings().value(f"{SETTINGS_NAMESPACE}/{SAVE_CREDS_KEY}"))
            
        self.loginButton.clicked.connect(self.login)
        self.dlg = None

    def connect(self):
        """
        Attempts to authenticate with the provided API key, tenant ID, and organization ID.
        Displays a warning if authentication fails.
        """
        api = self.apiEdit.text()
        tenant = self.tenantEdit.text()
        org = self.orgEdit.text()

        auth = client.get_client(api_key=api, tenant_id=tenant, org_id=org, legacy=False)

        if not auth:
            QMessageBox.information(self.iface.mainWindow(), \
            QCoreApplication.translate('IBMPairsConnector', "IBM Geospatial APIs plugin error"), \
            QCoreApplication.translate('IBMPairsConnector', "Error: Wrong login information."))
            return None

        return auth
    
    def catalog(self):
        """
        Retrieve catalog information in order to load in the dialog.
        """
        
        dsets_path = os.path.join(os.path.dirname(__file__),'data_sets.json')
        layer_path = os.path.join(os.path.dirname(__file__),'data_layers.json')
        if not os.path.isfile(dsets_path):
            cat_dset = catalog.get_data_sets().to_json()
            f = open(dsets_path, "w")
            f.write(cat_dset)
            f.close()
        else:
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(dsets_path))
            duration = today - modified_date
            # Refresh the catalog every 15 days
            if duration.days > 15:
                cat_dset = catalog.get_data_sets().to_json()
                f = open(dsets_path, "w")
                f.write(cat_dset)
                f.close()
                    
        # Now handle layers
        if not os.path.isfile(layer_path):
            cat_layers = catalog.get_data_layers().to_json()
            f = open(layer_path, "w")
            f.write(cat_layers)
            f.close()
        else:
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(dsets_path))
            duration = today - modified_date
            # Refresh the catalog every 15 days
            if duration.days > 15:
                cat_layers = catalog.get_data_layers().to_json()
                f = open(layer_path, "w")
                f.write(cat_layers)
                f.close()

    def login(self):
        """
        Handles the login button click event. Saves credentials if the corresponding checkbox is checked.
        Initiates login to the IBM Pairs service.
        """
        api = self.apiEdit.text()
        tenant = self.tenantEdit.text()
        org = self.orgEdit.text()
        if self.cbx_save_credentials.isChecked():
            self.save_credentials(api, tenant, org)
        self.ibmpairs.login()

    def save_credentials(self, api, tenant, org):
        """
        Encrypts and saves the credentials to qGIS database.
        :param api: The API key.
        :param tenant: The tenant ID.
        :param org: The organization ID.
        """

        auth_creds_str = AUTH_STRING.format(
            EIS_API_KEY = api,
            EIS_TENANT_ID = tenant,
            EIS_ORG_ID = org,
            sep = AUTH_SEP,
        )
        self.auth_man.storeAuthSetting(AUTH_CREDS_KEY, auth_creds_str, True)


    def load_credentials(self):
        """
        Attempts to load credentials saved in qGIS Auth Database.
        Returns EIS_API_KEY, EIS_TENANT_ID, AND EIS_ORG_ID otherwise 
        None if the file is missing, empty, or contains invalid data.
        """
        auth_creds_str = (
            self.auth_man.authSetting(AUTH_CREDS_KEY, defaultValue="", decrypt=True)
            or ""
        )
        creds = auth_creds_str.split(AUTH_SEP) if auth_creds_str is not None else []
        return {
            "EIS_API_KEY": creds[0] if len(creds) > 0 else None,
            "EIS_TENANT_ID": creds[1] if len(creds) > 1 else None,
            "EIS_ORG_ID": creds[2] if len(creds) > 2 else None,
        }
    