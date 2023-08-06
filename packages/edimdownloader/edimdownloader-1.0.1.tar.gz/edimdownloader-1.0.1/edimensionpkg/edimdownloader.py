#!env/usr/bin python3
"""EEE Dimension Downloader

Usage:
  yeeDimDownloader.py (-h | --help)
  yeeDimDownloader.py <username> <password> <dirname> [-j=<jsonfile>]
  yeeDimDownloader.py (--default)
  yeeDimDownloader.py (-u | <username>) (-p | <password>) (-d | <dirname>) [-j=<jsonfile>]
  yeeDimDownloader.py --version


Options:
  -h --help         Show this screen.
  --version         Show version.
  <username>        Your username
  <password>        Your password
  <dirname>         Name of directory where files will be downloaded
                    (Can be an absolute or relative path)
  -j=<jsonfile>     Specify JSON cache [default: cache.json]
  --default         Use default values
  -u --userdefault  Use default username in USERNAME
  -p --passdefault  Use default password in PASSWORD
  -d --dirdefault   Use default directory in DIRNAME

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import dict
from builtins import open
from future import standard_library

import requests
import urllib.parse
import os
import re
import utilities
import json
import codecs
import mimetypes
from docopt import docopt
from bs4 import BeautifulSoup

standard_library.install_aliases()

mimetypes.init()


class EDimensionDownloader(object):

    def __init__(self, username, password, dirname,
                 jsonfile="cache.json",
                 url="https://edimension.sutd.edu.sg/",
                 webportalurl="https://edimension.sutd.edu.sg/webapps/portal/execute/tabs/tabAction"):
        self.url = url
        self.webportalurl = webportalurl
        self.jsonfile = jsonfile
        self.dirname = dirname
        self.json_dict = dict()
        self.session = None
        self.on_exit = False  # for __exit__ compatibility

        # if dirname is not absolute,
        # change it to absolute
        if not os.path.isabs(self.dirname):
            self.dirname = os.path.join(utilities.getFileDir(), self.dirname)
        # make dir is dir does not exist
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)
        # get repeat-download json checker file
        # and create file in case it does not exist
        if not os.path.isabs(self.jsonfile):
            self.jsonfile = os.path.join(self.dirname, self.jsonfile)
        codecs.open(self.jsonfile, 'a', encoding="utf-8").close()
        with codecs.open(self.jsonfile, 'r+', encoding="utf-8") as j_f:
            # if dict does not exist, create one
            try:
                self.json_dict = json.load(j_f)
            except ValueError:
                self.json_dict = {}

        # set login payload
        payload = {"user_id": username,
                   "password": password,
                   "persistent": "1"}

        ########################################
        # Required for persistent session access
        self.session = requests.session()
        self.req_with_check("post",
                            self.new_urljoin(self.url,
                                             "/webapps/login/"),
                            data=payload, message="Login success!")
        ########################################

    def run(self):
        r = self.req_with_check("post",
                                self.webportalurl,
                                data={"tab_tab_group_id": "_1_1"})
        login_soup = BeautifulSoup(r.text, "html.parser")
        # get course listing ajax parameters
        div3_1 = login_soup.select_one("#div_3_1")
        div_parent = div3_1.find_parent("div", recursive=False)
        script = div_parent.select_one("script").getText()
        search_res = re.search("'action=.+?'", script)
        parameters = search_res.group(0)[1:-1]
        # format parameters
        parameters = urllib.parse.parse_qs(parameters)
        parameters = {key: parameters[key][0] for key in parameters}

        # get course list xml
        r = self.req_with_check("post",
                                self.webportalurl,
                                data=parameters)
        xml_soup = BeautifulSoup(r.text, "lxml")
        self._courseListingSearch(xml_soup)

        self._on_exit()
        self.on_exit = True

    def _on_exit(self):
        with codecs.open(self.jsonfile, "w") as f:
            json.dump(self.json_dict, f, ensure_ascii=False)

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        if not self.on_exit:
            self._on_exit()

    def text_sanitize(self, text, width=75, placeholder="..."):
        text = text[:width]
        text = text + (placeholder if (len(text) >= width) else '')
        text = text.replace('/', '_').replace('\"', '')
        return text

    def req_with_check(self, method, *args, **kwargs):
        # requests.get with error checking
        message = None
        if "message" in kwargs:
            message = kwargs["message"]
            kwargs.pop("message", None)

        r = getattr(self.session, method)(*args, **kwargs)

        if r.status_code != 200:
            r.raise_for_status()
        else:
            if message:
                print(message)
            else:
                print("Accessed")

        return r

    def new_urljoin(self, url1, url2):
        return urllib.parse.urljoin(str(url1), str(url2))

    def _courseListingSearch(self, soup):
        """
        Searches the .courseListing list for all the links
        to all modules
        """
        print("Searching course listing...")

        course_listing = soup.select_one(".courseListing")

        if not course_listing:
            print("Directory empty.")
        else:
            # To get a formatted version of the module name
            mod_name_format = re.compile(": .+?$")
            for course in course_listing.find_all("li", recursive=False):
                a = course.select_one("a")
                url = a.get("href").strip()
                text = a.getText().strip()
                # Format text
                text = mod_name_format.findall(text)
                text = self.text_sanitize(text[-1][2:])

                # Make dir for each course and access
                abs_course_dir = os.path.join(self.dirname, text)
                if not os.path.isdir(abs_course_dir):
                    os.mkdir(abs_course_dir)

                # Access course
                abs_course_url = self.new_urljoin(self.url, url)
                message = text + " course accessed."
                course_r = self.req_with_check("get", abs_course_url,
                                               message=message)
                course_soup = BeautifulSoup(course_r.text, 'html.parser')

                # search course Menu
                self._courseMenuSearch(course_soup, abs_course_dir)

    def _courseMenuSearch(self, soup, absdir=None):
        # set absdir default
        if not absdir:
            absdir = self.dirname

        print("Searching course menu...")
        course_menu = soup.select_one(".courseMenu")
        course_list = {}

        if not course_menu:
            print("Directory empty.")
        else:
            for course in course_menu.find_all("li", recursive=False):
                a = course.select_one("a")
                url = a.get("href").strip()
                text = a.getText().strip()
                # skip home page
                if text in ("Home Page", "Information", "Discussions",
                            "Groups", "Tools", "Help"):
                    continue
                text = self.text_sanitize(text)
                course_list[text] = url

            # make dir for each link and access
            for link_chosen in course_list:
                abs_link_dir = os.path.join(absdir, link_chosen)
                if not os.path.isdir(abs_link_dir):
                    os.mkdir(abs_link_dir)
                # access course
                link_url = course_list[link_chosen]
                abs_link_url = self.new_urljoin(self.url, link_url)
                message = link_chosen + " link accessed."
                link_r = self.req_with_check("get", abs_link_url,
                                             message=message)
                link_soup = BeautifulSoup(link_r.text, 'html.parser')
                # Search content list
                self._contentListSearch(link_soup, abs_link_dir)

    def _contentListSearch(self, soup, absdir=None):
        # set absdir default
        if not absdir:
            absdir = self.dirname

        print("Searching content list...")
        course_listing = soup.select_one(".contentList")

        if not course_listing:
            print("Directory empty.")
        else:
            for course in course_listing.find_all("li", recursive=False):
                # recursive False: only direct children
                a = course.select_one("a")
                if not a:  # no link
                    continue
                url = a.get("href").strip()
                text_file = self.text_sanitize(a.getText().strip())
                abs_url = self.new_urljoin(self.url, url)
                r = self.req_with_check("get", abs_url, stream=True,
                                        message=text_file + " accessed.")
                # stream=True enables download of content
                # only after content is accessed e.g. r.content
                # check if html
                if "text/html" not in r.headers['content-type']:
                    print(r.headers['content-type'])
                    # get extension of file
                    ext = mimetypes.guess_extension(r.headers['content-type'])
                    # check if course["id"] in self.json_dict
                    print("Looking at " + course["id"])
                    if course["id"] not in self.json_dict:
                        # append course["id"] to self.json_dict for cache
                        self.json_dict[course["id"]] = 1
                        # start download
                        print("Downloading " + course["id"])

                        # path/to/dir/text_file.ext
                        if not text_file.endswith(ext):
                            filename = os.path.join(
                                absdir, text_file + "." + ext)
                        else:
                            filename = os.path.join(absdir, text_file)

                        with open(filename, "wb") as out_file:
                            r.raw.decode_content = True
                            utilities.copyfileobjprint(
                                r.raw, out_file)
                        # print("Magic test:")
                        # print(magic.from_file(filename))
                else:
                    abs_link_dir = os.path.join(absdir, text_file)
                    if not os.path.isdir(abs_link_dir):
                        os.mkdir(abs_link_dir)
                    url_soup = BeautifulSoup(r.text, "html.parser")
                    self._contentListSearch(url_soup, absdir)


class EDException(Exception):
    pass


if __name__ == "__main__":

    USERNAME = None
    PASSWORD = None
    DIRNAME = "testED"
    JSONFILE = "cache.json"

    doc_arguments = docopt(__doc__, version="E Dimension Downloader 1.1")
    if doc_arguments["<username>"]:
        USERNAME = doc_arguments["<username>"]
    else:
        if not USERNAME:
            raise EDException("USERNAME not found.")
    # check password exists
    if doc_arguments["<password>"]:
        PASSWORD = doc_arguments["<password>"]
    else:
        if not PASSWORD:
            raise EDException("PASSWORD not found.")
    # check dirname exists
    if doc_arguments["<dirname>"]:
        DIRNAME = doc_arguments["<dirname>"]
    else:
        if not DIRNAME:
            raise EDException("DIRNAME not found.")
    # check username exists
    if not JSONFILE:  # JSONFILE does not already exist
        JSONFILE = doc_arguments["-j"]
    else:
        if JSONFILE == "cache.json":  # If JSONFILE is the default
            JSONFILE = doc_arguments["-j"]

    with EDimensionDownloader(USERNAME, PASSWORD, DIRNAME, JSONFILE) as ed:
        ed.run()
