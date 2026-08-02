"""
Each fetch_* function returns a list of raw dicts:
{title, company, location, url, posted, source, kind}
kind is 'job' or 'client'. No filtering/scoring happens here.
"""

import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

HEADERS = {"User-Agent": "JobScoutCLI/1.0 (personal job search tool)"}
# Reddit rate-limits generic UAs hard — use something descriptive.
REDDIT_HEADERS = {"User-Agent": "python:jobscout-cli:1.0 (personal use)"}
TIMEOUT = 15
MAX_RETRIES = 2
RETRY_BACKOFF = 1.5  # seconds, doubles each retry


def _safe_get(url, params=None, headers=None, retries=MAX_RETRIES):
    headers = headers or HEADERS
    delay = RETRY_BACKOFF
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 429 and attempt < retries:
                print(f" [warn] rate limited on {url}, retrying in {delay:.1f}s")
                time.sleep(delay)
                delay *= 2
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            print(f" [warn] request failed for {url}: {e}")
            return None


def fetch_remotive(category_key: str, remotive_category: str, search: str = ""):
    resp = _safe_get("https://remotive.com/api/remote-jobs", params={"category": remotive_category, "search": search})
    if not resp:
        return []
    jobs = resp.json().get("jobs", [])
    out = []
    for j in jobs:
        out.append({
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("candidate_required_location", ""),
            "url": j.get("url", ""),
            "posted": j.get("publication_date", ""),
            "source": "remotive",
            "kind": "job",
        })
    return out


def fetch_remoteok(tags):
    resp = _safe_get("https://remoteok.com/api")
    if not resp:
        return []
    try:
        data = resp.json()
    except ValueError:
        return []
    out = []
    for j in data:
        if not isinstance(j, dict) or "position" not in j:
            continue
        job_tags = [t.lower() for t in j.get("tags", [])]
        if tags and not any(t.lower() in job_tags for t in tags):
            continue
        out.append({
            "title": j.get("position", ""),
            "company": j.get("company", ""),
            "location": j.get("location", "Remote"),
            "url": j.get("url", ""),
            "posted": j.get("date", ""),
            "source": "remoteok",
            "kind": "job",
        })
    return out


def fetch_arbeitnow(search: str):
    resp = _safe_get("https://arbeitnow.com/api/job-board-api")
    if not resp:
        return []
    jobs = resp.json().get("data", [])
    out = []
    search_l = search.lower()
    for j in jobs:
        title = j.get("title", "")
        tags = " ".join(j.get("tags", []))
        haystack = f"{title} {tags}".lower()
        if search_l and search_l not in haystack:
            continue
        out.append({
            "title": title,
            "company": j.get("company_name", ""),
            "location": j.get("location", "Remote"),
            "url": j.get("url", ""),
            "posted": str(j.get("created_at", "")),
            "source": "arbeitnow",
            "kind": "job",
        })
    return out


def fetch_jobicy(tag: str):
    resp = _safe_get("https://jobicy.com/api/v2/remote-jobs", params={"count": 30, "tag": tag})
    if not resp:
        return []
    try:
        jobs = resp.json().get("jobs", [])
    except ValueError:
        return []
    out = []
    for j in jobs:
        out.append({
            "title": j.get("jobTitle", ""),
            "company": j.get("companyName", ""),
            "location": j.get("jobGeo", "Remote"),
            "url": j.get("url", ""),
            "posted": j.get("pubDate", ""),
            "source": "jobicy",
            "kind": "job",
        })
    return out


def fetch_wwr_rss(feed_url: str):
    resp = _safe_get(feed_url)
    if not resp:
        return []
    out = []
    try:
        root = ET.fromstring(resp.content)
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            out.append({
                "title": title,
                "company": "",
                "location": "Remote",
                "url": link,
                "posted": pub,
                "source": "weworkremotely",
                "kind": "job",
            })
    except ET.ParseError:
        print(f" [warn] weworkremotely feed didn't parse as XML — check {feed_url}")
    return out


def fetch_reddit(subreddit: str):
    """Reddit's public RSS feed for a subreddit. Atom format, no login needed."""
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss"
    resp = _safe_get(url, headers=REDDIT_HEADERS)
    if not resp:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    out = []
    try:
        root = ET.fromstring(resp.content)
        for entry in root.findall("atom:entry", ns):
            title = entry.findtext("atom:title", "", ns)
            if title.upper().startswith("[FORHIRE]"):
                continue  # someone offering services, not hiring — skip
            link_el = entry.find("atom:link", ns)
            link = link_el.get("href") if link_el is not None else ""
            updated = entry.findtext("atom:updated", "", ns)
            out.append({
                "title": title,
                "company": f"r/{subreddit}",
                "location": "Remote",
                "url": link,
                "posted": updated,
                "source": "reddit",
                "kind": "client",
            })
    except ET.ParseError:
        print(f" [warn] r/{subreddit} feed didn't parse — likely rate-limited or blocked")
    return out


def fetch_upwork_rss(search_term: str):
    """Upwork's public RSS job-search feed. Note: Upwork has increasingly
    required auth on this endpoint, so a 0-result run may mean the feed is dead,
    not that there are no matches."""
    url = f"https://www.upwork.com/ab/feed/jobs/rss?q={quote(search_term)}&sort=recency"
    resp = _safe_get(url)
    if not resp:
        return []
    if b"<rss" not in resp.content[:500] and b"<?xml" not in resp.content[:100]:
        print(f" [warn] upwork response for '{search_term}' doesn't look like RSS — feed may require auth now")
        return []
    out = []
    try:
        root = ET.fromstring(resp.content)
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            out.append({
                "title": title,
                "company": "Upwork client",
                "location": "Remote",
                "url": link,
                "posted": pub,
                "source": "upwork",
                "kind": "client",
            })
    except ET.ParseError:
        print(f" [warn] upwork feed for '{search_term}' didn't parse as XML")
    return out
