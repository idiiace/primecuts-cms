const https = require('https');
const fs = require('fs').promises;

// Get Google Sheets URL from environment
const GOOGLE_SHEETS_URL = process.env.GOOGLE_SHEETS_URL;

async function syncArticles() {
    try {
        console.log('🔄 Starting article sync...');
        
        // Fetch CSV data from Google Sheets
        console.log('📊 Fetching from Google Sheets...');
        const csvData = await fetchFromUrl(GOOGLE_SHEETS_URL);
        console.log(`✅ Received ${csvData.length} characters`);
        
        // Parse CSV to articles
        const articles = parseCSVToArticles(csvData);
        console.log(`✅ Parsed ${articles.length} total articles`);
        
        // Filter to published only
        const publishedArticles = articles.filter(a => 
            a.status.toLowerCase() === 'published' && a.title.trim()
        );
        console.log(`📋 Found ${publishedArticles.length} published articles`);
        
        // Save JSON file (GitHub Actions will commit it)
        await fs.writeFile('articles.json', JSON.stringify(publishedArticles, null, 2));
        console.log('💾 Saved articles.json');
        
        // Also create a human-readable index
        const indexHtml = generateIndexHtml(publishedArticles);
        await fs.writeFile('index.html', indexHtml);
        console.log('📄 Generated index.html');
        
        console.log('🎉 Sync completed successfully!');
        console.log(`📡 CDN URL: https://${process.env.GITHUB_REPOSITORY_OWNER}.github.io/${process.env.GITHUB_REPOSITORY_NAME}/articles.json`);
        
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

function parseCSVToArticles(csvText) {
    const lines = csvText.split('\n');
    const articles = [];
    
    // Skip header row
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
            const values = parseCSVLine(line);
            if (values.length >= 2 && values[0]) { // At least title
                articles.push({
                    id: String(i), // Row number as ID
                    title: values[0] || '',
                    status: values[1] || '',
                    first_paragraph: values[2] || '',
                    second_paragraph: values[3] || '',
                    content: `${values[2] || ''}\n\n${values[3] || ''}`.trim(),
                    keywords: values[4] || '',
                    date: values[5] || new Date().toLocaleDateString(),
                    notes: values[6] || '',
                    url: values[7] || '',
                    author: 'Prime Cuts Team',
                    featured_image: '',
                    last_updated: new Date().toISOString()
                });
            }
        }
    }
    
    return articles;
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

function generateIndexHtml(articles) {
    return `<!DOCTYPE html>
<html>
<head>
    <title>Prime Cuts Articles CDN</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        .article { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .meta { color: #666; font-size: 14px; margin-bottom: 10px; }
        .content { color: #444; line-height: 1.5; }
        .json-link { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🥩 Prime Cuts Articles CDN</h1>
    <p><strong>Last Updated:</strong> ${new Date().toLocaleString()}</p>
    <p><strong>Published Articles:</strong> ${articles.length}</p>
    
    <a href="articles.json" class="json-link">📄 Download articles.json</a>
    
    <h2>Available Articles:</h2>
    
    ${articles.map(article => `
        <div class="article">
            <div class="title">📰 ${article.title}</div>
            <div class="meta">
                👤 ${article.author} | 📅 ${article.date} | 🏷️ ${article.keywords}
            </div>
            <div class="content">${article.content.substring(0, 200)}${article.content.length > 200 ? '...' : ''}</div>
        </div>
    `).join('')}
    
    <hr>
    <p><em>This CDN is updated automatically every 5 minutes from Google Sheets.</em></p>
</body>
</html>`;
}

// Run the sync
syncArticles();
