import csv
import os

from dapMailChimp import *
from ctteesApi import *

FROM_NAME = "Automated Reports"
REPLY_TO = "committeecorridor@parliament.uk"
SUBJECT = "Automated Committee Update"

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

def create_campaign(interest_id):
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
                            "condition_type": "StaticSegment",
                            "field": "static_segment",
                            "op": "static_is",
                            "value": interest_id  # integer ID of the tag
                        }
                    ]
                }
            },
            "settings": {
                "title": "Brand new campaign 4",
                "subject_line": SUBJECT,
                "from_name": FROM_NAME,
                "reply_to": REPLY_TO
            }
        }
    )
    return (campaign)

def update_mapping_CSV(filepath: str, cttee_id: int, campaign_id: str, interest_id: str) -> None:
    """
    Writes a new row (cttee_id, campaign_id, interest_id) to a CSV file.

    - If filepath is None, reports the problem and returns.
    - If the file exists but cannot be opened for writing, reports the problem and returns.
    - If the file does not exist, creates it with a header row then writes the new row.
    - Before writing to an existing file, checks that none of the three values already
      exist in their respective columns; if a duplicate is found, reports and returns.
    - Otherwise, appends the new row.

    Args:
        filepath    : Path to the CSV file (must end in .csv).
        cttee_id    : Committee ID (integer).
        campaign_id : Campaign ID (string).
        interest_id : Interest ID (string).
    """

    # --- 1. Validate filepath ---
    if filepath is None:
        print("Error: filepath is null. Please provide a valid file path.")
        return

    if not filepath.lower().endswith(".csv"):
        print(f"Error: filepath '{filepath}' does not point to a CSV file.")
        return

    file_exists = os.path.exists(filepath)

    # --- 2. Handle non-existent file: create with header then write row ---
    if not file_exists:
        try:
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["cttee_id", "campaign_id", "interest_id"])
                writer.writerow([cttee_id, campaign_id, interest_id])
            print(f"Created '{filepath}' and wrote new row successfully.")
        except OSError as e:
            print(f"Error: Could not create file at '{filepath}': {e}")
        return

    # --- 3. File exists: check it can be opened for writing ---
    try:
        with open(filepath, "a", newline="") as f:
            pass  # just test write access
    except OSError as e:
        print(f"Error: File '{filepath}' cannot be opened for writing: {e}")
        return

    # --- 4. Parse existing CSV and check for duplicates ---
    try:
        with open(filepath, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except OSError as e:
        print(f"Error: Could not read file '{filepath}': {e}")
        return

    # Skip header row when checking for duplicates
    data_rows = rows[1:] if len(rows) > 0 else []

    for row in data_rows:
        if len(row) < 3:
            continue  # skip malformed rows

        # Column 1: cttee_id (stored as int)
        try:
            if int(row[0]) == cttee_id:
                print(f"Error: cttee_id '{cttee_id}' already exists in the file.")
                return
        except ValueError:
            pass  # non-integer in column; skip comparison

        # Column 2: campaign_id
        if row[1] == campaign_id:
            print(f"Error: campaign_id '{campaign_id}' already exists in the file.")
            return

        # Column 3: interest_id
        if row[2] == interest_id:
            print(f"Error: interest_id '{interest_id}' already exists in the file.")
            return

    # --- 5. All checks passed: append new row ---
    try:
        with open(filepath, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([cttee_id, campaign_id, interest_id])
        print(f"Row written successfully to '{filepath}'.")
    except OSError as e:
        print(f"Error: Could not write to file '{filepath}': {e}")

def main():
    cttee_id = input("Committee id?").strip()
    try:
        cttee_id = int(cttee_id)
    except ValueError as e:
        print(f"Error: must enter integer value: {e}")
        return
    
    cttee = fetch_committees([cttee_id])
    if cttee == None:
        print(f"Error: couldn't get information from cttees API: {e}")
        return
    else:
        print(f"Cttee name {cttee['name']}")

if __name__ == "__main__":
    main()
