#!/usr/bin/env bash

RSS="https://www.ttela.se/?rss"

echo "START"
date

curl -L --compressed -s "$RSS" | head -20

echo "END"
