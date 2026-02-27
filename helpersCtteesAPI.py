import json
import logging
import urllib.request
from urllib.error import URLError

CTTEE_API_BASE_URL = "https://committees-api.parliament.uk/api/"
PAGE_SIZE = 30

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def fetch_committees_dict() -> dict:
    """
    Fetch committee data from the Parliament API.

    Returns:
        Dictionary with committee IDs as keys and committee data as values,
        filtered to Commons committees only.
    """
    base_url = f"{CTTEE_API_BASE_URL}Committees?ShowOnWebsiteOnly=true&Take={PAGE_SIZE}"
    committees = {}
    skip = 0
    total_results = 1

    while skip < total_results:
        url = f"{base_url}&Skip={skip}"
        logger.debug("Fetching: %s", url)

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
        except URLError as e:
            raise RuntimeError(f"Failed to fetch committees from API: {e}") from e

        total_results = data["totalResults"]
        items = data["items"]

        if not items:
            logger.warning("Received empty page at skip=%d, stopping early.", skip)
            break  # Safeguard against empty pages causing infinite loops

        for item in items:
            skip += 1
            if item.get("house") == "Commons":
                item_id = item.pop("id")
                committees[item_id] = item

    logger.info("Fetched %d Commons committees (total results reported: %d).", len(committees), total_results)
    return committees

fetch_committees_dict()