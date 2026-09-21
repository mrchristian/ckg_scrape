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

from ckg_s2mw.url import URL

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=str, help="list of URLs, else HTML")
    parser.add_argument("-l", "--list", action="store_true", help="file is a list of URLs, else HTML")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("MEDIAWIKI_USERNAME"):
        raise Exception("MEDIAWIKI_USERNAME is missing")

    if not os.getenv("MEDIAWIKI_PASSWORD"):
        raise Exception("MEDIAWIKI_PASSWORD is missing")

    if not os.getenv("MEDIAWIKI_URL"):
        raise Exception("MW_URL is missing")

    if not os.getenv("MEDIAWIKI_HOST"):
        raise Exception("MW_HOST is missing")

    if not os.getenv("GATSBY_ROOT"):
        raise Exception("GATSBY_ROOT is missing")

    if not os.getenv("WORDPRESS_ROOT"):
        raise Exception("WORDPRESS_ROOT is missing")

    if not args.list:
        gatsby = os.getenv("GATSBY_ROOT")
        if not gatsby.endswith(os.sep):
            gatsby += os.sep
        gatsby += args.file

        wordpress = os.getenv("WORDPRESS_ROOT")
        if not wordpress.endswith(os.sep):
            wordpress += os.sep
        wordpress += args.file

        if os.path.isfile(gatsby):
            file = gatsby

        elif os.path.isfile(wordpress):
            file = wordpress

        else:
            msg = f"File error: {args.file}"
            raise Exception(msg)

        postfile(file)
    else:
        print(f"LIST={args.file}")

        # URL mapper
        urlmap = URL()

        try:
            with open(args.file, "r") as f:
                for line in f:
                    l = line.strip()
                    if not l:
                        continue

                    # Create file path
                    file = urlmap.urltowiki(l)

                    postfile(file)
        except:
            msg = f"List error: {args.file}"
            raise Exception(msg)

def postfile(file):
    print(f"WIKI={file}")

    try:
        with open(file, "r") as f:
            mediawiki = f.read()
    except:
        msg = f"File error: {file}"
        raise Exception(msg)

    site = mwclient.Site(os.getenv("MEDIAWIKI_HOST"), connection_options={'timeout': 120})

    site.login(os.getenv("MEDIAWIKI_USERNAME"), os.getenv("MEDIAWIKI_PASSWORD"))

    # URL mapper
    urlmap = URL()

    wikipath = urlmap.pathtowiki(file)

    print(f"URL={os.getenv('MEDIAWIKI_URL')}{wikipath}")

    page = site.pages[wikipath]

    page.save(mediawiki, summary="IPCC")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
