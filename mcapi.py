import os
import json
import sys

import requests

# =========================
# CONFIGURATION
# =========================

API_KEY = os.environ['API_KEY']
DATA_CENTRE = os.environ['DATA_CENTRE']
AUDIENCE_ID = os.environ['AUDIENCE_ID']

FROM_NAME = "Automated Reports"
REPLY_TO = "noreply@example.com"
SUBJECT = "Automated Committee Update"

# Very small HTML body for proof-of-concept
HTML_BODY = """
<!DOCTYPE html>
<html>
  <body>
    <h1>Committee Update</h1>
    <p>This email was sent automatically from a GitHub Action.</p>
    <ul>
      <li>Item A</li>
      <li>Item B</li>
    </ul>
  </body>
</html>
"""

BASE_URL = f"https://{DATA_CENTRE}.api.mailchimp.com/3.0"

AUTH = ("anystring", API_KEY)  # Mailchimp uses HTTP Basic Auth


# =========================
# HELPER FUNCTIONS
# =========================

def mailchimp_post(path, payload):
    url = BASE_URL + path
    response = requests.post(url, auth=AUTH, json=payload)
    if not response.ok:
        print(f"POST {path} failed:")
        print(response.status_code, response.text)
        sys.exit(1)
    return response.json()


def mailchimp_put(path, payload):
    url = BASE_URL + path
    response = requests.put(url, auth=AUTH, json=payload)
    if not response.ok:
        print(f"PUT {path} failed:")
        print(response.status_code, response.text)
        sys.exit(1)
    return response.json()


def mailchimp_post_no_body(path):
    url = BASE_URL + path
    response = requests.post(url, auth=AUTH)
    if not response.ok:
        print(f"POST {path} failed:")
        print(response.status_code, response.text)
        sys.exit(1)


# =========================
# MAIN FLOW
# =========================

def main():
    # 1. Create campaign
    campaign = mailchimp_post(
        "/campaigns",
        {
            "type": "regular",
            "recipients": {
                "list_id": AUDIENCE_ID
            },
            "settings": {
                "subject_line": SUBJECT,
                "from_name": FROM_NAME,
                "reply_to": REPLY_TO
            }
        }
    )

    campaign_id = campaign["id"]
    print(f"Created campaign: {campaign_id}")

    # 2. Set HTML content
    mailchimp_put(
        f"/campaigns/{campaign_id}/content",
        {
            "html": HTML_BODY
        }
    )

    print("Uploaded HTML content")

    # 3. Send campaign
    mailchimp_post_no_body(
        f"/campaigns/{campaign_id}/actions/send"
    )

    print("Campaign sent successfully")


if __name__ == "__main__":
    main()
