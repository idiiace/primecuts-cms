// sync-articles.js (VERSION 2 - MORE ROBUST)
const https = require('https');
const fs = require('fs').promises;
const { parse } = require('csv-parse/sync'); // <-- IMPORT THE ROBUST PARSER

// Get Google Sheets URL from environment
const GOOGLE_SHEETS_URL = process.env.GOOGLE_SHEETS_URL;

async function syncArticles() {
    try {
        console.log('🔄 Starting article sync...');
        
        // Fetch CSV data from Google Sheets
        console.log('📊 Fetching from Google Sheets...');
        const csvData = await fetchFromUrl(GOOGLE_SHEETS_URL);
        console.log(`✅ Received ${csvData.length} characters of raw data.`);
        
        // Parse CSV to articles using the robust library
        const records = parse(csvData, {
            columns: true, // Use the first row as headers
            skip_empty_lines: true
        });
        
        console.log(`✅ Parsed ${records.length} total articles successfully!`);

        // Map records to our desired article format
        const articles = records.map((record, index) => ({
            id: String(index + 1),
            title: record['Title'] || '',
            status: record['Status'] || '',
            first_paragraph: record['First Paragraph'] || '',
            second_paragraph: record['Second Paragraph'] || '',
            content: `${record['First Paragraph'] || ''}\n\n${record['Second Paragraph'] || ''}`.trim(),
            keywords: record['Keywords'] || '',
            date: record['Date'] || new Date().toLocaleDateString(),
            notes: record['Notes'] || '',
            url: record['URL'] || '',
            author: 'Prime Cuts Team',
            featured_image: '',
            last_updated: new Date().toISOString()
        }));

        // Filter to published only
        const publishedArticles = articles.filter(a => 
            a.status.toLowerCase() === 'published' && a.title.trim()
        );
        console.log(`📋 Found ${publishedArticles.length} published articles.`);
        
        // Save JSON file
        await fs.writeFile('articles.json', JSON.stringify(publishedArticles, null, 2));
        console.log('💾 Saved articles.json');
        
        // Also create a human-readable index
        const indexHtml = generateIndexHtml(publishedArticles);
        await fs.writeFile('index.html', indexHtml);
        console.log('📄 Generated index.html');
        
        console.log('🎉 Sync completed successfully!');
        
    } catch (error) {
        console.error('❌ Sync failed:', error);
        process.exit(1);
    }
}

function fetchFromUrl(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
            res.on('error', reject);
        }).on('error', reject);
    });
}

function generateIndexHtml(articles) {
    // ... (This function remains exactly the same as before) ...
    return `<!DOCTYPE html><html><head><title>Prime Cuts Articles CDN</title><style>body{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;padding:20px;}.article{border:1px solid #ddd;padding:15px;margin:15px 0;border-radius:5px;}.title{font-size:18px;font-weight:bold;color:#333;margin-bottom:10px;}.meta{color:#666;font-size:14px;margin-bottom:10px;}.content{color:#444;line-height:1.5;}.json-link{background:#007bff;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;display:inline-block;margin:20px 0;}</style></head><body><h1>🥩 Prime Cuts Articles CDN</h1><p><strong>Last Updated:</strong> ${new Date().toLocaleString()}</p><p><strong>Published Articles:</strong> ${articles.length}</p><a href="articles.json" class="json-link">📄 Download articles.json</a><h2>Available Articles:</h2>${articles.map(article=>`<div class="article"><div class="title">📰 ${article.title}</div><div class="meta">👤 ${article.author} | 📅 ${article.date} | 🏷️ ${article.keywords}</div><div class="content">${article.content.substring(0,200)}${article.content.length>200?'...':''}</div></div>`).join('')}<hr><p><em>This CDN is updated automatically every 5 minutes from Google Sheets.</em></p></body></html>`;
}

// Run the sync
syncArticles();
