## CKG Scrape to MediaWiki

The demo scrapes the content of the IPCC website and stores the data in MediaWiki and Wikibase.

This project depends on [GNU wget](https://www.gnu.org/software/wget/) and [CPS Wikibase](https://wiki.kewl.org/projects:wikibase).

CPS Wikibase uses [Wikibase docker deployment](https://wiki.kewl.org/tools:wikibase#wikibase_docker_deployment).

## CKG

Climate Knowledge Graph tools have been written to make the IPCC report cycle 6 accessible by storing it in MediaWiki and Wikibase.

A Wikibase instance must first be created which will contain both the Wikidata and MediaWiki content.

Once the site is online and configured, custom scripts are utilized to scrape the IPCC site and convert the content to MediaWiki markup.

Finally, using an XML configuration file, Wikibase is populated using keyword tags to allow SPARQL queries to query for related MediaWiki text.

## Wikibase Docker Deployment

Follow the guide for [Wikibase docker deployment](https://wiki.kewl.org/tools:wikibase#wikibase_docker_deployment) but add these extra settings for MediaWiki in `LocalSettings.php`:

```php
$wgEnableUploads = true; # Enable uploads

// Allow images up to 100MB
$wgMaxUploadSize = 104857600;

// Allow page content/wikitext up to 8MB (unit is KiB)
$wgMaxArticleSize = 8192;

$wgShowExceptionDetails = true;

$wgGenerateThumbnailOnParse = false;
$wgThumbnailScriptPath = "{$wgScriptPath}/thumb.php";
```

These settings allow large single-page uploads and stop automatic thumbnail generation when importing images. Thumbnails are generated as required.

## Debian

This process for Debian downloads and sets up the scrape and import scripts.

### Setup

```bash
sudo apt install python3 python3-venv pandoc python3-magic mercurial
hg clone https://hg.kewl.org/pub/ckg_s2mw
cd ckg_s2mw
```

### Create Virtual Environment

```bash
python3 -m venv ~/.venvs/ckg_s2mw
```

or

```bash
make venv
```

### Activate Virtual Environment

TCSH:

```bash
source ~/.venvs/ckg_s2mw/bin/activate.csh
```

BASH:

```bash
source ~/.venvs/ckg_s2mw/bin/activate
```

### Initial Installation

```bash
make install
```

### Update Installation

```bash
hg pull -u
make
```

## Scrape

A script using `wget` is provided with a list of URLs to scrape into a local directory.

For this example the directory is accessible via the web but this is not necessary.

NB: a web scrape is a snapshot in time. There is no guarantee this process is repeatable after the date these scripts were written to work.

### Setup

```bash
mkdir -p /var/www/htdocs/www.example.com/IPCC
cp etc/wget.sh /var/www/htdocs/www.example.com/IPCC
cp etc/urls*txt /var/www/htdocs/www.example.com/IPCC
cd /var/www/htdocs/www.example.com/IPCC
```

### Run

```bash
./wget.sh
```

## Environment

After the scrape is complete, return to the project directory and set up the environment configuration.

This configuration is used by the Python scripts to gain access to the MediaWiki and Wikibase deployment.

```bash
cp dotenv .env
vi .env
```

The config requires setting up a MediaWiki bot password from the wiki at "Special pages -> Account management -> Bot passwords".

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

## Pandoc

Two scripts are provided to parse the Gatsby and WordPress CMS files to produce intermediary wikitext with Pandoc.

These processes contain various hacks, and the resultant output is far from perfect.

```bash
gatsby -l "etc/urls_gatsby.txt"
```

```bash
wordpress -l "etc/urls_wordpress.txt"
```

Both processes are IPCC-site-specific with various workarounds fixing URLs and styling.

## Wikitext

The Pandoc wikitext needs to be processed and cleaned, and this has two stages.

These processes can only be applied once since they modify the Pandoc output files from above.

### Upload

The first parse of the wikitext obtains the media files and uploads them to MediaWiki.

```bash
wikitext -u
```

### Clean

The second process fixes side effects of the Pandoc conversion process, rewrites media file links, and writes the results to disk.

```bash
wikitext -w
```

## MediaWiki

This final wikitext process takes the cleaned-up wikitext files and publishes them on MediaWiki.

```bash
mediawiki -l "etc/urls_gatsby.txt"
```

```bash
mediawiki -l "etc/urls_wordpress.txt"
```

## Wikibase

Using the XML configuration for the IPCC scrape, Wikibase entries are created.

```bash
wbset etc/work.xml
```

Finally, the main MediaWiki page `Main_Page` is written with links to the imported documents.

```bash
work
```
