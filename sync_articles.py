# sync_articles.py (FINAL & BULLETPROOF v4.0 - All Fixes + Sanity Check)
import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os
import sys

def fetch_articles_from_sheets(sheets_url):
    """Fetches raw CSV data and correctly handles text encoding."""
    try:
        response = requests.get(sheets_url, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding # Fixes special characters
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        return None

def parse_csv_to_articles(csv_text):
    """Dynamically parses CSV text, ensuring no data loss or duplication."""
    try:
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file)
        articles = []
        for i, row in enumerate(csv_reader):
            article_data = {key.strip(): value.strip() for key, value in row.items()}
            
            title = list(article_data.values())[0] if article_data else None
            if not title:
                continue
            
            article_data['id'] = str(i + 1)
            article_data['last_updated'] = datetime.now().isoformat()
            
            articles.append(article_data)
        return articles
    except Exception as e:
        print(f"❌ Error parsing CSV data: {e}")
        return None

def main():
    """Main function to run the sync process with all protections."""
    sheets_url = os.getenv('GOOGLE_SHEETS_URL')
    if not sheets_url:
        print("❌ FATAL: GOOGLE_SHEETS_URL secret not set.")
        sys.exit(1)

    print("🔄 Starting sync process...")
    csv_data = fetch_articles_from_sheets(sheets_url)
    if not csv_data:
        sys.exit(1)
        
    all_articles = parse_csv_to_articles(csv_data)
    if all_articles is None:
        sys.exit(1)

    published_articles = [
        article for article in all_articles 
        if article.get("Status", "").lower() == "published"
    ]
    
    # --- THIS IS THE CRITICAL SANITY CHECK YOU RIGHTFULLY POINTED OUT ---
    # It prevents the script from saving an empty file if no articles are found.
    if not published_articles:
        print("\n⚠️ SANITY CHECK FAILED: Found 0 published articles.")
        print("To prevent accidentally wiping out the live CDN data, the script will now exit WITHOUT updating articles.json.")
        print("If you truly intended to unpublish all articles, you must delete the articles.json file from the repository manually.\n")
        # Exit with a success code (0) so the workflow doesn't report a "failure",
        # but the key is that we exit *before* the file is written.
        sys.exit(0) 
    # --- END OF SANITY CHECK ---

    # This code will only be reached if the sanity check passes.
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found and saved {len(published_articles)} published articles to articles.json.")

if __name__ == "__main__":
    main()
