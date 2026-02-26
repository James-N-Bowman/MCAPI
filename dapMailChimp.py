import os
import requests
import sys

API_KEY = os.environ['API_KEY']
DATA_CENTRE = os.environ['DATA_CENTRE']
AUDIENCE_ID = os.environ['AUDIENCE_ID']
GROUP_ID = "3da1d0b028"
BASE_URL = f"https://{DATA_CENTRE}.api.mailchimp.com/3.0"
AUTH = ("jbanystring", API_KEY)  # Mailchimp uses HTTP Basic Auth

def mailchimp_post(path, payload):
    url = BASE_URL + path
    response = requests.post(url, auth=AUTH, json=payload)
    if not response.ok:
        print(f"POST {path} failed:")
        print(response.status_code, response.text)
        sys.exit(1)
    return response.json()

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