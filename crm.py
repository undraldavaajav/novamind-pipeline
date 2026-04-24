import os, json, datetime, requests
from dotenv import load_dotenv

load_dotenv()
HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com"
HEADERS = {"Authorization": f"Bearer {HUBSPOT_API_KEY}", "Content-Type": "application/json"}

MOCK_CONTACTS = [
    {"email": "sarah@brightcreative.com", "firstname": "Sarah", "lastname": "Chen", "persona": "agency_owner", "company": "Bright Creative Agency"},
    {"email": "marcus@brightcreative.com", "firstname": "Marcus", "lastname": "Liu", "persona": "agency_owner", "company": "Bright Creative Agency"},
    {"email": "priya@freelance.com", "firstname": "Priya", "lastname": "Patel", "persona": "freelance_designer", "company": "Self-employed"},
    {"email": "jake@freelance.com", "firstname": "Jake", "lastname": "Torres", "persona": "freelance_designer", "company": "Self-employed"},
    {"email": "nina@techcorp.com", "firstname": "Nina", "lastname": "Kovacs", "persona": "marketing_manager", "company": "TechCorp"},
    {"email": "david@techcorp.com", "firstname": "David", "lastname": "Park", "persona": "marketing_manager", "company": "TechCorp"},
]

def upsert_contact(contact):
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    payload = {
        "properties": {
            "email": contact["email"],
            "firstname": contact["firstname"],
            "lastname": contact["lastname"],
            "company": contact["company"],
            "hs_lead_status": "NEW",
            "jobtitle": contact["persona"].replace("_", " ").title()
        }
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code in [200, 201]:
        contact_id = r.json()["id"]
        print(f"    Created: {contact['email']} (id: {contact_id})")
        return contact_id
    elif r.status_code == 409:
        existing_id = r.json().get("message", "").split("ID: ")[-1].strip()
        print(f"    Already exists: {contact['email']}")
        return existing_id
    else:
        print(f"    Warning: {contact['email']} - {r.status_code} {r.text[:80]}")
        return None

def log_campaign(campaign_id, blog_title, newsletters):
    import pathlib
    pathlib.Path("data").mkdir(exist_ok=True)
    log = {
        "campaign_id": campaign_id,
        "blog_title": blog_title,
        "send_date": datetime.datetime.utcnow().isoformat(),
        "sends": []
    }
    for contact in MOCK_CONTACTS:
        newsletter = newsletters.get(contact["persona"])
        if newsletter:
            log["sends"].append({
                "email": contact["email"],
                "persona": contact["persona"],
                "subject_line": newsletter.get("subject_line", ""),
                "send_status": "simulated_sent",
                "send_date": datetime.datetime.utcnow().isoformat()
            })
    fname = f"data/{campaign_id}-campaign-log.json"
    with open(fname, "w") as f:
        json.dump(log, f, indent=2)
    print(f"    Campaign log saved: {fname}")
    return log

def run(blog, newsletters, campaign_id):
    print("\n[Stage 2] CRM Integration")
    print("  Upserting contacts to HubSpot...")
    contact_ids = []
    for contact in MOCK_CONTACTS:
        cid = upsert_contact(contact)
        if cid:
            contact_ids.append(cid)
    print(f"  Processed {len(contact_ids)} contacts")
    print("  Logging campaign...")
    log = log_campaign(campaign_id, blog["title"], newsletters)
    print(f"  Simulated {len(log['sends'])} newsletter sends")
    return log
