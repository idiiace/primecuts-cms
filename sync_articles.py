# sync_articles.py (FINAL PRODUCTION VERSION v3.1 - Cleaned up Content Fields)
import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os
import sys

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
            article_data = {key.strip(): value.strip() for key, value in row.items()}
            
            # Use the first column as the title, robustly
            title = list(article_data.values())[0]
            if not title:
                continue
            
            # Add our own metadata
            article_data['id'] = str(i + 1)
            article_data['last_updated'] = datetime.now().isoformat()
            
            articles.append(article_data)
        return articles
    except Exception as e:
        print(f"❌ Error parsing CSV data: {e}")
        return None

def main():
    """Main function to run the sync process."""
    sheets_url = os.getenv('GOOGLE_SHEET_URL') # Matching the new secret name
    if not sheets_url:
        print("❌ FATAL: GOOGLE_SHEET_URL secret not set.")
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
    
    # Bulletproof Sanity Check
    if not published_articles:
        print("\n⚠️ WARNING: Found 0 published articles. Exiting without updating JSON.\n")
        sys.exit(0) 

    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found and saved {len(published_articles)} published articles to articles.json.")

if __name__ == "__main__":
    main()
