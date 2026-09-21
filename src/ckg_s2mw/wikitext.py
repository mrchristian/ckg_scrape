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
import hashlib
import magic
import mwclient
import os
import re
import requests
import sys

from dotenv import load_dotenv

from ckg_s2mw.url import URL

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

cache_dir = None

def main():
    global cache_dir

    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=str, help="WIKI file else recurse directories", nargs='?')

    parser.add_argument("-w", "--write", action="store_true", help="Write wiki file(s)")
    parser.add_argument("-u", "--upload", action="store_true", help="Upload wiki file(s)")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("GATSBY_ROOT"):
        raise Exception("GATSBY_ROOT is missing")

    if not os.path.isdir(os.getenv("GATSBY_ROOT")):
        msg = f"GATSBY_ROOT not found"
        raise Exception(msg)

    if not os.getenv("WORDPRESS_ROOT"):
        raise Exception("WORDPRESS_ROOT is missing")

    if not os.path.isdir(os.getenv("WORDPRESS_ROOT")):
        msg = f"WORDPRESS_ROOT not found"
        raise Exception(msg)

    if not os.getenv("MEDIAWIKI_USERNAME"):
        raise Exception("MEDIAWIKI_USERNAME is missing")

    if not os.getenv("MEDIAWIKI_PASSWORD"):
        raise Exception("MEDIAWIKI_PASSWORD is missing")

    if not os.getenv("MEDIAWIKI_HOST"):
        raise Exception("MW_HOST is missing")

    if not os.getenv("CACHE_DIR"):
        raise Exception("CACHE_DIR is missing")

    cache_dir = os.getenv("CACHE_DIR")
    if not cache_dir.endswith(os.sep):
        cache_dir += os.sep

    """
    site = mwclient.Site(os.getenv("MEDIAWIKI_HOST"))
    site.login(os.getenv("MEDIAWIKI_USERNAME"), os.getenv("MEDIAWIKI_PASSWORD"))
    for image in site.allpages(namespace=6):
        print(f"Unlinking: {image.name}")
        image.delete(reason="Wiping for fresh start")
    sys.exit(0)
    """

    if args.file:
        output(args.file, args.write, args.upload)
    else:
        print(f"RECURSE")
        for root, dirs, files in os.walk(os.getenv("GATSBY_ROOT")):
            for file in files:
                if file.lower().endswith("clean.wiki"):
                    output(root + os.sep + file, args.write, args.upload)

        for root, dirs, files in os.walk(os.getenv("WORDPRESS_ROOT")):
            for file in files:
                if file.lower().endswith("clean.wiki"):
                    output(root + os.sep + file, args.write, args.upload)

def output(file, write=False, upload=False):
    print(f"FILE = {file}, WRITE = {write}, UPLOAD = {upload}", flush=True)
    try:
        f = open(file, "r", encoding="utf-8")
    except:
        raise Exception("Invalid file")

    words = [
        "== '''Acknow''' '''ledgements",
        "== '''Ex''' '''ecutive",
        "== '''Exe''' '''cutive",
        "== '''Executi''' '''ve",
        "'''A g''' '''ender",
        "''''''Attr''' '''ibution",
        "'''C''' '''ase",
        "'''Ca''' '''se",
        "'''Cha''' '''pter",
        "'''Chap''' '''ter",
        "'''Chapter Sc''' '''ientists",
        "'''Contri''' '''buting",
        "'''Contrib''' '''uting",
        "'''Coordinatin''' '''g",
        "'''Coordinating Lea''' '''d",
        "'''F''' '''AQ",
        "'''Fi''' '''gure",
        "'''Fig''' '''ure",
        "'''Figu''' '''re",
        "'''Figur''' '''e",
        "'''Frame''' '''work",
        "'''Gov''' '''ernance",
        "'''I''' '''ncreasing",
        "'''Lea''' '''d",
        "'''Nexu''' '''s",
        "''''''Observ''' '''ed",
        "'''Po''' '''licy",
        "''''''Precipi''' '''tation",
        "'''T''' '''able",
        "''''''Tempe''' '''rature",
    ]

    page = ''
    last = ''

    for line in f:
        l = line.strip()
        if l == last:
            continue

        # FIX DIV
        if "<div" in l:
            if "id=" in l and ">" in l:
                if not l.endswith("</div>"):
                    l += "</div>"
            else:
                continue
        elif "<div>" in l:
            continue
        elif "</div>" in l:
            continue

        # REMOVE [[IPCC:...Figures...]]
        regex = r"\[\[IPCC:[^\]]*Figures:[^\]]+\]\]"
        matches = re.findall(regex, l)
        if matches:
            """
            for match in matches:
                parts = match.strip("[]|").split(":")
                url = f"https://www.ipcc.ch/report/ar6/{parts[1].lower()}/figures/{parts[3].lower()}/{parts[4].lower()}"
                print(f"{match} => {url}", flush=True)
            """
            l = re.sub(regex, ' ', l).strip()
            if not l:
                continue

        # REMOVE [[File:...web-resources...]]
        regex = r"\[\[File:[^\]]*-web-resources\/image\/[^\]]+\]\]"
        matches = re.findall(regex, l)
        if matches:
            """
            for match in matches:
                print(f"{match}", flush=True)
            """
            l = re.sub(regex, ' ', l).strip()
            if not l or l == "|":
                continue

        # [[File:...]]
        regex = r"\[\[File:[^\]]+\]\]"
        matches = re.findall(regex, l)
        for match in matches:
            if not "thumb|400x300px" in match:
                url = imageurl(file, match)
                if url:
                    md5 = hashlib.md5(match.encode()).hexdigest()
                    wikifile = md5 + " " + os.path.basename(match[7:-2])
                    imagecache(wikifile, url, upload)
                    l = l.replace(match, f"[[File:{wikifile}|thumb|400x300px]]", count=1)
            else:
                print(f"MATCH = {match}")

        # REPLACE ''' '''
        for x in words:
            if l.startswith(x):
                l = l.replace("''' '''", "", count=1)

        # ENSURE TRIMMED
        l = l.strip()

        # LAST LINE
        t = last
        last = l

        # WALL OF TEXT FIX
        if l and t:
            ts = t.startswith(("'", '=', '*', '#', ':', ';', '{', '|', '!', '<', '['))
            te = t.endswith((">"))
            ls = l.startswith(("'", '=', '*', '#', ':', ';', '{', '|', '!', '<', '['))
            le = l.endswith((">"))
            if not ts and not te and not ls and not le and t[:1].isalnum():
                l = "<br/><br/>\n" + l

        page = page + l + "\n"

    f.close()

    if write:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(page)

