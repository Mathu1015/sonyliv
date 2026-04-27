import os
import requests
from flask import Flask, request
from pyngrok import ngrok
import re
import cloudscraper

# =========================
# CONFIG (FROM ENV)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NGROK_TOKEN = os.getenv("NGROK_TOKEN")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

# =========================
# NGROK AUTH
# =========================
ngrok.set_auth_token(NGROK_TOKEN)

public_url = ngrok.connect(5000).public_url
print("🔥 PUBLIC URL:", public_url)
print(f"{API}/setWebhook?url={public_url}/telegram")

# =========================
# FETCH HTML
# =========================
def get_source(url):
    try:
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url, timeout=30)
        if r.status_code != 200:
            return None
        return r.text
    except:
        return None

def get_title(html):
    for pattern in [
        r'originalTitle\s*:\s*"(.*?)"',
        r'overlay_content_title\s*:\s*"(.*?)"',
        r'"name"\s*:\s*"(.*?)"'
    ]:
        t = re.search(pattern, html)
        if t:
            return t.group(1)
    return "SonyLIV Content"

def get_year(html):
    y = re.search(r'release_year\s*:\s*"?(\d{4})"?', html)
    return y.group(1) if y else "2025"

def parse(html):
    html = html.replace("\\/", "/")
    title = get_title(html)
    year = get_year(html)

    def find(p):
        m = re.search(p, html)
        return m.group(1) if m else "N/A"

    return (
        title,
        year,
        find(r'thumbnailURL\s*:\s*"(https?://[^"]+)"'),
        find(r'image_600x900_clean\s*:\s*"(https?://[^"]+)"'),
        find(r'landscape_thumb\s*:\s*"(https?://[^"]+)"'),
        find(r'portrait_thumb\s*:\s*"(https?://[^"]+)"')
    )

def send(text):
    requests.post(API + "/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": text
    })

@app.route("/telegram", methods=["POST"])
def telegram():
    data = request.json or {}
    msg = data.get("message", {})
    url = msg.get("text", "")

    if "sonyliv.com" not in url:
        return "OK"

    html = get_source(url)
    if not html:
        return "OK"

    title, year, p1, pt1, p2, pt2 = parse(html)

    send(f"🎬 {title} ({year})\n\nPoster:\n{p1}\nPortrait:\n{pt1}")
    send(f"🎬 {title} ({year})\n\nPoster:\n{p2}\nPortrait:\n{pt2}")

    return "OK"

app.run(host="0.0.0.0", port=5000)
