#!/usr/bin/env python

from datetime import datetime
import os
import subprocess
import shlex
import configparser
import cmd
import sys
import platform
import shutil
import argparse
import pathlib
import zipfile
import re
from packaging.version import Version

def console_print(name, message):
    dt = datetime.now()
    dt_string = dt.strftime("%Y/%m/%d %H:%M:%S")
    
    print("{} {}(): {}".format(dt, name, message))

class Packaging(cmd.Cmd):

    prompt = '>> '
    intro = 'IBM Environmental Intelligence: Geospatial APIs QGIS Plugin Packaging CLI.'

    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()
        self.project_version   = "0.1.0"

    def postcmd(self, stop, args):

        print("========")
        return stop

    def windows_qgis_version(self, root_dir):
        latest = Version("0.0.0")
        for item in os.listdir(root_dir):
            if 'QGIS' in item:
                split = item.split(" ")
                if len(split) > 1:
                    current_version = split[1]
                    if Version(current_version) > latest:
                        latest = Version(current_version)
        return latest
    
    def windows_qgis_python_version(self, qgis_dir):
      
        python_folder_regex = re.compile('^Python\d{2,3}$')
      
        apps_dir = "{}/{}".format(qgis_dir, '/apps')
        if os.path.isdir(apps_dir):
            for item in os.listdir(apps_dir):
                if python_folder_regex.match(item):
                    return item
                
        return None
        
    def do_quit(self, args):

        """
        Exit the Packaging CLI.
        """

        return True
    
    def do_develop(self, args):
        
        """
        Install development pre-requisites.
        """
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-development.txt"])


    def do_clean(self, args):

        """
        Cleans the repository of build artefacts.
        """
      
        if platform.system() == "Windows":
            cmd = "{}/sphinx/make.bat clean -C {}/sphinx".format(self.current_directory, self.current_directory)
        else:
            cmd = "make clean -C {}/sphinx".format(self.current_directory)

        # sphinx/build
        console_print('clean', 'sphinx/build')
        os.system(cmd)
        
        # src/ei_geospatial/docs
        docs = "src/ei_geospatial/docs"
        if os.path.exists(docs):
            console_print('clean', 'src/ei_geospatial/docs')
            shutil.rmtree(docs)

        # docs  
        docs = "docs"
        if os.path.exists(docs):
            console_print('clean', 'docs')
            shutil.rmtree(docs)

        # metadata.txt
        metadata = "src/ei_geospatial/metadata.txt"
        if os.path.exists(metadata):
            console_print('clean', 'src/ei_geospatial/metadata.txt')
            os.remove(metadata)

        # resources.py
        #resources = "src/ei_geospatial/resources/resources.py"
        resources = "src/ei_geospatial/resources.py"
        if os.path.exists(resources):
            #console_print('clean', 'src/ei_geospatial/resources/resources.py')
            console_print('clean', 'src/ei_geospatial/resources.py')
            os.remove(resources)
            
        # src/ei_geospatial/docs
        target = "target"
        if os.path.exists(target):
            console_print('clean', 'target')
            shutil.rmtree(target)


    def do_doc(self, args):

        """
        Generates the Sphinx documentation.
        """

        console_print('doc', 'building sphinx/build')
        
        if platform.system() == "Windows":
            cmd = "{}/sphinx/make.bat html -C {}/sphinx".format(self.current_directory, self.current_directory)
        else:
            cmd = "make html -C {}/sphinx".format(self.current_directory)

        os.system(cmd)

        if os.path.exists("sphinx/build/html/index.html"):
            console_print('doc', 'successfully built sphinx docs')
        else:
            console_print('doc', 'failed building sphinx docs')

        console_print('docs', 'copying doc build to src/ei_geospatial/docs')
        shutil.copytree("sphinx/build/", "src/ei_geospatial/docs/")    


    def do_pages(self, args):
        
        console_print('pages', 'copying sphinx/build to ./docs')

        shutil.copytree("sphinx/build/html", "docs/")
        
        subprocess.check_call(["touch", "docs/.nojekyll"])


    def do_metadata(self, args):

        """
        Generates the src/ei_geospatial/metadata.txt file for the QGIS Plugin.
        """

        # https://docs.qgis.org/3.34/en/docs/pyqgis_developer_cookbook/plugins/plugins.html

        config = configparser.ConfigParser()
        config['general'] = {}

        # Required Fields
        config['general']['name'] = "IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin" 
        config['general']['qgisMinimumVersion'] = "3.0"
        config['general']['description'] = "IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin"
        config['general']['about'] = "The IBM Environmental Intelligence: Geospatial APIs- QGIS Plugin allows users to discover, query and download environmental data and insights within QGIS."
        config['general']['version'] = "1.0"
        config['general']['author'] = "Jannis Fleckenstein, Patrick Dantressangle, David Selby & Steffan J. Taylor"
        config['general']['email'] = "pairs@us.ibm.com"
        config['general']['homepage'] = "https://www.ibm.com/products/environmental-intelligence"
        config['general']['repository'] = "https://github.com/IBM/ei-geospatial-qgis-plugin"
        config['general']['icon'] = "icon.png"

        # Optional Fields
        #config['general']['qgisMaximumVersion']
        #config['general']['changelog']
        #config['general']['experimental']
        #config['general']['deprecated']
        #config['general']['tags']
        #config['general']['tracker']
        #config['general']['category']
        #config['general']['plugin_dependencies']
        #config['general']['server']
        #config['general']['hasProcessingProvider']

        with open('src/ei_geospatial/metadata.txt', 'w') as configfile:
            console_print('metadata', 'writing src/ei_geospatial/metadata.txt')
            config.write(configfile)
            console_print('metadata', 'src/ei_geospatial/metadata.txt created')


    #def do_repo_xml(self, args):
    
    
    def do_compile_ui(self, args):
      
        """
        Compiles the .ui files using pyuic5.
        """
        
        ui = "{}/src/ei_geospatial".format(self.current_directory)
        py = "{}/src/ei_geospatial".format(self.current_directory)
        
        console_print('compile', 'src/ei_geospatial/ibmpairs_login.ui')
        
        os.system("pyuic5 -o {}/ibmpairs_login.py {}/ibmpairs_login.ui".format(py, ui))
        
        console_print('compile', 'src/ei_geospatial/ibmpairs_plugin.ui')
        
        os.system("pyuic5 -o {}/ibmpairs_plugin.py {}/ibmpairs_plugin.ui".format(py, ui))
        
        if os.path.exists("src/ei_geospatial/ibmpairs_login.py"):
            console_print('compile', 'successfully built src/ibmpairs_login.py')
        else:
            console_print('compile', 'failed building src/ibmpairs_login.py')
          
        if os.path.exists("src/ei_geospatial/ibmpairs_plugin.py"):
            console_print('compile', 'successfully built src/ibmpairs_plugin.py')
        else:
            console_print('compile', 'failed building src/ibmpairs_plugin.py')
      
        
    def do_compile_resources(self, args):
      
        """
        Compiles the resources.py from resources.qrc using pyrcc5.
        """
      
        console_print('compile', 'src/ei_geospatial/resources.qrc')
      
        resources = "{}/src/ei_geospatial".format(self.current_directory)
        
        os.system("pyrcc5 -o {}/resources.py {}/resources.qrc".format(resources,resources))
      
        if os.path.exists("src/ei_geospatial/resources.py"):
            console_print('compile', 'successfully built src/resources.py')
        else:
            console_print('compile', 'failed building src/resources.py')


    def do_compile(self, args):

        """
        Compiles the resources and ui files.
        """
        
        self.do_compile_resources(args)
        
        self.do_compile_ui(args)


    def do_package(self, args):

        """
        Packages a release zip.
        """
        
        console_print('package', 'reading exclude file')
        
        # Gather exclusions
        f = open("exclude", "r")
        exclusions = f.read().splitlines()
        console_print('package', 'package exclusions {}'.format(exclusions))
        f.close
        
        # Create a list of files to be zipped
        zip_list = []

        src = os.getcwd() + '/src/'
        for root, dirs, files in os.walk(src):
            for f in files:
                rel_dir = os.path.relpath(root, src)
                file_path = str(os.path.join(rel_dir, f))
                if not f in exclusions:
                    zip_list.append(file_path)
                    console_print('package', 'file included {}'.format(file_path))
                else:
                    console_print('package', 'file excluded {}'.format(file_path))
        
        # Create the target directory
        pathlib.Path('target').mkdir(parents=True, exist_ok=True)
        console_print('package', 'created directory ./target')
        
        # Create the zipped package
        with zipfile.ZipFile('target/ei_geospatial_{}.zip'.format(self.project_version), 'w') as zipped:
            for f in zip_list:
                zipped.write('src/{}'.format(f),
                             arcname=f, 
                             compress_type=zipfile.ZIP_DEFLATED)


    def do_prerequisites(self, args):

        """
        Installs pip pre-requisites into QGIS python environment.
        """
        
        parser = argparse.ArgumentParser(description='QGIS Directory', usage='install [--qgis_dir=<qgis_dir>]')
        parser.add_argument("--qgis_dir", required=False)
        
        argsparsed = parser.parse_args(shlex.split(args))
        
        if argsparsed.qgis_dir is not None:
          if platform.system() == "Windows":
              qgis_python_version = self.windows_qgis_python_version("{}".format(argsparsed.qgis_dir))
              
              if qgis_python_version is None:
                  raise Exception("A QGIS Python installation could not be found in the provided installation path: {}/apps/Python{}.".format(root_dir, qgis_version, '<version>'))
                  
              os.environ["PYTHONHOME"] = "{}/apps/{}".format(argsparsed.qgis_dir, qgis_python_version)
              os.environ["PYTHONPATH"] = "{}/apps/{}/Lib".format(argsparsed.qgis_dir, qgis_python_version)
              os.environ["PATH"] = os.environ["PATH"] + ";{}/bin".format(argsparsed.qgis_dir) + ";{}/apps/{}/Scripts".format(argsparsed.qgis_dir, qgis_python_version)
              
              qgis_pyenv = "{}/bin/python3.exe".format(argsparsed.qgis_dir)
          else:
              qgis_pyenv = "{}/bin/python3".format(argsparsed.qgis_dir)
        else:
            if platform.system() == "Linux":
                console_print('prerequisites', 'platform is Linux')
                default_qgis_pyenv = "/usr/bin/python"
            elif platform.system() == "Darwin":
                console_print('prerequisites', 'platform is Mac (Darwin)')
                default_qgis_pyenv = "/Applications/QGIS.app/Contents/MacOS/bin/python3"
            elif platform.system() == "Windows":
                console_print('prerequisites', 'platform is Windows')
                root_dir = "C:/Program Files/"
                qgis_version = self.windows_qgis_version(root_dir = root_dir)
                
                if qgis_version is Version("0.0.0"):
                    raise Exception("A QGIS installation could not be found in the default installation path: {}/QGIS {}, please supply the QGIS directory with the option --qgis_dir={}.".format(root_dir, '<version>', '<qgis_dir>'))
                
                qgis_python_version = self.windows_qgis_python_version("{}/QGIS {}".format(root_dir, qgis_version))
                
                if qgis_python_version is None:
                    raise Exception("A QGIS Python installation could not be found in the default installation path: {}/QGIS {}/apps/Python{}.".format(root_dir, qgis_version, '<version>'))
                    
                qgis_python = "{}/QGIS {}/apps/{}".format(root_dir, qgis_version, qgis_python_version)

                os.environ["PYTHONHOME"] = qgis_python
                os.environ["PYTHONPATH"] = "{}/Lib".format(qgis_python)
                os.environ["PATH"] = os.environ["PATH"] + ";{}/QGIS {}/bin".format(root_dir, qgis_version) + ";{}/QGIS {}/apps/{}/Scripts".format(root_dir, qgis_version, qgis_python_version)
                
                default_qgis_pyenv = "{}/python3.exe".format(qgis_python)
            else:
                console_print('prerequisites', 'unknown platform {}, should be Linux, Darwin or Windows'.format(platform.system()))
                
            qgis_pyenv = default_qgis_pyenv
            
        console_print('prerequisites', "The QGIS Python environment is {}".format(qgis_pyenv))
            
        subprocess.check_call([qgis_pyenv, "-m", "pip", "install", "-r", "requirements.txt"])

    def do_install(self, args):

        """
        Installs zip package to environment.
        """
        
        parser = argparse.ArgumentParser(description='Install Arguments', usage='install [--plugin_path=<plugin_path>]')
        parser.add_argument("--plugin_path", required=False)

        argsparsed = parser.parse_args(shlex.split(args))

        if platform.system() == "Linux":
            console_print('install', 'platform is Linux')
            default_plugin_path = "/.local/share/QGIS/QGIS3/profiles/default/python/plugins"
        elif platform.system() == "Darwin":
            console_print('install', 'platform is Mac (Darwin)')
            default_plugin_path = "/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
        elif platform.system() == "Windows":
            console_print('install', 'platform is Windows')
            default_plugin_path = "/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins"
        else:
            console_print('install', 'unknown platform {}, should be Linux, Darwin or Windows'.format(platform.system()))
            
        user_path = os.path.expanduser('~')
        
        if argsparsed.plugin_path is not None:
            plugin_path = user_path + argsparsed.plugin_path
        else:
            plugin_path = user_path + default_plugin_path
            
        console_print('install', 'plugin_path={}'.format(plugin_path))
        
        if not os.path.exists(plugin_path):
            console_print('install', 'ensuring {} exists or creating'.format(plugin_path))
            os.makedirs(plugin_path, exist_ok=True)
        
        console_print('install', 'unzipping target/ei_geospatial_{}.zip to {}'.format(self.project_version, plugin_path))
        with zipfile.ZipFile('target/ei_geospatial_{}.zip'.format(self.project_version), 'r') as zipped:
            zipped.extractall(path=plugin_path)
            
        console_print('install', 'installed plugin to {}/ei_geospatial'.format(plugin_path))
        

if __name__ == '__main__':

    if len(sys.argv) > 1:
        Packaging().onecmd(' '.join(sys.argv[1:]))
    else:
        Packaging().cmdloop()
      
      