"""
سحب تغريدات @Fisalahs عن النرجسية باستخدام Playwright
شغّله على جهازك Windows
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

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
    "احترام", "ثقة", "نفس", "وعي",
]

def matches(text):
    t = text.lower()
    return any(k.lower() in t for k in KEYWORDS)

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # نفتح المتصفح عشان نشوف
        page = await browser.new_page()

        print(f"🌐 فتح صفحة @{TARGET_USER}...")
        await page.goto(f"https://x.com/{TARGET_USER}", wait_until="networkidle")
        await asyncio.sleep(3)

        filtered = []
        seen = set()
        scroll_count = 0
        max_scrolls = 100

        print("📜 بدء السحب...")

        while scroll_count < max_scrolls:
            # اجمع التغريدات الظاهرة
            tweets = await page.query_selector_all("article[data-testid='tweet']")

            for tweet in tweets:
                try:
                    text_el = await tweet.query_selector("[data-testid='tweetText']")
                    if not text_el:
                        continue
                    text = await text_el.inner_text()

                    # تجنب التكرار
                    if text in seen:
                        continue
                    seen.add(text)

                    # تاريخ التغريدة
                    time_el = await tweet.query_selector("time")
                    date = await time_el.get_attribute("datetime") if time_el else ""
                    date = date[:10] if date else ""

                    # رابط التغريدة
                    link_el = await tweet.query_selector("a[href*='/status/']")
                    href = await link_el.get_attribute("href") if link_el else ""
                    url = f"https://x.com{href}" if href else ""

                    if matches(text):
                        filtered.append({
                            "date": date,
                            "text": text,
                            "url": url,
                        })
                        print(f"  ✅ [{len(filtered)}] {date} — {text[:70]}...")

                except:
                    continue

            # اسكرول للأسفل
            await page.evaluate("window.scrollBy(0, 1500)")
            await asyncio.sleep(2)
            scroll_count += 1
            print(f"  📄 سكرول {scroll_count}/{max_scrolls} | تغريدات مرت: {len(seen)}", end="\r")

        await browser.close()
        return filtered

def save(tweets):
    if not tweets:
        print("⚠️  ما لقينا تغريدات مطابقة")
        return

    # JSON
    with open(OUTPUT_DIR / "tweets.json", "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

    # Markdown
    md = f"# تغريدات فيصل السعدون — النرجسية والشخصية\n\n"
    md += f"**الحساب:** @{TARGET_USER}  \n"
    md += f"**تاريخ الجمع:** {datetime.now().strftime('%Y-%m-%d')}  \n"
    md += f"**عدد التغريدات:** {len(tweets)}\n\n---\n\n"

    for i, t in enumerate(sorted(tweets, key=lambda x: x["date"]), 1):
        md += f"## {i}. {t['date']}\n\n"
        md += f"{t['text']}\n\n"
        if t["url"]:
            md += f"> [رابط التغريدة]({t['url']})\n"
        md += "\n---\n\n"

    with open(OUTPUT_DIR / "كتيب_النرجسية.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n✅ {len(tweets)} تغريدة محفوظة في مجلد output/")
    print(f"   📄 كتيب_النرجسية.md")
    print(f"   💾 tweets.json")

if __name__ == "__main__":
    print("=" * 45)
    print(f"  سحب تغريدات @{TARGET_USER} — Playwright")
    print("=" * 45)
    tweets = asyncio.run(scrape())
    save(tweets)
