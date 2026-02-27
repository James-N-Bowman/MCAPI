import csv
import os

from helpersMailChimp import *
from helpersCtteesAPI import *
from helpersCSVMapping import *

FROM_NAME = "Automated Reports"
REPLY_TO = "committeecorridor@parliament.uk"
SUBJECT = "Automated Committee Update"

def main():
    cttee_id = input("Committee id?").strip()
    try:
        cttee_id = int(cttee_id)
    except ValueError as e:
        print(f"Error: must enter integer value: {e}")
        return
    
    cttees = fetch_committees_dict()

    if cttee_id in cttees:
        cttee_name = cttees[cttee_id]['name']
    else:
        print(f"Error: committee id not found.")
        return
    


if __name__ == "__main__":
    main()
