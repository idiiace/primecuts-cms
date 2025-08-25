# sync_articles.py (FINAL, DYNAMIC VERSION - NO DATA LOSS)
import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os

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
    """
    Dynamically parses CSV text into a list of article dictionaries.
    It captures ALL columns from the sheet, ensuring no data loss.
    """
    try:
        # Use StringIO to treat the string as a file
        csv_file = StringIO(csv_text)
        
        # Use DictReader to automatically use the first row as headers
        csv_reader = csv.DictReader(csv_file)
        
        articles = []
        for i, row in enumerate(csv_reader):
            # Create a dictionary for the article, cleaning up keys and values
            article_data = {key.strip(): value.strip() for key, value in row.items()}
            
            # Skip rows that don't have a title
            if not article_data.get("Title"):
                continue

            # --- STANDARDIZE CORE FIELDS & ADD METADATA ---
            # Add our own metadata while preserving all original data
            article_data['id'] = str(i + 1)
            article_data['last_updated'] = datetime.now().isoformat()
            
            # Create a combined 'content' field for convenience in Unbounce,
            # but KEEP the original paragraph fields.
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
        exit(1)

    print("🔄 Starting sync process...")
    csv_data = fetch_articles_from_sheets(sheets_url)
    
    if not csv_data:
        exit(1) # Exit with an error
        
    all_articles = parse_csv_to_articles(csv_data)

    if all_articles is None:
        exit(1) # Exit with an error

    # Filter for published articles AFTER all data has been parsed
    published_articles = [
        article for article in all_articles 
        if article.get("Status", "").lower() == "published"
    ]
    
    # Save the complete, rich JSON file
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found and saved {len(published_articles)} published articles to articles.json.")

if __name__ == "__main__":
    main()
