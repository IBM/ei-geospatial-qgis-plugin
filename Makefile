PYTHON_ENV:="python"

develop: ## Install development pre-requisites.
develop:
	@echo 'develop'
	@if $(PYTHON_ENV) packaging_cli.py develop; then exit 0; else exit 1; fi

clean: ## Cleans the repository of build artefacts. 
clean:
	@echo 'clean'
	@if $(PYTHON_ENV) packaging_cli.py clean; then exit 0; else exit 1; fi

doc: ## Generates the Sphinx documentation.
doc:
	@echo 'doc'
	@if $(PYTHON_ENV) packaging_cli.py doc; then exit 0; else exit 1; fi

pages: ## Copies Sphinx docs to the docs repository to show as a set of GitHub pages.
pages: doc
	@echo 'page'
	@if $(PYTHON_ENV) packaging_cli.py pages; then exit 0; else exit 1; fi

metadata: ## Generates the src/ei_geospatial/metadata.txt file for the QGIS Plugin.
metadata:
	@echo 'metadata'
	@if $(PYTHON_ENV) packaging_cli.py metadata; then exit 0; else exit 1; fi

compile: ## Compiles the resources.py from resources.qrc using pyrcc5.
compile:
	@echo 'compile'
	@if $(PYTHON_ENV) packaging_cli.py compile; then exit 0; else exit 1; fi

package: ## Packages a release zip.
package: clean doc metadata compile
package:
	@echo 'compile'
	@if $(PYTHON_ENV) packaging_cli.py package; then exit 0; else exit 1; fi

prerequisites: ## Installs zip package to environment.
prerequisites:
	@echo 'prerequisites'
	@if $(PYTHON_ENV) packaging_cli.py prerequisites; then exit 0; else exit 1; fi

install: ## Installs zip package to environment.
install: prerequisites 
install:
	@echo 'install'
	@if $(PYTHON_ENV) packaging_cli.py install; then exit 0; else exit 1; fi
	
