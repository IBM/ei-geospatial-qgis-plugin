@echo "Installing IBM Geospatial QGIS plug-in ..."
python -m packaging_cli prerequisites
python -m packaging_cli install
pause "Done"
