// scraperDemo.js
const express = require('express');
const puppeteer = require('puppeteer');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.send(`
    <h2>Power BI Scraper Demo</h2>
    <form method="POST" action="/scrape">
      <label>Enter Dashboard URL with Auth Token:</label><br/>
      <input type="text" name="url" style="width: 90%;" required /><br/><br/>
      <button type="submit">Scrape</button>
    </form>
  `);
});

app.post('/scrape', async (req, res) => {
  const { url } = req.body;

  if (!url || !url.startsWith('http')) {
    return res.send('Invalid URL');
  }

  const scrapedQueries = [];
  let browser;

  try {
    browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    // Intercept XHR 'query' responses
    page.on('response', async (response) => {
      const request = response.request();
      const reqUrl = request.url();

      if (request.resourceType() === 'xhr' && reqUrl.includes('query')) {
        try {
          const json = await response.json();
          scrapedQueries.push({
            url: reqUrl,
            status: response.status(),
            data: json,
          });
        } catch (err) {
          console.log(`Error reading JSON from ${reqUrl}`);
        }
      }
    });

    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.waitForTimeout(5000); // Wait for queries to fire
  } catch (err) {
    if (browser) {
      await browser.close();
    }
    return res.send(`❌ Error loading page: ${err.message}`);
  }

  await browser.close();

  if (scrapedQueries.length === 0) {
    return res.send("<p>No 'query' XHR requests found.</p>");
  }

  // Display results
  const html = `
    <h2>Found ${scrapedQueries.length} Query Requests</h2>
    ${scrapedQueries
      .map(
        (q, i) => `
      <details>
        <summary><strong>[${i + 1}]</strong> ${q.url}</summary>
        <pre>${JSON.stringify(q.data, null, 2)}</pre>
      </details>
    `
      )
      .join('')}
    <br/><a href="/">🔙 Back</a>
  `;

  res.send(html);
});

app.listen(PORT, () => {
  console.log(`🧪 Scraper running at http://localhost:${PORT}`);
});
