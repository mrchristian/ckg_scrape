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

    if not os.getenv("GATSBY_URL"):
        raise Exception("GATSBY_URL is missing")

    if not os.getenv("GATSBY_ROOT"):
        raise Exception("GATSBY_ROOT is missing")

    if not os.getenv("ASSETS_URL"):
        raise Exception("ASSETS_URL is missing")

    root = os.getenv("GATSBY_ROOT")
    if not root.endswith(os.sep):
        root = root + os.sep

    if not args.list:
        # Create file path
        file = root + args.file

        output(file)
    else:
        print(f"LIST={args.file}", flush=True)

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
    print(f"HTML={file}", flush=True)

    try:
        with open(file, "r") as finput:
            page = finput.read()
    except:
        msg = f"HTML error: {file}"
        raise Exception(msg)

    path, ext = os.path.splitext(file)

    html_tidy = tidy(file, page, False)

    with open(path + ".tidy" + ext, "w", encoding="utf-8") as foutput:
        foutput.write(html_tidy)

    pandoc_tidy = pypandoc.convert_text(html_tidy, to='mediawiki', format='html')

    with open(path + ".tidy.wiki", "w", encoding="utf-8") as foutput:
        foutput.write(pandoc_tidy)

    html_clean = tidy(file, page, True)

    with open(path + ".clean" + ext, "w", encoding="utf-8") as foutput:
        foutput.write(html_clean)

    pandoc_clean = pypandoc.convert_text(html_clean, to='mediawiki', format='html')

    with open(path + ".clean.wiki", "w", encoding="utf-8") as foutput:
        foutput.write(pandoc_clean)

