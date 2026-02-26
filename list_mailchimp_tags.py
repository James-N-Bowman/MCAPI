#!/usr/bin/env python3
"""
List Mailchimp tags, campaigns, groups (interest categories + interests),
and segments for a given audience.

Outputs CSV-style sections to stdout.

Env vars:
  MAILCHIMP_API_KEY       - e.g. 'abcd1234-us21'
  MAILCHIMP_DATA_CENTRE    - e.g. 'us21'
  MAILCHIMP_AUDIENCE_ID   - e.g. 'a1b2c3d4e5'
"""

import os
import sys
import requests

API_KEY = os.environ['API_KEY']
DATA_CENTRE = os.environ['DATA_CENTRE']
AUDIENCE_ID = os.environ['AUDIENCE_ID']

if not API_KEY or not DATA_CENTRE or not AUDIENCE_ID:
    print("Please set MAILCHIMP_API_KEY, MAILCHIMP_DATA_CENTRE, MAILCHIMP_AUDIENCE_ID", file=sys.stderr)
    sys.exit(2)

BASE_URL = f"https://{DATA_CENTRE}.api.mailchimp.com/3.0"
AUTH     = ("anyOldString", API_KEY)
TIMEOUT  = 30
PAGE_SIZE = 1000  # use large pages to minimize round-trips

def _get(path, params=None):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, auth=AUTH, params=params or {}, timeout=TIMEOUT)
    if not r.ok:
        raise SystemExit(f"GET {path} failed: {r.status_code} {r.text}")
    return r.json()

def fetch_all_tags(list_id):
    """GET /lists/{list_id}/tag-search with pagination (count/offset)."""
    tags = []
    offset = 0
    while True:
        data = _get(f"/lists/{list_id}/tag-search", params={"count": PAGE_SIZE, "offset": offset})
        batch = data.get("tags", [])
        tags.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return tags

def fetch_all_campaigns():
    """GET /campaigns with pagination (count/offset)."""
    items = []
    offset = 0
    while True:
        data = _get("/campaigns", params={"count": PAGE_SIZE, "offset": offset})
        batch = data.get("campaigns", [])
        items.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return items

def fetch_interest_categories(list_id):
    """GET /lists/{list_id}/interest-categories (groups)."""
    cats = []
    offset = 0
    while True:
        data = _get(f"/lists/{list_id}/interest-categories", params={"count": PAGE_SIZE, "offset": offset})
        batch = data.get("categories", [])
        cats.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return cats

def fetch_interests(list_id, interest_category_id):
    """GET /lists/{list_id}/interest-categories/{category_id}/interests."""
    interests = []
    offset = 0
    while True:
        data = _get(
            f"/lists/{list_id}/interest-categories/{interest_category_id}/interests",
            params={"count": PAGE_SIZE, "offset": offset},
        )
        batch = data.get("interests", [])
        interests.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return interests

def fetch_all_segments(list_id):
    """GET /lists/{list_id}/segments with pagination."""
    segs = []
    offset = 0
    while True:
        data = _get(f"/lists/{list_id}/segments", params={"count": PAGE_SIZE, "offset": offset})
        batch = data.get("segments", [])
        segs.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return segs

def main():
    # 1) Tags
    tags = fetch_all_tags(AUDIENCE_ID)
    print("# TAGS (id,name)")
    print("id,name")
    for t in tags:
        tag_id = t.get("id")
        name = (t.get("name") or "").replace('"', '""')
        print(f"{tag_id},\"{name}\"")
    print()

    # 2) Campaigns
    campaigns = fetch_all_campaigns()
    print("# CAMPAIGNS (id,title,subject_line,status)")
    print("id,title,subject_line,status")
    for c in campaigns:
        cid = c.get("id")
        settings = c.get("settings", {}) or {}
        title = (settings.get("title") or "").replace('"', '""')
        subj  = (settings.get("subject_line") or "").replace('"', '""')
        status = c.get("status") or ""
        print(f"{cid},\"{title}\",\"{subj}\",{status}")
    print()

    # 3) Groups (Interest Categories + Interests)
    print("# GROUPS (category_id,category_title,interest_id,interest_name)")
    print("category_id,category_title,interest_id,interest_name")
    cats = fetch_interest_categories(AUDIENCE_ID)
    for cat in cats:
        cat_id = cat.get("id")
        cat_title = (cat.get("title") or "").replace('"', '""')
        interests = fetch_interests(AUDIENCE_ID, cat_id)
        if not interests:
            # still output category row with blanks for interests
            print(f"{cat_id},\"{cat_title}\",,")
        else:
            for i in interests:
                iid = i.get("id")
                iname = (i.get("name") or "").replace('"', '""')
                print(f"{cat_id},\"{cat_title}\",{iid},\"{iname}\"")
    print()

    # 4) Segments
    segs = fetch_all_segments(AUDIENCE_ID)
    print("# SEGMENTS (id,name,type)")
    print("id,name,type")
    for s in segs:
        sid = s.get("id")
        name = (s.get("name") or "").replace('"', '""')
        stype = s.get("type") or ""  # 'saved', 'static', 'fuzzy', etc. depends on account
        print(f"{sid},\"{name}\",{stype}")

if __name__ == "__main__":
    main()