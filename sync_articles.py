# sync_articles.py (DEBUGGING VERSION)
import requests
import csv
import json
from io import StringIO
from datetime import datetime

# This is the only function we need for this test
def fetch_articles_from_sheets(sheets_url):
    try:       
        response = requests.get(sheets_url, timeout=10)
        response.raise_for_status()
        
        # --- THIS IS THE CRITICAL DEBUGGING STEP ---
        print("\n--- RESPONSE FROM GOOGLE (first 500 chars) ---")
        print(response.text[:500])
        print("--- END OF RESPONSE ---\n")
        # --- END OF DEBUGGING STEP ---

        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        # Also print the response text on error
        if e.response:
            print("\n--- ERROR RESPONSE FROM GOOGLE ---")
            print(e.response.text[:500])
            print("--- END OF ERROR RESPONSE ---\n")
        return None

# The rest of your proven code
def parse_csv_to_articles(csv_text):
    csv_reader = csv.DictReader(StringIO(csv_text))
    articles = []
    for row_num, row in enumerate(csv_reader, 1):
        cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
        if cleaned_row.get("Title"):
            articles.append({
                "id": str(row_num),
                "title": cleaned_row.get("Title", ""),
                "status": cleaned_row.get("Status", ""),
                "content": f"{cleaned_row.get('First Paragraph', '')}\n\n{cleaned_row.get('Second Paragraph', '')}".strip(),
                "keywords": cleaned_row.get("Keywords", ""),
                "date": cleaned_row.get("Date", ""),
            })
    return articles

def main():
    # We will get this URL from the GitHub Secret
    import os
    sheets_url = os.getenv('GOOGLE_SHEETS_URL')
    
    if not sheets_url:
        print("❌ FATAL ERROR: GOOGLE_SHEETS_URL secret is not set.")
        exit(1)

    print(f"🕵️ Attempting to fetch from URL: {sheets_url[:80]}...")
    
    csv_data = fetch_articles_from_sheets(sheets_url)
    
    if not csv_data:
        print("❌ Script finished with fetch error.")
        exit(1)
        
    articles = parse_csv_to_articles(csv_data)

    if articles is None:
        print("❌ Script finished with parse error.")
        exit(1)

    published_articles = [a for a in articles if a.get("status", "").lower() == "published"]
    
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found {len(published_articles)} published articles.")

if __name__ == "__main__":
    main()
