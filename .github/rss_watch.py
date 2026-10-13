import requests
import xml.etree.ElementTree as ET
import re

RSS = "https://www.ttela.se/?rss"

KEYWORDS = [
    "Belfragegatan",
    "Sikhall",
    "Gestad",
    "Vita Sannar",
    "Bråna"
]

print("=" * 60)
print("TTELA WATCH")
print("=" * 60)

rss = requests.get(RSS, timeout=30)
rss.raise_for_status()

root = ET.fromstring(rss.text)

matches_found = False

for item in root.findall(".//item"):

    title = item.findtext("title", "")
    link = item.findtext("link", "")

    try:
        page = requests.get(link, timeout=30).text
    except Exception as e:
        print(f"ERROR reading {link}: {e}")
        continue

    hits = []

    for keyword in KEYWORDS:
        count = len(
            re.findall(
                re.escape(keyword),
                page,
                flags=re.IGNORECASE
            )
        )

        if count:
            hits.append(f"{keyword} ({count})")

    if hits:
        matches_found = True

        print()
        print("-" * 60)
        print("MATCH FOUND")
        print(f"TITLE: {title}")
        print(f"URL:   {link}")
        print("HITS:")
        print(", ".join(hits))

if not matches_found:
    print()
    print("NO MATCHES FOUND")
