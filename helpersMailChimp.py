import logging
import os
import requests
import sys

API_KEY = os.environ['API_KEY']
DATA_CENTRE = os.environ['DATA_CENTRE']
AUDIENCE_ID = os.environ['AUDIENCE_ID']

GROUP_ID = "3da1d0b028"
BASE_URL = f"https://{DATA_CENTRE}.api.mailchimp.com/3.0"
AUTH = ("jbanystring", API_KEY)  # Mailchimp uses HTTP Basic Auth

TIMEOUT  = 30
PAGE_SIZE = 1000  # use large pages to minimize round-trips

DEFAULT_FROM_NAME = "Automated Reports"
DEFAULT_REPLY_TO = "committeecorridor@parliament.uk"
DEFAULT_SUBJECT = "Automated Committee Update"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# =========================
# GET, PUSH, PUT HELPERS
# =========================

def mailchimp_request(method, path, payload=None, params=None):
    url = BASE_URL + path
    logger.info("Fetching: %s", url)
    response = requests.request(
        method,
        url,
        auth=AUTH,
        json=payload,
        params=params or {},
        timeout=TIMEOUT,
    )
    if not response.ok:
        logger.debug(f"{method.upper()} {path} failed:")
        logger.debug(response.status_code, response.text)
        sys.exit(1)
    return response.json() if response.content else None

def mailchimp_get(path, params=None):
    return mailchimp_request("GET", path, params=params)

def mailchimp_post(path, payload=None):
    return mailchimp_request("POST", path, payload=payload)

def mailchimp_put(path, payload):
    return mailchimp_request("PUT", path, payload=payload)

# =========================
# FETCH HELPERS
# =========================

def fetch_all_tags(list_id):
    """GET /lists/{list_id}/tag-search with pagination (count/offset)."""
    tags = []
    offset = 0
    while True:
        data = mailchimp_get(f"/lists/{list_id}/tag-search", params={"count": PAGE_SIZE, "offset": offset})
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
        data = mailchimp_get("/campaigns", params={"count": PAGE_SIZE, "offset": offset})
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
        data = mailchimp_get(f"/lists/{list_id}/interest-categories", params={"count": PAGE_SIZE, "offset": offset})
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
        data = mailchimp_get(
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
        data = mailchimp_get(f"/lists/{list_id}/segments", params={"count": PAGE_SIZE, "offset": offset})
        batch = data.get("segments", [])
        segs.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return segs

# =========================
# LIST FOR ME HELPERS
# =========================

def list_all_tags():
    tags = fetch_all_tags(AUDIENCE_ID)
    print("# TAGS (id,name)")
    print("id,name")
    for t in tags:
        tag_id = t.get("id")
        name = (t.get("name") or "").replace('"', '""')
        print(f"{tag_id},\"{name}\"")
    print()


def list_all_campaigns():
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

def list_all_groups_and_interests():
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

def list_all_segments():
    segs = fetch_all_segments(AUDIENCE_ID)
    print("# SEGMENTS (id,name,type)")
    print("id,name,type")
    for s in segs:
        sid = s.get("id")
        name = (s.get("name") or "").replace('"', '""')
        stype = s.get("type") or ""  # 'saved', 'static', 'fuzzy', etc. depends on account
        print(f"{sid},\"{name}\",{stype}")

# =========================
# CREATION HELPERS
# =========================

def create_group_interest(name):
    """
    Adds an individual interest (option) inside a Group Category.
    
    :param audience_id: The ID of the audience/list
    :param group_id: The ID of the interest category (group) returned from create_group()
    :param name: The name of the interest option (e.g. "Football", "Basketball")
    """
    interest = mailchimp_post(
        f"/lists/{AUDIENCE_ID}/interest-categories/{GROUP_ID}/interests",
        {
            "name": name
        }
    )
    return interest

def create_campaign(interest_id, campaign_title, subject=DEFAULT_SUBJECT, from_name=DEFAULT_FROM_NAME, reply_to=DEFAULT_REPLY_TO):
    campaign = mailchimp_post(
        "/campaigns",
        {
            "type": "regular",
            "recipients": {
                "list_id": AUDIENCE_ID,
                "segment_opts": {
                    "match": "all",
                    "conditions": [
                        {
                            "condition_type": "Interests",
                            "field": f"interests-{GROUP_ID}",
                            "op": "interestcontains",
                            "value": [interest_id]  # integer ID of the tag
                        }
                    ]
                }
            },
            "settings": {
                "title": campaign_title,
                "subject_line": subject,
                "from_name": from_name,
                "reply_to": reply_to
            }
        }
    )
    return (campaign)

list_all_campaigns()