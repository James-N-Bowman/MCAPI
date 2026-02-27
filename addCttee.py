import logging
from helpersMailChimp import *
from helpersCtteesAPI import *
from helpersCSVMapping import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    cttee_id = input("Committee id?").strip()
    try:
        cttee_id = int(cttee_id)
    except ValueError as e:
        logger.debug(f"Error: must enter integer value: {e}")
        return
    
    cttees = fetch_committees_dict()

    if cttee_id in cttees:
        cttee_name = cttees[cttee_id]['name']
        logger.info(f"{cttee_name} found on committees API.")
    else:
        logger.warning(f"{cttee_name} found on committees API.")
        return
    
    interest = create_group_interest(cttee_name)
    interest_id = interest.get("id")
    create_campaign(interest_id, cttee_name)

if __name__ == "__main__":
    main()
