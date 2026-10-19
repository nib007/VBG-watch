import requests
import smtplib
from email.mime.text import MIMEText

API_URL = "https://jobsearch.api.jobtechdev.se/search"

SEARCHES = [
    "Forskare Proteinkemist Core Facilities",
    "forskningsingenjör protein",
    "research engineer protein"
]

def search_jobs(query):

    r = requests.get(
        API_URL,
        params={
            "q": query,
            "limit": 50
        },
        headers={"accept": "application/json"},
        timeout=30
    )

    r.raise_for_status()

    return r.json().get("hits", [])


jobs = {}

for query in SEARCHES:

    for job in search_jobs(query):

        url = job.get("webpage_url", "")

        if not url:
            continue

        jobs[url] = {
            "title": job.get("headline", ""),
            "employer": job.get(
                "employer",
                {}
            ).get("name", ""),
            "url": url
        }

if not jobs:
    print("No jobs found")
    quit()

html = """
<h2>Protein-related jobs</h2>
<ul>
"""

for job in jobs.values():

    html += f"""
    <li>
    <a href="{job['url']}">
    {job['title']}
    </a>
    - {job['employer']}
    </li>
    """

html += "</ul>"

msg = MIMEText(html, "html")
msg["Subject"] = "Protein Jobs"
msg["From"] = "github-agent"
msg["To"] = EMAIL_TO

with smtplib.SMTP_SSL(
    SMTP_SERVER,
    int(SMTP_PORT)
) as smtp:

    smtp.login(
        SMTP_USER,
        SMTP_PASSWORD
    )

    smtp.send_message(msg)

print(f"Sent {len(jobs)} jobs")
