#! /bin/bash

WGET () {
	wget \
	--server-response \
	--no-verbose \
	--adjust-extension \
	--convert-links \
	--force-directories \
	--backup-converted \
	--compression=auto \
	-e robots=off \
	--restrict-file-names=unix \
	--timeout=30 \
	--tries=2 \
	--warc-file=warc \
	--page-requisites \
	--no-check-certificate \
	--no-hsts \
	--no-parent \
	--mirror \
	--recursive \
	--warc-file=$(date +%s) \
	--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36" \
	"$1"
}

mkdir Gatsby
cd Gatsby
while read -r "URL"; do
	if test -n "$URL"; then
		WGET "$URL"
	fi
done < ../urls_gatsby.txt
cd ..

mkdir WordPress
cd WordPress
while read -r "URL"; do
	if test -n "$URL"; then
		WGET "$URL"
	fi
done < ../urls_wordpress.txt
cd ..

exit 0
