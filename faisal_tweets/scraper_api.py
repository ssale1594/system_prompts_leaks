"""
سحب تغريدات @Fisalahs عن النرجسية عبر Twitter API v2
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALgO3gEAAAAAlf5wLn%2BZumESbrI7HOOzPJgpru0%3DqgtuGwjYWdjAG32VcYlNyKNjoC7oYHSiZMP8weKLGpL2DXToPY"
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
    "احترام", "ثقة", "نفس",
]

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

def get_user_id():
    url = f"https://api.twitter.com/2/users/by/username/{TARGET_USER}"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    if "data" not in data:
        raise Exception(f"خطأ: {data}")
    return data["data"]["id"]

def get_tweets(user_id, pagination_token=None):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": 100,
        "tweet.fields": "created_at,public_metrics,text",
        "exclude": "retweets",
    }
    if pagination_token:
        params["pagination_token"] = pagination_token
    r = requests.get(url, headers=HEADERS, params=params)
    return r.json()

def matches(text):
    t = text.lower()
    return any(k.lower() in t for k in KEYWORDS)

def main():
    print("=" * 45)
    print(f"  سحب تغريدات @{TARGET_USER} — Twitter API v2")
    print("=" * 45)

    print("🔍 جاري البحث عن معرف المستخدم...")
    user_id = get_user_id()
    print(f"✅ معرف @{TARGET_USER}: {user_id}")

    all_tweets = []
    filtered = []
    token = None
    page = 1

    while True:
        print(f"📄 صفحة {page}...")
        data = get_tweets(user_id, token)

        if "data" not in data:
            print(f"⚠️  {data}")
            break

        for t in data["data"]:
            all_tweets.append(t)
            if matches(t["text"]):
                filtered.append(t)
                print(f"  ✅ {t['created_at'][:10]} — {t['text'][:70]}...")

        token = data.get("meta", {}).get("next_token")
        if not token:
            break

        page += 1
        time.sleep(1)

    print(f"\n📊 إجمالي التغريدات: {len(all_tweets)}")
    print(f"📌 متعلقة بالنرجسية: {len(filtered)}")

    if not filtered:
        print("⚠️  ما لقينا تغريدات مطابقة")
        return

    # JSON
    with open(OUTPUT_DIR / "tweets.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    # Markdown كتيب
    md = f"# تغريدات فيصل السعدون — النرجسية والشخصية\n\n"
    md += f"**الحساب:** @{TARGET_USER}  \n"
    md += f"**تاريخ الجمع:** {datetime.now().strftime('%Y-%m-%d')}  \n"
    md += f"**عدد التغريدات:** {len(filtered)}\n\n---\n\n"

    for i, t in enumerate(sorted(filtered, key=lambda x: x["created_at"]), 1):
        date = t["created_at"][:10]
        text = t["text"]
        m = t.get("public_metrics", {})
        likes = m.get("like_count", 0)
        rt = m.get("retweet_count", 0)
        replies = m.get("reply_count", 0)
        url = f"https://x.com/{TARGET_USER}/status/{t['id']}"

        md += f"## {i}. {date}\n\n"
        md += f"{text}\n\n"
        md += f"> 👍 {likes} &nbsp;|&nbsp; 🔁 {rt} &nbsp;|&nbsp; 💬 {replies}  \n"
        md += f"> [رابط التغريدة]({url})\n\n---\n\n"

    with open(OUTPUT_DIR / "كتيب_النرجسية.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n✅ الملفات جاهزة في مجلد output/")
    print(f"   📄 كتيب_النرجسية.md")
    print(f"   💾 tweets.json")

if __name__ == "__main__":
    main()
