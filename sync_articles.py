# sync_articles.py (ULTRA-DEBUG VERSION)
import requests
import csv
import json
from io import StringIO
from datetime import datetime
import os

def fetch_articles_from_sheets(sheets_url):
    try:
        response = requests.get(sheets_url, timeout=15)
        response.raise_for_status()
        print("✅ Fetch successful.")
        # print(f"Raw Response Text:\n---\n{response.text[:500]}\n---") # Uncomment for extreme debugging
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        return None

def parse_csv_to_articles(csv_text):
    try:
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file)
        
        articles = []
        print("\n--- DEBUG: Inspecting each row from CSV ---")
        for i, row in enumerate(csv_reader):
            # --- START OF DEBUG BLOCK ---
            print(f"\n[Row {i+1}] Raw data read by parser: {row}")
            
            status_value = row.get("Status", "STATUS_COLUMN_NOT_FOUND").strip()
            
            print(f"[Row {i+1}] Inspecting Status column...")
            print(f"  - Value found: '{status_value}'")
            print(f"  - Length: {len(status_value)}")
            print(f"  - Lowercased: '{status_value.lower()}'")
            print(f"  - Does it equal 'published'? {status_value.lower() == 'published'}")
            # --- END OF DEBUG BLOCK ---

            article_data = {key.strip(): value.strip() for key, value in row.items()}
            
            if not article_data.get("Title"):
                print(f"[Row {i+1}] Skipping row because Title is missing.")
                continue

            article_data['id'] = str(i + 1)
            article_data['last_updated'] = datetime.now().isoformat()
            
            p1 = article_data.get('First Paragraph', '')
            p2 = article_data.get('Second Paragraph', '')
            article_data['content'] = f"{p1}\n\n{p2}".strip()

            articles.append(article_data)
        
        print("\n--- DEBUG: Finished inspecting all rows ---\n")
        return articles
        
    except Exception as e:
        print(f"❌ Error parsing CSV data: {e}")
        return None

def main():
    sheets_url = os.getenv('GOOGLE_SHEETS_URL')
    if not sheets_url:
        print("❌ FATAL: GOOGLE_SHEETS_URL secret not set.")
        exit(1)

    print("🔄 Starting sync process...")
    csv_data = fetch_articles_from_sheets(sheets_url)
    
    if not csv_data:
        exit(1)
        
    all_articles = parse_csv_to_articles(csv_data)

    if all_articles is None:
        exit(1)

    published_articles = [
        article for article in all_articles 
        if article.get("Status", "").strip().lower() == "published"
    ]
    
    with open("articles.json", 'w', encoding='utf-8') as f:
        json.dump(published_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Sync complete. Found and saved {len(published_articles)} published articles to articles.json.")

if __name__ == "__main__":
    main()
