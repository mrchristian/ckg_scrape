#! /usr/bin/env python3
#
# Copyright (C) 2025 Darron Broad
# All rights reserved.
#
# This file is part of ckg_s2mw.
#
# ckg_s2mw is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# ckg_s2mw is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with ckg_s2mw. If not, see http://www.gnu.org/licenses/
#
import os

from dotenv import load_dotenv

from pathlib import Path

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    pass

class URL:
    def __init__(self):
        load_dotenv(os.getcwd() + os.sep + ".env")

        if not os.getenv("GATSBY_URL"):
            raise Exception("GATSBY_URL is missing")

        if not os.getenv("GATSBY_ROOT"):
            raise Exception("GATSBY_ROOT is missing")

        if not os.getenv("WORDPRESS_URL"):
            raise Exception("WORDPRESS_URL is missing")

        if not os.getenv("WORDPRESS_ROOT"):
            raise Exception("WORDPRESS_ROOT is missing")

    def pathtowiki(self, path):
        if path.startswith(os.getenv("GATSBY_ROOT")):
            path = path.replace(os.getenv("GATSBY_ROOT"), "")

        elif path.startswith(os.getenv("WORDPRESS_ROOT")):
            path = path.replace(os.getenv("WORDPRESS_ROOT"), "")

        else:
            msg = f"Path error: {path}"
            raise Exception(msg)

        wikipath = "IPCC"

        path = Path(path)
        for d in path.parts[:-1]:
            wikipath = wikipath + ":" + d.capitalize()

        return wikipath

    def urltopath(self, url):
        if url.startswith(os.getenv("GATSBY_URL")):
            path = url.replace(os.getenv("GATSBY_URL"), "")

        elif url.startswith(os.getenv("WORDPRESS_URL")):
            path = url.replace(os.getenv("WORDPRESS_URL"), "")

        else:
            msg = f"URL error: {url}"
            raise Exception(msg)

        wikipath = "IPCC"

        path = Path(path)
        for d in path.parts:
            wikipath = wikipath + ":" + d.capitalize()

        return wikipath

    def urltoindex(self, url):
        if url.startswith(os.getenv("GATSBY_URL")):
            path = url.replace(os.getenv("GATSBY_URL"), "")

            if path.endswith('/'):
                path += "index.html"
            else: # summary-for-policymakers.html
                path += ".html"

            file = os.getenv("GATSBY_ROOT") + path
            if os.path.isfile(file):
                return file

            msg = f"URL error: {url} {path}"
            raise Exception(msg)

        elif url.startswith(os.getenv("WORDPRESS_URL")):
            path = url.replace(os.getenv("WORDPRESS_URL"), "")

            if path.endswith('/'):
                path += "index.html"
            else:
                path += "/index.html"

            file = os.getenv("WORDPRESS_ROOT") + path
            if os.path.isfile(file):
                return file

            msg = f"URL error: {url} {path}"
            raise Exception(msg)

        msg = f"URL error: {url}"
        raise Exception(msg)

    def urltowiki(self, url):
        if url.startswith(os.getenv("GATSBY_URL")):
            path = url.replace(os.getenv("GATSBY_URL"), "")

            if path.endswith('/'):
                path += "index.clean.wiki"
            else: # summary-for-policymakers.html
                path += ".clean.wiki"

            file = os.getenv("GATSBY_ROOT") + path
            if os.path.isfile(file):
                return file

            msg = f"FILE error: {file}"
            raise Exception(msg)

        elif url.startswith(os.getenv("WORDPRESS_URL")):
            path = url.replace(os.getenv("WORDPRESS_URL"), "")

            if path.endswith('/'):
                path += "index.clean.wiki"
            else:
                path += "/index.clean.wiki"

            file = os.getenv("WORDPRESS_ROOT") + path
            if os.path.isfile(file):
                return file

            msg = f"FILE error: {file}"
            raise Exception(msg)

        msg = f"URL error: {url}"
        raise Exception(msg)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
