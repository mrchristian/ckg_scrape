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
import os
import pypandoc

from bs4 import BeautifulSoup

from dotenv import load_dotenv

from ckg_s2mw.url import URL

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=str, help="list of URLs, else HTML")
    parser.add_argument("-l", "--list", action="store_true", help="file is a list of URLs, else HTML")

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("WORDPRESS_URL"):
        raise Exception("WORDPRESS_URL is missing")

    if not os.getenv("WORDPRESS_ROOT"):
        raise Exception("WORDPRESS_ROOT is missing")

    if not os.getenv("ASSETS_URL"):
        raise Exception("ASSETS_URL is missing")

    root = os.getenv("WORDPRESS_ROOT")
    if not root.endswith(os.sep):
        root = root + os.sep

    if not args.list:
        # Create file path
        file = root + args.file

        output(file)
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
                    file = urlmap.urltoindex(l)

                    output(file)
        except:
            msg = f"List error: {args.file}"
            raise Exception(msg)

def output(file):
    print(f"HTML={file}")

    try:
        with open(file, "r") as finput:
            page = finput.read()
    except:
        msg = f"HTML error: {file}"
        raise Exception(msg)

    path, ext = os.path.splitext(file)

    html_tidy = tidy(page, False)

    with open(path + ".tidy" + ext, "w", encoding="utf-8") as foutput:
        foutput.write(html_tidy)

    pandoc_tidy = pypandoc.convert_text(html_tidy, to='mediawiki', format='html')

    with open(path + ".tidy.wiki", "w", encoding="utf-8") as foutput:
        foutput.write(pandoc_tidy)

    html_clean = tidy(page, True)

    with open(path + ".clean" + ext, "w", encoding="utf-8") as foutput:
        foutput.write(html_clean)

    pandoc_clean = pypandoc.convert_text(html_clean, to='mediawiki', format='html')

    with open(path + ".clean.wiki", "w", encoding="utf-8") as foutput:
        foutput.write(pandoc_clean)

def tidy(page_source, clean=False):
    ##################################################################
    # Extract HTML
    #
    soup = BeautifulSoup(page_source, "html.parser")

    ##################################################################
    # Tidy HTML
    #

    # Remove some tags with text
    for tag in soup("noscript"):
        tag.decompose()
    for tag in soup("script"):
        tag.decompose()
    for tag in soup("style"):
        tag.decompose()
    for tag in soup("link"):
        tag.decompose()
    for tag in soup("meta"):
        tag.decompose()

    ##################################################################
    # Clean HTML
    #

    # Clean tags and attributes
    if clean:
        # URL mapper
        urlmap = URL()

        # Rename tags
        for tag in soup("html"):
            tag.name = "div"
        for tag in soup("body"):
            tag.name = "div"
        for tag in soup("head"):
            tag.name = "div"
        for tag in soup("title"):
            tag.name = "h1"

        # Remove tags
        for tag in soup("nav"):
            tag.decompose()
        for tag in soup("footer"):
            tag.decompose()

        # Remove nearly all tag attributes
        for tag in soup.find_all(True):
            for attr in tag.attrs.copy():

                if tag.name == "i":
                    if attr == "class":
                        # Decompose italic later
                        if "icon" in tag[attr]:
                            tag.name = "decompose"

                elif tag.name == "main":
                    tag.name = "div"

                elif tag.name == "a":
                    if attr == "class":
                        # Decompose anchors later
                        if "footnote-return" in tag[attr]:
                            tag.name = "decompose"
                        elif "figure-dl-link" in tag[attr]:
                            tag.name = "decompose"
                    elif attr == "href":
                        if "index.html#" in tag[attr]:
                            # Citations
                            i = tag[attr].index('#')
                            tag[attr] = tag[attr][i:]

                        elif tag[attr].startswith(os.getenv("WORDPRESS_URL")) and \
                                not tag[attr].startswith(os.getenv("ASSETS_URL")):
                            tag[attr] = urlmap.urltopath(tag[attr])
                    else:
                        del tag[attr]

                elif tag.name == "li":
                    if attr != "id":
                        del tag[attr]

                elif tag.name == "img":
                    if attr != "src":
                        if attr == "data-src":
                            tag["src"] = tag["data-src"]
                        del tag[attr]

                elif tag.name == "td" or tag.name == "th":
                    if attr != "colspan" and attr != "rowspan":
                        del tag[attr]

                elif tag.name.startswith('h'):
                    if attr == "class":
                        if "section-number" in tag[attr]:
                            tag.name = "span"
                        elif "section-title" in tag[attr]:
                            tag.name = "span"
                    del tag[attr]

                elif tag.name == "div":
                    if attr == "class":
                        # Preserve class
                        if "type-box" in tag[attr]:
                            tag["class"] = "box"
                        # Rename tag and remove class
                        elif "section-text" in tag[attr]:
                            tag.name = "h2"
                            del tag[attr]
                        # Decompose div later
                        elif "social-menu" in tag[attr]:
                             tag.name = "decompose"
                        elif "share-wrap" in tag[attr]:
                            tag.name = "decompose"
                        # Remove class
                        else:
                            del tag[attr]
                    elif attr == "id":
                        if "chapter-media" in tag[attr]:
                            tag.name = "decompose"
                        elif "chapter-faq" in tag[attr]:
                            tag.name = "decompose"
                        # else keep
                    else:
                        del tag[attr]

                else:
                    del tag[attr]

        # Remove anchor
        for tag in soup("a"):
            # Remove no anchor
            if not tag.get("href"):
                tag.unwrap()

        # Remove figurecaption
        for tag in soup("figcaption"):
            tag.unwrap()

        # Remove no img source
        for tag in soup("img"):
            if not tag.get("src"):
                tag.unwrap()

        # Remove input
        for tag in soup("input"):
            tag.unwrap()

        # Remove span
        for tag in soup("span"):
            tag.unwrap()

        # Remove source
        for tag in soup("source"):
            tag.unwrap()

        # Remove picture
        for tag in soup("picture"):
            tag.unwrap()

        # Remove decompose
        for tag in soup("decompose"):
            tag.decompose();

        # Remove empty div
        for tag in soup("div"):
            if not tag.get_text(strip=True):
                tag.unwrap()

        # Remove empty header
        for tag in soup("header"):
            if not tag.get_text(strip=True):
                tag.unwrap()

    return soup.prettify(formatter="html")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
