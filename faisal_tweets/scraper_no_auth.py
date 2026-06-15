"""
سحب تغريدات @Fisalahs بدون API ولا تسجيل دخول
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from pathlib import Path

TARGET_USER = "Fisalahs"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

KEYWORDS = [
    "نرجس", "نرجسي", "نرجسية", "نرجسيه",
    "تلاعب", "غازلايتنج", "gaslighting",
    "سمية", "سام", "شخصية",
    "ego", "انانية", "أنانية",
    "ضحية", "تحكم", "سيطرة",
    "حدود", "self-love", "narciss", "toxic",
]

NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.nl",
]

def matches_keywords(text):
    t = text.lower()
    return any(k.lower() in t for k in KEYWORDS)

def get_working_instance():
    for instance in NITTER_INSTANCES:
        try:
            r = requests.get(f"{instance}/{TARGET_USER}", timeout=8)
            if r.status_code == 200:
                print(f"✅ نستخدم: {instance}")
                return instance
        except:
            continue
    return None

def scrape_page(instance, cursor=None):
    url = f"{instance}/{TARGET_USER}"
    if cursor:
        url += f"?cursor={cursor}"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    tweets = []
    for item in soup.select(".timeline-item"):
        text_el = item.select_one(".tweet-content")
        date_el = item.select_one(".tweet-date a")
        stats = item.select(".icon-container")

        if not text_el:
            continue

        text = text_el.get_text(strip=True)
        date = date_el["title"] if date_el and date_el.has_attr("title") else ""
        link = date_el["href"] if date_el and date_el.has_attr("href") else ""

        stat_vals = [s.get_text(strip=True) for s in stats]

        tweets.append({
            "text": text,
            "date": date,
            "url": f"https://x.com{link}" if link else "",
            "stats": stat_vals,
        })

    # الصفحة التالية
    next_cursor = None
    next_btn = soup.select_one(".show-more a")
    if next_btn and "cursor=" in next_btn.get("href", ""):
        next_cursor = next_btn["href"].split("cursor=")[-1]

    return tweets, next_cursor

def main():
    print("=" * 45)
    print(f"  سحب تغريدات @{TARGET_USER} — بدون تسجيل دخول")
    print("=" * 45)

    instance = get_working_instance()
    if not instance:
        print("❌ كل Nitter instances محجوبة، جرب لاحقاً")
        return

    all_tweets = []
    filtered = []
    cursor = None
    page = 1

    while page <= 20:  # أقصى 20 صفحة
        print(f"📄 صفحة {page}...")
        try:
            tweets, cursor = scrape_page(instance, cursor)
        except Exception as e:
            print(f"⚠️  خطأ: {e}")
            break

        if not tweets:
            break

        for t in tweets:
            all_tweets.append(t)
            if matches_keywords(t["text"]):
                filtered.append(t)
                print(f"  ✅ {t['date'][:10]} — {t['text'][:70]}...")

        if not cursor:
            break

        page += 1
        time.sleep(1.5)

    print(f"\n📊 إجمالي التغريدات: {len(all_tweets)}")
    print(f"📌 متعلقة بالنرجسية: {len(filtered)}")

    if not filtered:
        print("⚠️  ما لقينا تغريدات — ممكن الـ instance محجوب")
        return

    # حفظ JSON
    with open(OUTPUT_DIR / "tweets.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    # حفظ Markdown
    md = f"# تغريدات فيصل السعدون — النرجسية\n"
    md += f"*{datetime.now().strftime('%Y-%m-%d')} | {len(filtered)} تغريدة*\n\n---\n\n"
    for i, t in enumerate(filtered, 1):
        md += f"## {i}. {t['date']}\n\n{t['text']}\n\n"
        if t['url']:
            md += f"> [رابط]({t['url']})\n"
        md += "\n---\n\n"

    with open(OUTPUT_DIR / "كتيب_النرجسية.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n✅ محفوظ في output/")
    print(f"   - tweets.json")
    print(f"   - كتيب_النرجسية.md")

if __name__ == "__main__":
    main()
