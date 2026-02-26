import json
import urllib.request
import urllib.parse

CTTEE_API_BASE_URL = "https://committees-api.parliament.uk/api/"

def fetch_committees_dict () -> dict:
    """
    Fetch committee data from the Parliament API.

    Returns:
        Dictionary, with cttee ids as keys, and cttee data as values
    """
    url = f"{CTTEE_API_BASE_URL}Committees?ShowOnWebsiteOnly=true"

    print(f"Fetching: {url}\n")

    cttee_items = []
    total_received = 0
    total_results = 1
    
    while total_received < total_results:
        url_with_skip = f"{url}&Skip={total_received}"
        print(url_with_skip)
        with urllib.request.urlopen(url_with_skip) as response:
            response_json = json.loads(response.read().decode())
            total_results = response_json['totalResults']
            latest_items = response_json['items']
            for item in latest_items:
                total_received += 1
                item_house = item['house']
                if item_house != 'Commons':
                    continue
                item_id = item.pop('id')
                cttee_items[item_id] = item
            print()
    
    return(cttee_items)

