from helpersMailChimp import *

# Very small HTML body for proof-of-concept
HTML_BODY = """
<!DOCTYPE html>
<html>
  <body>
    <h1>Committee Update</h1>
    <p>This email was sent to the RSS tag.</p>
    <ul>
      <li>Item A</li>
      <li>Item B</li>
    </ul>
  </body>
</html>
"""

# =========================
# MAIN FLOW
# =========================

def send_html_to_campaign (campaign_id, html):
    
    content_path = f"/campaigns/{campaign_id}/content" 
    payload = {"html": html}
    mailchimp_put(content_path, payload)

    send_path = f"/campaigns/{campaign_id}/actions/send"
    mailchimp_post(send_path)

    print("Campaign sent successfully")

def main():
    send_html_to_campaign("a0ee568ff0",HTML_BODY)

if __name__ == "__main__":
    main()