
import os
import time
import requests
import smtplib
from email.mime.text import MIMEText

API_URL = "https://jobsearch.api.jobtechdev.se/search"

SEARCHES = [
    "protein",
    "protein expression",
    "protein purification",
    "research engineer",
    "forskningsingenjör",
    "core facility",
    "mammalian cell culture",
]

# Retry email delivery up to five times, waiting one hour between attempts.
EMAIL_RETRIES = 5
EMAIL_RETRY_DELAY_SECONDS = 60 * 60

SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


def search_jobs(query):
    response = requests.get(
        API_URL,
        params={
            "q": query,
            "limit": 100
        },
        headers={
            "accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("hits", [])


def calculate_score(job):

    title = job.get("headline", "").lower()

    description = (
        job.get("description", {})
           .get("text", "")
           .lower()
    )

    text = f"{title} {description}"

    score = 0

    # Strong protein relevance

    if "protein" in text:
        score += 20

    if "protein expression" in text:
        score += 20

    if "protein purification" in text:
        score += 20

    if "recombinant protein" in text:
        score += 20

    # Cell culture

    if "mammalian cell culture" in text:
        score += 20

    if "cell culture" in text:
        score += 10

    # Core facilities

    if "core facility" in text:
        score += 25

    if "core facilities" in text:
        score += 25

    # Job titles

    if "research engineer" in title:
        score += 30

    if "forskningsingenjör" in title:
        score += 30

    if "staff scientist" in title:
        score += 25

    if "scientist" in title:
        score += 15

    if "researcher" in title:
        score += 15

    if "forskare" in title:
        score += 15

    # Biology / biochemistry

    bonus_terms = [
        "biochemistry",
        "biokemi",
        "molecular biology",
        "molekylärbiologi",
        "antibody",
        "protein production",
        "bioinformatics",
        "genomics",
        "proteomics",
        "ngs",
        "chromatography",
        "hplc",
        "lc-ms",
        "mass spectrometry"
    ]

    for term in bonus_terms:
        if term in text:
            score += 10

    return score


def build_html(job_list):

    html = """
    <html>
    <body>
    <h2>Protein / Research Engineer Jobs</h2>
    <table border="1" cellpadding="5" cellspacing="0">
    <tr>
        <th>Score</th>
        <th>Title</th>
        <th>Employer</th>
        <th>Location</th>
    </tr>
    """

    for job in job_list:

        html += f"""
        <tr>
            <td>{job['score']}</td>
            <td>
                <a href="{job['url']}">
                {job['title']}
                </a>
            </td>
            <td>{job['employer']}</td>
            <td>{job['city']}</td>
        </tr>
        """

    html += """
    </table>
    </body>
    </html>
    """

    return html


def send_email(html):

    msg = MIMEText(html, "html")

    msg["Subject"] = "Protein / Research Engineer Jobs"
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30
    ) as smtp:

        smtp.login(
            SMTP_USER,
            SMTP_PASSWORD
        )

        smtp.send_message(msg)


def send_email_with_retries(html):
    # Initial attempt plus up to five retries (six attempts total).
    for attempt in range(1, EMAIL_RETRIES + 2):
        try:
            print(f"Sending email (attempt {attempt}/{EMAIL_RETRIES + 1})...")
            send_email(html)
            return
        except Exception as error:
            if attempt > EMAIL_RETRIES:
                print(f"Email delivery failed after {attempt} attempts: {error}")
                raise

            print(
                f"Email attempt {attempt} failed: {error}. "
                f"Retrying in one hour. ({EMAIL_RETRIES - attempt + 1} retries left)"
            )
            time.sleep(EMAIL_RETRY_DELAY_SECONDS)


def main():

    jobs = {}

    for query in SEARCHES:

        print(f"Searching: {query}")

        try:
            results = search_jobs(query)

        except Exception as e:
            print(f"Failed search: {query}")
            print(e)
            continue

        for job in results:

            url = job.get("webpage_url", "")

            if not url:
                continue

            score = calculate_score(job)

            if score < 40:
                continue

            jobs[url] = {
                "title": job.get("headline", ""),
                "employer": (
                    job.get("employer", {})
                       .get("name", "")
                ),
                "city": (
                    job.get(
                        "workplace_address",
                        {}
                    ).get(
                        "municipality",
                        ""
                    )
                ),
                "url": url,
                "score": score
            }

    if not jobs:
        print("No relevant jobs found")
        return

    jobs_list = sorted(
        jobs.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    print(f"Found {len(jobs_list)} relevant jobs")

    html = build_html(jobs_list)

    send_email_with_retries(html)

    print("Email sent")


if __name__ == "__main__":
    main()
