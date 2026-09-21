# CKG Scrape

<p align="left">
	<a href="https://github.com/TIBHannover/climate-knowledge-graph">
		<img src="https://raw.githubusercontent.com/TIBHannover/climate-knowledge-graph/main/images/climatekg-logo.png" alt="ClimateKG logo" width="180">
	</a>
	<img src="https://raw.githubusercontent.com/TIBHannover/climate-knowledge-graph/main/images/tib-logo.png" alt="TIB logo" width="180">
	<img src="https://raw.githubusercontent.com/TIBHannover/climate-knowledge-graph/main/images/semanticclimate-logo.jpg" alt="#semanticClimate logo" width="180">
</p>

<p align="center">
	Funded by the <a href="https://www.tib.eu/en/research-development/project-overview/project-summary/climatekg">TIB Innovation Fund</a>
</p>

CKG Scrape is the data collection and publishing toolkit for the Climate Knowledge Graph project. It turns IPCC AR6 content into MediaWiki pages and Wikibase entries so the knowledge graph can support structured access, document distribution, and analysis.

Main project repository: https://github.com/TIBHannover/climate-knowledge-graph

CKG Scrape software documentation: https://wiki.kewl.org/projects:ckgscrape

## Installation

CKG Scrape: AKA `ckg_s2mw` is a Python package that scrapes IPCC content and prepares it for MediaWiki and Wikibase.

### Prerequisites

- Python 3.9 or newer
- `pip` and `venv`
- `pandoc`
- `wget`
- `mercurial` if you are cloning the original upstream repository
- A MediaWiki / Wikibase instance if you plan to publish content

### Clone the repository

```bash
git clone https://github.com/mrchristian/ckg_scrape.git
cd ckg_scrape
```

If you need the original Mercurial source, clone it with:

```bash
hg clone https://anonymous:anonymous@hg.kewl.org/pub/ckg_s2mw
```

### Create a virtual environment

```bash
python3 -m venv ~/.venvs/ckg_s2mw
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On bash or zsh:

```bash
source ~/.venvs/ckg_s2mw/bin/activate
```

### Install the package

The project Makefile provides the simplest install path:

```bash
make install
```

That installs the package and the extra `dotenv` dependency used by the scripts.

If you prefer `pip` directly:

```bash
python3 -m pip install .
python3 -m pip install dotenv
```

### Configure the MediaWiki and Wikibase environment

The wiki deployment needs a few extra MediaWiki settings for uploads and large pages:

```php
$wgEnableUploads = true;
$wgMaxUploadSize = 104857600;
$wgMaxArticleSize = 8192;
$wgShowExceptionDetails = true;
$wgGenerateThumbnailOnParse = false;
$wgThumbnailScriptPath = "{$wgScriptPath}/thumb.php";
```

Create a local environment file from the template and set your site-specific values:

```bash
cp dotenv .env
```

Typical values include:

```text
MEDIAWIKI_URL="https://www.example.com/wiki/"
MEDIAWIKI_HOST="www.example.com"
MEDIAWIKI_USERNAME="User"
MEDIAWIKI_PASSWORD="mybot@xxx"
GATSBY_URL="https://www.ipcc.ch/report/ar6/"
GATSBY_ROOT="/var/www/htdocs/www.example.com/IPCC/Gatsby/www.ipcc.ch/report/ar6/"
WORDPRESS_URL="https://www.ipcc.ch/"
WORDPRESS_ROOT="/var/www/htdocs/www.example.com/IPCC/WordPress/www.ipcc.ch/"
ASSETS_URL="https://www.ipcc.ch/site/"
CACHE_DIR="/var/www/htdocs/www.example.com/IPCC/assets/"
```

### Next steps

Once installed and configured, the main workflow is:

```bash
gatsby -l "etc/urls_gatsby.txt"
wordpress -l "etc/urls_wordpress.txt"
wikitext -u
wikitext -w
mediawiki -l "etc/urls_gatsby.txt"
mediawiki -l "etc/urls_wordpress.txt"
wbset etc/work.xml
```

For the full project background and operational notes, see the wiki page above.

License: [GPL-3.0-or-later](LICENSE)
