import os
import requests
import smtplib
from email.mime.text import MIMEText

# =========================
# Configuration
# =========================

API_URL = "https://jobsearch.api.jobtechdev.se/search"

SEARCHES = [
    "Forskare Proteinkemist Core Facilities",
    "forskningsingenjör protein",
    "research engineer protein"
]

SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

# =========================
# Functions
# =========================

def search_jobs(query):
    print(f"Searching: {query}")

    r = requests.get(
        API_URL,
        params={
            "q": query,
            "limit": 50
        },
        headers={
            "accept": "application/json"
        },
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    return data.get("hits", [])


# =========================
# Collect jobs
# =========================

jobs = {}

for query in SEARCHES:

    try:
        results = search_jobs(query)

        for job in results:

            url = job.get("webpage_url", "")

            if not url:
                continue

            jobs[url] = {
                "title": job.get("headline", "No title"),
                "employer": job.get(
                    "employer",
                    {}
                ).get("name", "Unknown employer"),
                "url": url
            }

    except Exception as e:
        print(f"Error searching '{query}': {e}")

# =========================
# Build email
# =========================

if not jobs:
    print("No jobs found.")
    exit(0)

html = """
<h2>Protein-related jobs</h2>
<ul>
"""

for job in jobs.values():

    html += f"""
    <li>
        <a href="{job['url']}">{job['title']}</a>
        - {job['employer']}
    </li>
    """

html += "</ul>"

msg = MIMEText(html, "html")

msg["Subject"] = f"Protein Jobs ({len(jobs)})"
msg["From"] = SMTP_USER
msg["To"] = EMAIL_TO

# =========================
# Send email
# =========================

print("Connecting to SMTP server...")

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:

    smtp.ehlo()

    smtp.starttls()

    smtp.ehlo()

    smtp.login(
        SMTP_USER,
        SMTP_PASSWORD
    )

    smtp.send_message(msg)

print(f"Sent {len(jobs)} jobs to {EMAIL_TO}")

