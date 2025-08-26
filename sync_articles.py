# sync_articles.py (BULLETPROOF PRODUCTION VERSION v4)
import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os
import sys # Using sys.exit for clearer error handling

def fetch_articles_from_sheets(sheets_url):
    """Fetches raw CSV data from the Google Sheets public URL."""
    try:
        response = requests.get(sheets_url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        return None

def parse_csv_to_articles(csv_text):
    """Dynamically parses CSV text into a list of article dictionaries."""
    try:
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file)
        articles = []
        for i, row in enumerate(csv_reader):
            article_data = {key.strip() if key else f"unknown_column_{j}": value.strip() for j, (key, value) in enumerate(row.items())}
            
            header_keys = list(row.keys())
            title_key = header_keys[0] if header_keys else None
            title = article_data.get(title_key, "").strip()

            if not title:
                continue
            
            article_data["Title"] = title
            article_data['id'] = str(i + 1)
            article_data['last_updated'] = datetime.now().isoformat()
            
            p1 = article_data.get('First Paragraph', '')
            p2 = article_data.get('Second Paragraph', '')
            article_data['content'] = f"{p1}\n\n{p2}".strip()

            articles.append(article_data)
        return articles
    except Exception as e:
        print(f"❌ Error parsing CSV data: {e}")
        return None

def main():
    """Main function to run the sync process."""
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
    
    # --- THIS IS THE BULLETPROOF SANITY CHECK ---
    if not published_articles:
        print("\n⚠️ WARNING: Found 0 published articles.")
        print("To prevent accidentally wiping out the live data, the script will now exit WITHOUT updating articles.json.")
        print("If you intended to unpublish all articles, please delete the articles.json file from the repository manually.\n")
        # Exit with a success code so the workflow doesn't show a failure,
        # but without writing a new file.
        sys.exit(0) 
    # --- END OF SANITY CHECK ---
    
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found and saved {len(published_articles)} published articles to articles.json.")

if __name__ == "__main__":
    main()
