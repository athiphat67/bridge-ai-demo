const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  // We'll just intercept the network request to force a 500 error
  await page.setRequestInterception(true);
  page.on('request', request => {
    if (request.url().includes('/api/analyze') && request.method() === 'POST') {
      request.respond({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Simulated backend crash' })
      });
    } else {
      request.continue();
    }
  });

  await page.goto('http://localhost:5173');
  await page.waitForSelector('text/Analysis Settings');
  
  // Switch to real mode
  const toggle = await page.$('button[role="switch"]');
  await toggle.click();
  
  // Wait for file input
  const fileInput = await page.$('input[type="file"]');
  // Upload dummy file
  const fs = require('fs');
  fs.writeFileSync('dummy.png', 'fake image data');
  await fileInput.uploadFile('dummy.png');

  // Click analyze
  const analyzeBtn = await page.$('.btn-analyze');
  await analyzeBtn.click();
  
  // Wait for error banner
  try {
    await page.waitForSelector('text/Analysis Failed', { timeout: 5000 });
    const text = await page.evaluate(() => document.body.innerText);
    if (text.includes('Simulated backend crash')) {
      console.log('SUCCESS: Error banner is showing the correct message.');
    } else {
      console.log('FAILURE: Error banner not showing message. Text:', text.substring(0, 500));
    }
  } catch(e) {
    console.log('FAILURE: Error banner did not appear.');
  }

  await browser.close();
})();
