import simplejson as json
import os
import sys
import zipfile
import shutil
import pyprind
import requests
from Utils import Utils
from Builder import *

KAPTL_HOST = "https://www.kaptl.com"
KAPTL_PARSE_URL = KAPTL_HOST + "/api/apps/parse"
KAPTL_DOWNLOAD_URL = KAPTL_HOST + "/api/apps/download"

session = requests.Session()


class NoStackInfoException(Exception):
    pass


class WrongStackInfoException(Exception):
    pass


class NoRulesInfoException(Exception):
    pass


class Kaptl:
    def __init__(self, arguments):
        self.rules = ""
        self.angular_only = False
        self.frontend = []
        self.backend = []
        self.stack = []
        self.manifest = {}
        self.kaptl_cookie = None
        self.builder = Builder()
        self.project_dir = ""

        # used in two cases, when there is an existing app and when rules.kaptl file exists
        self.existing = False
        self.arguments = arguments

    def execute_pipeline(self):
        """Run the pipeline of requests, get the file and unzip it"""
        # process arguments
        if self.arguments["update"]:
            self.existing = True
            self.process_manifest()
            if self.manifest["appName"]:
                self.kaptl_cookie = {"kaptl-session-id": self.manifest["appName"]}

        if self.arguments["show"]:
            self.process_manifest()
            self.output_project_info()
        else:
            try:
                self.process_stack_info()
            except NoStackInfoException, e:
                print e.message
                sys.exit()
            except WrongStackInfoException, e:
                print e.message
                sys.exit()

            if self.arguments["<rules>"] is None and \
                            self.arguments["--rules-file"] is False and \
                            self.arguments["--rules-from-config"] is False:
                self.rules = Utils.read_rules_from_file(os.getcwd() + "/rules.kaptl")
                self.existing = True
            elif self.arguments["<rules>"]:
                self.rules = self.arguments["<rules>"]
            elif self.arguments["--rules-file"]:
                self.rules = Utils.read_rules_from_file(self.arguments["--rules-file"])  # read the data from file
            elif self.arguments["--rules-from-config"]:
                self.rules = Utils.read_rules_from_file(os.getcwd() + "/rules.kaptl")
            else:
                print "ERROR: Couldn't find rules"
                sys.exit()

        app_name = self.parse_rules()
        if app_name is not None:
            file_info = self.get_file_info(app_name)
            if file_info is not None:
                self.download_file(file_info)
                if self.arguments["--rules-from-config"]:
                    self.existing = True
                if self.existing:
                    self.project_dir = os.getcwd()
                else:
                    self.project_dir = os.getcwd() + "/" + file_info[1][:-4]
                self.unzip_archive(file_info[1], existing=self.existing)
                if self.arguments["--build"]:
                    try:
                        subprocess.call([self.project_dir + "/NuGet.exe", "restore",
                                         self.project_dir + "/MvcApp-Demo.sln"])
                        self.builder.build(self.project_dir + "/MvcApp-Demo.sln")
                    except MSBuildNotFoundException, e:
                        print e.message
                        sys.exit()
                    except MSBuildFailedException, e:
                        print e.message
                        sys.exit()
            else:
                print "ERROR: Couldn't retrieve a file from the server. Try again later."
                sys.exit()
        else:
            sys.exit()

    def parse_rules(self):
        print "Parsing the rules..."
        request_data = dict(rulesText=self.rules.replace('\\', '').replace('\'', '"'), stack=self.stack)
        try:
            if self.kaptl_cookie is not None:
                response = session.post(KAPTL_PARSE_URL, json=request_data,
                                        cookies=self.kaptl_cookie)
            else:
                response = session.post(KAPTL_PARSE_URL, json=request_data)
            response_content = response.json()
            if response.status_code and response_content["success"]:
                print "Rules were parsed successfully"
                return response_content["appName"]
            else:
                print "ERROR: There was a problem with parsing the rules"
                if response_content["compilerOutput"]:
                    print response_content["compilerOutput"]
                return None
        except requests.exceptions.RequestException:
            print("ERROR: API is unavailable at the moment, please try again later")
            sys.exit()

    def get_file_info(self, app_name):
        print "Downloading the generated app..."
        request_data = dict(app={
            'id': 0,
            'name': app_name,
            'rules': self.rules,
            'stack': self.stack
        }, angularOnly=self.angular_only)

        try:
            response = session.post(KAPTL_DOWNLOAD_URL, json=request_data)
            response_content = response.json()
            if response.status_code and response_content["success"]:
                return response_content["fileUrl"], response_content["fileName"]
            else:
                return None
        except requests.exceptions.RequestException:
            print("ERROR: API is unavailable at the moment, please try again later.")
            sys.exit()

    @staticmethod
    def download_file(file_info):
        try:
            with open(file_info[1], 'wb') as f:
                r = session.get(file_info[0], stream=True)
                total_length = int(r.headers.get('content-length'))
                bar = pyprind.ProgBar(total_length / 1024)
                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                        bar.update()
        except IOError:
            print "ERROR: Couldn't download a file"
            sys.exit()

    @staticmethod
    def unzip_archive(filename, existing):
        if not os.path.exists(filename[:-4]):
            os.makedirs(filename[:-4])
        try:
            with open(filename, "rb") as f:
                z = zipfile.ZipFile(f)
                if existing:
                    result = Utils.query_yes_no("This action may override changes you already made to your project "
                                                "in the current directory. Do you want to proceed?")
                    if result == "yes" or result == "y":
                        for name in z.namelist():
                            z.extract(name, os.getcwd())
                    elif result == "no" or result == "n":
                        print "Exiting the program..."
                    try:
                        if os.path.exists(filename[:-4]):
                            shutil.rmtree(filename[:-4], True)
                    except IOError:
                        print "ERROR: Couldn't delete the directory"
                else:
                    for name in z.namelist():
                        z.extract(name, filename[:-4])
            try:
                print "Cleaning up..."
                os.remove(filename)
            except IOError:
                print "ERROR: Couldn't delete a zip file"
        except IOError:
            print "ERROR: Couldn't unzip the file"

    def process_manifest(self):
        try:
            with open("kaptl_manifest.json", "r") as manifest_file:
                self.manifest = json.loads(manifest_file.read(), 'utf-8')
        except IOError:
            print "ERROR: Couldn't parse a manifest file. " \
                  "Check if kaptl_manifest.json exists in the directory " \
                  "and is a valid JSON."

    def process_stack_info(self):
        if self.arguments["init"]:
            if self.arguments["--backend"] is not None:
                self.backend = [self.arguments["--backend"]]
                if self.backend != ["mvc"] and self.backend != ["sails"]:
                    raise WrongStackInfoException("ERROR: Backend framework is specified incorrectly")
            else:
                self.backend = []

            if self.arguments["--frontend"] is not None:
                self.frontend = [self.arguments["--frontend"]]
                if self.frontend != ["angular"]:
                    raise WrongStackInfoException("ERROR: Frontend framework is specified incorrectly")
            else:
                self.frontend = []

            if self.arguments["--backend"] is None and self.arguments["--frontend"] is None:
                # raise NoStackInfoException("ERROR: Please specify at least one of the stack parts")
                print "Using defaults (Backend: ASP.NET MVC, Frontend: None)"
                self.backend = ["mvc"]
                self.frontend = []

            self.stack = {"backend": self.backend, "frontend": self.frontend}

        if self.arguments["update"]:
            self.stack = self.manifest["stack"]
            if self.stack["backend"] is None:
                self.stack["backend"] = []
            if self.stack["frontend"] is None:
                self.stack["frontend"] = []

        if not self.backend:
            if self.frontend == ["angular"]:
                self.angular_only = True
            elif self.stack["frontend"] == ["angular"] and self.stack["backend"] == []:
                self.angular_only = True
            else:
                self.angular_only = False
        else:
            pass

    def output_project_info(self):
        print "App name: " + self.manifest["appName"]
        print "Stack: " + self.get_stack_string()
        if "\n" in self.manifest["rules"]:
            print "Rules:"
            print self.manifest["rules"]
        else:
            print "Rules: " + self.manifest["rules"]

    def get_stack_string(self):
        backend = ""
        frontend = ""
        if self.manifest["stack"]["backend"] == ["mvc"]:
            backend = "ASP.NET MVC"
        elif self.manifest["stack"]["backend"] == ["sails"]:
            backend = "Sails.js"
        elif self.manifest["stack"]["backend"] is None:
            backend = ""

        if self.manifest["stack"]["frontend"] == ["angular"]:
            frontend = "AngularJS"
        elif self.manifest["stack"]["frontend"] is None:
            frontend = ""

        if frontend == "":
            return backend
        elif backend == "":
            return frontend
        else:
            return backend + " + " + frontend
