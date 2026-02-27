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

def main(campaign_id):


    # 2. Set HTML content
    mailchimp_put(
        f"/campaigns/{campaign_id}/content",
        {
            "html": HTML_BODY
        }
    )

    print("Uploaded HTML content")

    # 3. Send campaign
    mailchimp_post(
        f"/campaigns/{campaign_id}/actions/send"
    )

    print("Campaign sent successfully")


if __name__ == "__main__":
    campaigns = ["923dd33776"]
    main(campaigns)