def tidy(file, page_source, clean=False):
    ##################################################################
    # HREF REWRITE
    #
    i = file.find("/index.html")
    if i != -1:
        this = os.getenv("GATSBY_URL") + file[len(os.getenv("GATSBY_ROOT")):i]
    else:
        this = os.getenv("GATSBY_URL")

    if "wg1/chapter/chapter" in file:
        base = os.getenv("GATSBY_URL") + "wg1/chapter/"

    elif "wg2/chapter/chapter" in file:
        base = os.getenv("GATSBY_URL") + "wg2/chapter/"

    elif "wg3/chapter/chapter" in file:
        base = os.getenv("GATSBY_URL") + "wg3/chapter/"

    elif "syr/longer-report" in file:
        base = os.getenv("GATSBY_URL") + "syr/longer-report/"

    else:
        base = None

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
        """
        for tag in soup("html"):
            tag.name = "div"
        for tag in soup("body"):
            tag.name = "div"
        for tag in soup("head"):
            tag.name = "div"
        for tag in soup("title"):
            tag.name = "h1"
        """

        # Remove tags
        for tag in soup("button"):
            tag.decompose()
        for tag in soup("footer"):
            tag.decompose()

        # Remove nearly all tag attributes
        for tag in soup.find_all(True):
            for attr in tag.attrs.copy():

                if tag.name == "a":
                    if attr == "href":
                        if tag[attr].startswith("https://www.ipcc.ch/chapters/chapter"):
                            if not base:
                                print(f"{tag[attr]} => ?", flush=True)
                            else:
                                if "longer-report" in base:
                                    right = tag[attr][38:]
                                else:
                                    right = tag[attr][29:]

                                new = base + right
                                print(f"{tag[attr]} => {new}", flush=True)
                                tag[attr] = new

                        # GATSBY_URL / THIS CHAPTER
                        if tag[attr].startswith(this) or not tag[attr].startswith("http"):

                            if '#' in tag[attr]:
                                # URL Citations
                                i = tag[attr].index('#')
                                tag[attr] = tag[attr][i:]

                            elif not tag[attr].startswith("http"):
                                tag.name = "decompose"

                        elif tag[attr].startswith(os.getenv("GATSBY_URL")) and \
                            not tag[attr].startswith(os.getenv("ASSETS_URL")):
                                tag[attr] = urlmap.urltopath(tag[attr])

                    else:
                        del tag[attr]

                elif tag.name == "p":
                    if attr == "class":
                        #   "Body-copy_Boxes_Blue-Boxes_•-Box-heading", \
                        l = ["Body-copy_•-Body-copy--full-justify--all-bold--BLUE--No-space-below", \
                            "Body-copy_•-Body-copy--full-justify--all-bold--BLUE-", \
                            "TS-Technical-Summary-styles_•-TS-Box-standfirst-with-Blue-sidebar", \
                            "TS-Technical-Summary-styles_•-TS-Standfirst-with-blue-sidebar", \
                            "Body-copy_Boxes_Blue-Boxes_•-Box-subhead-H1---no-space-below", \
                            "Body_Box_blue_Box_head", \
                            "Body_Box_blue_Box_subhead_H2", \
                            "LR-salmon-grey-box", \
                            "SPM-salmon-grey-box" ]
                        for i in l:
                            if i in tag[attr]:
                                tag.name = "b"

                        del tag[attr]

                    elif attr == "id" and not tag[attr].startswith("readmore-"):
                        tag.name = "div"

                    else:
                        del tag[attr]

                elif tag.name == "strong":
                    tag.name = "div"

                elif tag.name == "img":
                    if attr == "class":
                        if "chart-icon" in tag["class"]:
                            tag.name = "decompose"
                        else:
                            del tag[attr]

                    elif attr == "src":
                        if "share.png" in tag["src"]:
                            tag.name = "decompose"
                        if "-icon.png" in tag["src"]:
                            tag.name = "decompose"

                        # else keep

                    elif attr == "data-src":
                        tag["src"] = tag["data-src"]
                        del tag[attr]

                    else:
                        del tag[attr]

                elif tag.name == "td" or tag.name == "th":
                    if attr != "colspan" and attr != "rowspan":
                        del tag[attr]

                elif tag.name == "div":
                    if attr == "class":
                        if "nav2" in tag[attr]:
                             tag.name = "decompose"
                        elif "reflinks" in tag[attr]:
                             tag.name = "decompose"
                        elif "spm-tooltip" in tag[attr]:
                             tag.name = "decompose"
                        elif "related_pages" in tag[attr]:
                             tag.name = "decompose"
                    elif attr == "id":
                        if "chapter-figures" in tag[attr]:
                             tag.name = "decompose"
                        # else keep
                    else:
                        del tag[attr]

                elif tag.name == "span":
                    if attr == "class":

                        lb = ["•-Bold-condensed", \
                            "bold", \
                            "•-Bold-condensed--dark-blue-", \
                            "•-Bold-condensed-subscript", \
                            "•-Bold-Condensed-Subscript--dark-blue", \
                            "bold_condensed", \
                            "bold_condensed-dark-blue", \
                            "figure_number", \
                            "table_number", \
                            "SPM-salmon-grey-box", \
                            "LR-salmon-grey-box", \
                            "CharOverride-3", \
                            "CharOverride-20", \
                            "CharOverride-30", \
                            "CharOverride-37", \
                            "CharOverride-39", \
                            "CharOverride-9" ]

                        li = ["•-Light-condensed-italic", \
                            "•-Light-Condensed-Italic", \
                            "light_condensed_italic", \
                            "•-Condensed-italic", \
                            "condensed_italic", \
                            "•-Regular-Italic", \
                            "CharOverride-4", \
                            "CharOverride-10", \
                            "CharOverride-22" ]

                        lbi = ["•-Bold-Condensed-Italic--dark-blue-", \
                            "bold_condensed_italic", \
                            "CharOverride-18", \
                            "CharOverride-21" ]

                        #<class 'bs4.element.AttributeValueList'>
                        for a in tag[attr]:
                            for i in lb:
                                if i == a:
                                    tag.name = "b"
                            for i in li:
                                if i == a:
                                    tag.name = "i"
                            for i in lbi:
                                if i == a:
                                    tag.name = "b"
                                    text = tag.get_text(strip=True)
                                    tag.clear()
                                    new = soup.new_tag("i")
                                    tag.append(new)
                                    new.string = text

                    del tag[attr]

                else:
                    del tag[attr]

        # Remove decompose
        for tag in soup("decompose"):
            tag.decompose();

        for tag in soup("textarea"):
            tag.decompose();

        # Remove anchor
        for tag in soup("a"):
            # Remove no anchor
            if not tag.get("href"):
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

        # Remove empty div
        for tag in soup("div"):
            if not tag.get_text(strip=True):
                tag.unwrap()

        # Remove empty b
        for tag in soup("b"):
            if not tag.get_text(strip=True):
                tag.unwrap()

        # Remove empty i
        for tag in soup("i"):
            if not tag.get_text(strip=True):
                tag.unwrap()

        # Rename headers
        for tag in soup("h5"):
            tag.name = "H6"
        for tag in soup("h4"):
            tag.name = "H5"
        for tag in soup("h3"):
            tag.name = "H4"
        for tag in soup("h2"):
            tag.name = "H3"
        for tag in soup("h1"):
            tag.name = "H2"

    return soup.prettify(formatter="html")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
