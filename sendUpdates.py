import os

from helpersCSVMapping import *
from helpersMailChimp import *

MAPPING_FILE = 'mapping.csv'
HTMLS_DIR = 'HTMLs'

def send_html_to_campaign(campaign_id, html_content):
    """Updates campaign content and triggers the send action."""
    # 1. Update the Campaign Content
    content_path = f"/campaigns/{campaign_id}/content" 
    payload = {"html": html_content}
    mailchimp_put(content_path, payload)

    # 2. Send the Campaign
    send_path = f"/campaigns/{campaign_id}/actions/send"
    mailchimp_post(send_path)

    print(f"Campaign {campaign_id} sent successfully.")

def main():
    if not os.path.exists(MAPPING_CSV_FILEPATH):
        print(f"Error: {MAPPING_CSV_FILEPATH} not found.")
        return

    with open(MAPPING_CSV_FILEPATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        
        for row in reader:
            # Ensure row has enough columns (Cttee ID, Name, Campaign ID)
            if not row or len(row) < 3:
                continue
            
            cttee_id = row[0].strip()
            campaign_id = row[2].strip()
            
            # Check if an HTML file exists for this committee
            html_file_path = os.path.join(HTMLS_DIR, f"{cttee_id}.html")
            
            if os.path.exists(html_file_path):
                print(f"Found content for Committee {cttee_id}. Preparing to send...")
                
                with open(html_file_path, 'r', encoding='utf-8') as hf:
                    html_body = hf.read()
                
                try:
                    send_html_to_campaign(campaign_id, html_body)
                except Exception as e:
                    print(f"Error sending campaign {campaign_id} for committee {cttee_id}: {e}")
            else:
                # If no HTML file was created by the previous script (no new data), we skip
                print(f"No new updates for Committee {cttee_id} (No HTML file). Skipping.")

if __name__ == "__main__":
    main()
