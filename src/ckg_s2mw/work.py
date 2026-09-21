#! /usr/bin/env python
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
import argparse
import mwclient
import os
import time

from dotenv import load_dotenv

def main():
    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("MEDIAWIKI_USERNAME"):
        raise Exception("MEDIAWIKI_USERNAME is missing")

    if not os.getenv("MEDIAWIKI_PASSWORD"):
        raise Exception("MEDIAWIKI_PASSWORD is missing")

    if not os.getenv("MEDIAWIKI_URL"):
        raise Exception("MW_URL is missing")

    if not os.getenv("MEDIAWIKI_HOST"):
        raise Exception("MW_HOST is missing")

    postfile("etc/work.wiki");

def postfile(file):
    try:
        with open(file, "r") as f:
            mediawiki = f.read()
    except:
        msg = f"File error: {file}"
        raise Exception(msg)

    site = mwclient.Site(os.getenv("MEDIAWIKI_HOST"), connection_options={'timeout': 120})

    site.login(os.getenv("MEDIAWIKI_USERNAME"), os.getenv("MEDIAWIKI_PASSWORD"))

    page = site.pages["IPCC"]

    page.save(mediawiki, summary="IPCC")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
