const express = require("express");
const puppeteer = require("puppeteer");

const app = express();

/* =========================
   SONYLIV SCRAPER
========================= */
app.get("/sonyliv", async (req, res) => {
  try {
    const url = req.query.url;
    if (!url) return res.json({ error: "No URL provided" });

    const browser = await puppeteer.launch({
      headless: "new",
      args: ["--no-sandbox"]
    });

    const page = await browser.newPage();

    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    );

    await page.goto(url, { waitUntil: "networkidle2" });

    const html = await page.content();

    let title = (html.match(/<title>(.*?)<\/title>/i) || [])[1] || "Unknown";
    title = title.replace(" - SonyLIV", "").trim();

    let year = (html.match(/"releaseYear":"(\\d{4})"/) || [])[1] || "Unknown";

    let poster = (html.match(/"imageUrl":"(.*?)"/) || [])[1] || "";
    poster = poster.replace(/\\u002F/g, "/");

    let portrait = (html.match(/"posterURL":"(.*?)"/) || [])[1] || "";
    portrait = portrait.replace(/\\u002F/g, "/");

    await browser.close();

    res.json({ title, year, poster, portrait });

  } catch (e) {
    res.json({ error: e.toString() });
  }
});

/* ========================= */
app.listen(3000, () => console.log("Server running"));