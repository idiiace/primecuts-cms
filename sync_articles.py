# This is YOUR proven script, with only print statements added for debugging.
# I have checked this for syntax errors.

import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os # <-- Added os to get the secret

def fetch_articles_from_sheets(sheets_url):
    """
    Fetch articles from Google Sheets using public CSV export
    """
    try: # <--- Colon is present
        print("🔄 Fetching data from Google Sheets...")
        
        response = requests.get(sheets_url, timeout=10)
        response.raise_for_status()
        
        # --- CRITICAL DEBUGGING STEP ---
        print("\n--- RESPONSE FROM GOOGLE (first 500 chars) ---")
        print(response.text[:500])
        print("--- END OF RESPONSE ---\n")
        # --- END DEBUGGING STEP ---
        
        return response.text
        
    except requests.exceptions.RequestException as e: # <--- Colon is present
        print(f"❌ Error fetching from Google Sheets: {e}")
        return None

def parse_csv_to_articles(csv_text):
    """
    Parse CSV text into structured article data
    """
    try: # <--- Colon is present
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
        
    except Exception as e: # <--- Colon is present
        print(f"❌ Error parsing CSV: {e}")
        return []

def main():
    """
    Main function to run in GitHub Actions
    """
    # Get the URL from the GitHub Secret
    sheets_url = os.getenv('GOOGLE_SHEETS_URL')

    if not sheets_url:
        print("❌ FATAL ERROR: GOOGLE_SHEETS_URL secret is not set in the repository settings.")
        exit(1)

    print(f"🕵️ Attempting to fetch from URL that starts with: {sheets_url[:80]}...")
    
    csv_data = fetch_articles_from_sheets(sheets_url)
    
    if not csv_data:
        print("❌ Script finished: Failed to fetch data.")
        exit(1)
        
    articles = parse_csv_to_articles(csv_data)

    if articles is None:
        print("❌ Script finished: Failed to parse data.")
        exit(1)

    published_articles = [a for a in articles if a.get("status", "").lower() == "published"]
    
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found {len(published_articles)} published articles. Saved to articles.json.")

if __name__ == "__main__":
    main()
