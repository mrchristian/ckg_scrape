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

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator import wbi_login
from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.wbi_config import config as wbi_config

from dotenv import load_dotenv

def main():
    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("WB_URL"):
        raise Exception("MB_URL is missing")

    if not os.getenv("WB_USERNAME"):
        raise Exception("WB_USERNAME is missing")

    if not os.getenv("WB_PASSWORD"):
        raise Exception("WB_PASSWORD is missing")

    wbi_config["DEFAULT_LANGUAGE"] = "en"
    wbi_config["WIKIBASE_URL"] = os.getenv("WB_URL")
    wbi_config["MEDIAWIKI_API_URL"] = os.getenv("WB_URL") + "w/api.php"
    wbi_config["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

    PROPERTY_ID = 'P30'
    WRONG_DOMAIN = 'wikibase.runstop.uk'

    item_ids = [f"Q{i}" for i in range(1, 561)]

    for qid in item_ids:
        try:
            item = wbi.item.get(entity_id=qid)

            if PROPERTY_ID in item.claims.claims:
                removed = False

                for claim in item.claims.claims[PROPERTY_ID]:

                    url = claim.mainsnak.datavalue['value']

                    if WRONG_DOMAIN in url:
                        claim.remove()
                        removed = True

                if removed:
                        item.write(summary=f"IPCC")

        except Exception as e:
            print(f"Skipping {qid} (Could be the missing item or an error): {str(e)}")

if __name__=="__main__":
    main()
