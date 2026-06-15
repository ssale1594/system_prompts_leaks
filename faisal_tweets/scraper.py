"""
جامع تغريدات فيصل السعدون (@Fisalahs) عن النرجسية
يشتغل بدون Twitter API Key — يستخدم twscrape
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

try:
    from twscrape import API, gather
    from twscrape.logger import set_log_level
except ImportError:
    print("❌ تحتاج تثبت twscrape أولاً:")
    print("   pip install twscrape fpdf2")
    exit(1)

# ──────────────────────────────────────────────
# إعدادات
# ──────────────────────────────────────────────
TARGET_USER = "Fisalahs"

KEYWORDS = [
    # عربي
    "نرجس", "نرجسي", "نرجسية", "نرجسيه",
    "تلاعب", "غازلايتنج", "gaslighting",
    "سمية", "سام", "شخصية",
    "ego", "انانية", "أنانية",
    "ضحية", "تحكم", "سيطرة",
    "احترام", "حدود", "حد",
    # انجليزي
    "narciss", "toxic", "manipulat",
    "empath", "boundary", "self-love",
]

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# دوال المساعدة
# ──────────────────────────────────────────────

def matches_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS)


def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)       # حذف روابط
    text = re.sub(r"\s+", " ", text).strip()  # تنظيف مسافات
    return text


def tweet_to_dict(tweet) -> dict:
    return {
        "id": tweet.id,
        "date": tweet.date.strftime("%Y-%m-%d %H:%M"),
        "text": tweet.rawContent,
        "clean_text": clean_text(tweet.rawContent),
        "likes": tweet.likeCount,
        "retweets": tweet.retweetCount,
        "replies": tweet.replyCount,
        "url": f"https://x.com/{TARGET_USER}/status/{tweet.id}",
    }


# ──────────────────────────────────────────────
# السحب من تويتر
# ──────────────────────────────────────────────

async def scrape(twitter_username: str, twitter_password: str):
    set_log_level("WARNING")
    api = API()

    print("🔐 تسجيل الدخول لتويتر...")
    await api.pool.add_account(twitter_username, twitter_password)
    await api.pool.login_all()

    print(f"🔍 جاري سحب تغريدات @{TARGET_USER}...")

    all_tweets = []
    filtered_tweets = []
    count = 0

    async for tweet in api.user_tweets_and_replies(
        await _get_user_id(api, TARGET_USER),
        limit=3000,
    ):
        count += 1
        t = tweet_to_dict(tweet)
        all_tweets.append(t)

        if matches_keywords(tweet.rawContent):
            filtered_tweets.append(t)
            print(f"  ✅ [{len(filtered_tweets)}] {t['date']} — {t['clean_text'][:80]}...")

    print(f"\n📊 إجمالي التغريدات المسحوبة: {count}")
    print(f"📌 التغريدات المتعلقة بالنرجسية: {len(filtered_tweets)}")

    return filtered_tweets


async def _get_user_id(api: "API", username: str) -> int:
    user = await api.user_by_login(username)
    if not user:
        raise ValueError(f"المستخدم @{username} غير موجود")
    return user.id


# ──────────────────────────────────────────────
# التصدير
# ──────────────────────────────────────────────

def export_json(tweets: list):
    path = OUTPUT_DIR / "tweets.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON محفوظ: {path}")


def export_markdown(tweets: list):
    path = OUTPUT_DIR / "كتيب_النرجسية.md"
    lines = [
        "# تغريدات فيصل السعدون — موضوع النرجسية",
        f"*جُمعت بتاريخ: {datetime.now().strftime('%Y-%m-%d')}*",
        f"*عدد التغريدات: {len(tweets)}*",
        "",
        "---",
        "",
    ]

    # ترتيب من الأقدم للأحدث
    for i, t in enumerate(sorted(tweets, key=lambda x: x["date"]), 1):
        lines += [
            f"## {i}. {t['date']}",
            "",
            t["clean_text"],
            "",
            f"> 👍 {t['likes']} | 🔁 {t['retweets']} | 💬 {t['replies']}",
            f"> [رابط التغريدة]({t['url']})",
            "",
            "---",
            "",
        ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📄 Markdown محفوظ: {path}")


def export_pdf(tweets: list):
    try:
        from fpdf import FPDF
    except ImportError:
        print("⚠️  fpdf2 غير مثبت — تخطي تصدير PDF (pip install fpdf2)")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # خط يدعم العربية — يحتاج ملف خط عربي
    # نستخدم Helvetica كبديل مؤقت
    pdf.set_font("Helvetica", size=12)
    pdf.set_right_margin(15)

    pdf.cell(0, 10, f"Faisal Al-Saadoun (@Fisalahs) - Narcissism Tweets", ln=True, align="C")
    pdf.cell(0, 8, f"Total: {len(tweets)} tweets | {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(5)

    for i, t in enumerate(sorted(tweets, key=lambda x: x["date"]), 1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, f"{i}. {t['date']} | Likes:{t['likes']} RT:{t['retweets']}", ln=True)
        pdf.set_font("Helvetica", size=9)
        # PDF لا يدعم العربية بدون خط مخصص — نحفظ النص كما هو
        safe_text = t["clean_text"].encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text)
        pdf.cell(0, 5, t["url"], ln=True)
        pdf.ln(3)

    path = OUTPUT_DIR / "tweets.pdf"
    pdf.output(str(path))
    print(f"📑 PDF محفوظ: {path}")
    print("⚠️  ملاحظة: PDF يحتاج خط عربي للعرض الصحيح — الـ Markdown أفضل للعربية")


# ──────────────────────────────────────────────
# نقطة البداية
# ──────────────────────────────────────────────

async def main():
    print("=" * 50)
    print("  جامع تغريدات النرجسية — @Fisalahs")
    print("=" * 50)
    print()

    tw_user = input("📧 أدخل إيميل/يوزرنيم حساب تويتر الخاص بك: ").strip()
    tw_pass = input("🔑 أدخل كلمة المرور: ").strip()

    tweets = await scrape(tw_user, tw_pass)

    if not tweets:
        print("⚠️  لم يتم العثور على تغريدات مطابقة.")
        return

    export_json(tweets)
    export_markdown(tweets)
    export_pdf(tweets)

    print()
    print("✅ اكتمل! الملفات موجودة في مجلد output/")


if __name__ == "__main__":
    asyncio.run(main())
