from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from nbconvert.exporters.export import *
import base64
import json
import requests
import tornado
import os
import logging

# Example usage: tornado_logger.error("This is an error!")
tornado_logger = logging.getLogger("tornado.application")

def raise_error(msg):
    raise tornado.web.HTTPError(500, "ERROR: " + msg)

def raise_github_error(msg):
    raise tornado.web.HTTPError(500, "ERROR: Github returned the following: " + msg)


class BaseHandler(IPythonHandler):
    client_id = None
    client_secret = None

    # Extracts the access code from the arguments dictionary (given back from github)
    def extract_code_from_args(self, args):
        error = args.get("error_description", None)
        if error is not None:
            if (len(error) >= 0):
                raise_github_error(error)

        access_code = args.get("code", None)
        if access_code is None or len(access_code) <= 0:
            raise_error("Couldn't extract github authentication code from response"),

        # If we get here, everything was good - no errors
        access_code = access_code[0].decode('ascii')
        return access_code

    # Extracts the notebook path from the arguments dictionary (given back from github)
    def extract_notebook_path_from_args(self, args):
        error = args.get("error_description", None)
        if error is not None:
            if (len(error) >= 0):
                raise_github_error(error)

        path_bytes = args.get("nb_path", None)
        if path_bytes is None or len(path_bytes) <= 0:
            raise_error("Couldn't extract notebook path from response")

        # If we get here, everything was good - no errors
        nb_path = base64.b64decode(path_bytes[0]).decode('utf-8').lstrip("/")
        return nb_path


    def request_access_token(self, access_code):

        # Request access token from github
        token_response = requests.post("https://github.com/login/oauth/access_token",
            data = {
                "client_id": BaseHandler.client_id,
                "client_secret" : BaseHandler.client_secret,
                "code" : access_code
            },
            headers = {"Accept" : "application/json"})

        token_args = json.loads(token_response.text)

        token_error = token_args.get("error_description", None)
        if token_error is not None:
            raise_github_error(token_error)

        # Extract token and other info from github response
        access_token = token_args.get("access_token", None)
        token_type = token_args.get("token_type", None)
        scope = token_args.get("scope", None)
        if access_token is None or token_type is None or scope is None:
            raise_error("Couldn't extract needed info from github access token response")

        # If we get here everything is good
        return access_token #do not care about scope or token_type

    def get_notebook_filename(self, nb_path):

        # Extract file names given path to notebook
        filename = os.path.basename(nb_path)
        ext_start_ind = filename.rfind(".")
        if ext_start_ind == -1:
            filename_no_ext = filename
        else:
            filename_no_ext = filename[:ext_start_ind]

        return filename, filename_no_ext

    def get_notebook_contents(self, nb_path):

        # Extract file contents given the path to the notebook
        notebook_output, _ = export_by_name("notebook", nb_path)
        python_output, _ = export_by_name("python", nb_path)

        return (notebook_output, python_output)

    def find_existing_gist_by_name(self, nb_filename, py_filename, access_token):

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        response = requests.get("https://api.github.com/gists",
            headers = github_headers)
        get_gists_args = json.loads(response.text)

        match_counter = 0;
        matchID = None
        for gist in get_gists_args:
            gist_files = gist.get("files", None)
            if (gist_files is not None and nb_filename in gist_files
                    and py_filename in gist_files):
                match_counter += 1
                if "id" in gist:
                    matchID = gist["id"]

        # TODO: This probably shouldn't actually be an error
        # Instead, we should ask the user which gist they meant?
        if match_counter > 1:
            raise_error("You had multiple gists with the same name as this notebook. Aborting.")

        # If we are here we have either 0 or 1 gists that match. 
        return matchID

    def create_new_gist(self, gist_contents, access_token):

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        gist_response = requests.post("https://api.github.com/gists",
                data = json.dumps(gist_contents),
                headers = github_headers)

        self.verify_gist_response(gist_response)
        

    def edit_existing_gist(self, gist_contents, gist_id, access_token):

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        gist_response = requests.patch("https://api.github.com/gists/" + gist_id,
                data = json.dumps(gist_contents),
                headers = github_headers)

        self.verify_gist_response(gist_response)
        

    def verify_gist_response(self, gist_response):

        gist_response_json = gist_response.json()
        update_gist_error = gist_response_json.get("error_description", None)
        if update_gist_error is not None:
            raise_github_error(update_gist_error)
            
        gist_url = gist_response_json.get("html_url", None)
        if gist_url is None:
            raise_error("Couldn't get the url for the gist that was just updated")

        # If we return without erroring we are good
        self.redirect(gist_url)

# This handler will save out the notebook to GitHub gists in either a new Gist 
# or it will create a new revision for a gist that already contains these two files.
class GistHandler(BaseHandler):

    def get(self):

        # Extract access code
        access_code = self.extract_code_from_args(self.request.arguments)

        # Request access token from github
        access_token = self.request_access_token(access_code)

        github_headers = { "Accept" : "application/json",
                            "Authorization" : "token " + access_token }

        # Extract notebook path
        nb_path = self.extract_notebook_path_from_args(self.request.arguments)

        # Extract file name
        filename, filename_no_ext = self.get_notebook_filename(nb_path)

        # Extract file contents given the path to the notebook
        notebook_output, python_output = self.get_notebook_contents(nb_path)

        # Prepare and our github request to create the new gist
        filename_with_py = filename_no_ext + ".py"
        gist_contents = {
            "description": filename_no_ext,
            "public": False,
            "files": {
                filename : {"filename" : filename, "content": notebook_output},
                filename_with_py : { "filename" : filename_with_py,
                                "content": python_output }
            }
        }

        # Get the authenticated user's matching gist (if available)
        matchID = self.find_existing_gist_by_name(filename, 
                                filename_with_py, access_token)

        # If no gist with this name exists yet, create a new gist
        if matchID is None:
            gist_response = self.create_new_gist(gist_contents, access_token)

        # If we have another gist with the same files, create a new revision
        # Note: The case where we have multiple gists with the files is handled by find_existing_gist_by_name
        # This else catches the case where there is exactly 1 match
        else: 
            gist_response = self.edit_existing_gist(gist_contents, matchID, access_token)  


class DownloadNotebookHandler(IPythonHandler):
    def post(self):
        # url and filename are sent in a JSON encoded blob
        post_data = tornado.escape.json_decode(self.request.body) 

        nb_url = post_data["nb_url"]
        nb_name = base64.b64decode(post_data["nb_name"]).decode('utf-8')
        force_download = post_data["force_download"]

        file_path = os.path.join(os.getcwd(), nb_name)

        if os.path.isfile(file_path):
            if not force_download:
                raise tornado.web.HTTPError(409, "ERROR: File already exists.")

        r = requests.get(nb_url, stream=True)
        with open(file_path, 'wb') as fd:
            for chunk in r.iter_content(1024): # TODO: check if this is a good chunk size
                fd.write(chunk)

        self.write(nb_name)
        self.flush()


def load_jupyter_server_extension(nb_server_app):

    # Extract our gist client details from the config:
    cfg = nb_server_app.config["NotebookApp"]
    BaseHandler.client_id = cfg["oauth_client_id"]
    BaseHandler.client_secret = cfg["oauth_client_secret"]

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/create_gist')
    download_notebook_route_pattern = url_path_join(web_app.settings['base_url'], '/download_notebook')


    web_app.add_handlers(host_pattern, [(route_pattern, GistHandler), (download_notebook_route_pattern, DownloadNotebookHandler)])


