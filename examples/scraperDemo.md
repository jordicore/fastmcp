# Power BI Scraper Demo

This example shows how to use Express and Puppeteer to capture XHR requests that contain `query` in their URL. The captured JSON payloads are rendered in the browser so you can inspect responses coming from an authenticated dashboard URL.

## Prerequisites

- Node.js 18+
- npm

## Installation

```bash
cd examples
npm install express puppeteer body-parser
```

## Usage

```bash
node scraperDemo.js
```

Open <http://localhost:3000>, paste your dashboard URL (including the auth token), and submit the form. Any `xhr` requests whose URLs contain `query` will be captured and displayed.

> **Note:** Authentication is handled through the token embedded in the URL—no additional login flow is required.