def imageurl(sourcefile, path):
    url = None

    if "Gatsby" in sourcefile:
        if not path.startswith("[[File:https://"):
            if path.startswith("[[File:downloads/"):
                url = "https://www.ipcc.ch/report/ar6/" + sourcefile[len(os.getenv("GATSBY_ROOT")):-35] + \
                    path[7:-2]
            else:
                url = "https://www.ipcc.ch/report/ar6/" + sourcefile[len(os.getenv("GATSBY_ROOT")):-16] + \
                    path[7:-2]
        else:
            url = path[7:-2]
            if url == "https://ipcc.ch/report/ar6/wg3/downloads/figures/IPCC_AR6_SYR_Table_Figure_2_5.png":
                url = "https://www.ipcc.ch/report/ar6/wg1/downloads/figures/IPCC_AR6_WGI_Figure_8_10.png"
            elif url == "https://ipcc.ch/report/ar6/wg2/downloads/figures/IPCC_AR6_WGII_Figure_TS_013a":
                url = "https://ipcc.ch/report/ar6/wg2/downloads/figures/IPCC_AR6_WGII_Figure_TS_013a.png"

    elif "WordPress" in sourcefile:
        if not path.startswith("[[File:https://"):
            m1 = "[[File:../../../site/assets/uploads/sites/"
            m2 = "[[File:../../../../site/assets/uploads/sites/"
            if path.startswith(m1):
                url = "https://www.ipcc.ch/site/assets/uploads/sites/" + path[len(m1):-2]
            elif path.startswith(m2):
                url = "https://www.ipcc.ch/site/assets/uploads/sites/" + path[len(m2):-2]
        else:
            url = path[7:-2]

    return url

# DOWNLOAD AND CACHE IMAGE
def imagecache(wikifile, url, upload=False):
    print(f"CACHE = {wikifile} UPLOAD = {upload}")

    cachefile = cache_dir + wikifile

    if not os.path.isfile(cachefile) or os.path.getsize(cachefile) == 0:
        header = {"User-Agent": _USER_AGENT}
        try:
            response = requests.get(url, headers=header, stream=True)
        except:
            msg = f"REQUEST FAILED [{url}]"
            raise Exception(msg)

        try:
            with open(cachefile, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
        except:
            msg = f"WRITE FAILED [{cachefile}]"
            raise Exception(msg)

    type = magic.from_file(cachefile, mime=True)
    if not type.startswith("image/"):
        print(f"ERROR = {url}", file=sys.stderr)
        os.unlink(cachefile)

    elif upload:
        site = mwclient.Site(os.getenv("MEDIAWIKI_HOST"))
        site.login(os.getenv("MEDIAWIKI_USERNAME"), os.getenv("MEDIAWIKI_PASSWORD"))
        try:
            with open(cachefile, 'rb') as f:
                site.upload(file=f, filename=wikifile, comment="IPCC", ignore=True)
            print(f"UPLOADED = {wikifile}", file=sys.stderr)
        except:
            print(f"DUPLICATE = {wikifile}", file=sys.stderr)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
